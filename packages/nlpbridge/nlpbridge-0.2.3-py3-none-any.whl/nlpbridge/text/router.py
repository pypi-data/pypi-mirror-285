import logging
import random
from typing import List, Literal, Optional, TypeVar, TypedDict, Callable, Tuple, Any, Dict

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.base import RunnableLike, Runnable
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph

from nlpbridge import ChatAgent

from nlpbridge.persistent.mysql import CRUDNode, CRUDEdge, CRUDTemplate, CRUDRouter
from nlpbridge.persistent.mysql import MySqlDBClient
from nlpbridge.persistent.mysql_dataschema import Node as NodeModel
from nlpbridge.text.tools import tool_list

memory = MemorySaver()

Input = TypeVar("Input", contravariant=True)
Output = TypeVar("Output", covariant=True)
logger = logging.getLogger(__name__)



class BaseNode:
    id: int
    name: str
    description: str
    goal: str  # node goal
    chat_limit: int
    system_template_ids: List[int]
    user_template_ids: List[int]
    tool_names: List[str]


class Template:
    id: int
    name: str
    type: Literal["user", "sys"] = "user"
    content: str


class Edge:
    id: int
    start_id: int
    end_id: int
    goal: str
    weight: float


class Node(Callable[[dict], TypedDict]):
    def __init__(self, id, name, description, goal, chat_limit, system_template_ids, user_template_ids,
                 system_templates,
                 user_templates, tool_names,
                 in_edges,
                 out_edges,
                 llm,
                 chat_id, **kwargs):
        self.id = id
        self.name = name
        self.description = description
        self.goal = goal
        self.chat_limit = chat_limit
        self.system_templates_ids = system_template_ids
        self.user_templates_ids = user_template_ids
        self.tool_names = tool_names
        self.system_templates = system_templates
        self.user_templates = user_templates
        self.in_edges = in_edges
        self.out_edges = out_edges
        self.llm = llm
        self.chat_id = chat_id

    system_templates: List[Template]
    user_templates: List[Template]
    chain: Optional[RunnableLike]
    in_edges: List[Edge]
    out_edges: List[Edge]

    def rand_prompt(self):
        ## init new prompt with random sys_prompt and user_prompt
        sys_prompt = random.choice(self.system_templates)
        user_prompt = random.choice(self.user_templates)
        return ChatPromptTemplate.from_messages(
            [
                ("system", sys_prompt.content + user_prompt.content),
                MessagesPlaceholder(variable_name="chat_history"),
                # MessagesPlaceholder(variable_name="intermediate_steps"),
                ("human", "User qeustion: {input}"),
            ]
        )

    def _init_agent(self):
        prompt = self.rand_prompt()
        self.agent = ChatAgent(None, self.chat_id, self.llm, self.tool_names, prompt, True)

    def __call__(self, state: dict) -> Output:
        self._init_agent()
        self.chat_limit -= 1
        # question = input("[Question]: ")
        question = "你好呀，你是谁？"
        response = self.agent.run(question)
        print(f"[current agent generate]: {response}")
        print(f"[node state]:\n{state}")
        return {"context": {"input": question, "response": response.content}}

    @classmethod
    def init_with_params(cls, id, name, description, goal, chat_limit, system_template_ids, user_template_ids,
                         system_templates,
                         user_templates, tool_names,
                         in_edges,
                         out_edges,
                         llm,
                         chat_id, **kwargs):
        return cls(id, name, description, goal, chat_limit, system_template_ids, user_template_ids,
                   system_templates,
                   user_templates, tool_names,
                   in_edges,
                   out_edges,
                   llm,
                   chat_id, **kwargs)


class Router:
    id: int
    name: str
    node_ids: List[str]
    edge_ids: List[str]


class NodeManager:

    @staticmethod
    def get_nodes(node_ids: List[int]) -> List[NodeModel]:
        from nlpbridge.config import CONFIG
        session = MySqlDBClient(CONFIG).get_session()
        return CRUDNode(session).get_by_ids(list_ids=node_ids)


class EdgeManager:
    @staticmethod
    def get_edges(edge_ids: List[int]) -> List[Edge]:
        from nlpbridge.config import CONFIG
        session = MySqlDBClient(CONFIG).get_session()
        return CRUDEdge(session).get_by_ids(list_ids=edge_ids)


class TemplateManager:
    @staticmethod
    def get_templates(template_ids: List[int]) -> List[Template]:
        from nlpbridge.config import CONFIG
        session = MySqlDBClient(CONFIG).get_session()
        return CRUDTemplate(session).get_by_ids(list_ids=template_ids)


class GraphState(TypedDict):
    nodes: Optional[List[Node]]
    context: Any | Dict[str, Any]





class Condition(Callable[[dict], TypedDict]):
    def __init__(self, cur_node: Node, target_nodes: List[Node]):
        self.cur_node = cur_node
        self.target_nodes = target_nodes

    def __call__(self, node_state: TypedDict) -> str:
        # Randomly select the next node from the current node and the node pointed to by the node.
        next = random.choice([self.cur_node, *self.target_nodes])
        print(f'({self.cur_node.name})[remains]: {self.cur_node.chat_limit}')
        if next.chat_limit <= 0:
            next = random.choice([*self.target_nodes])
        return next.name

    @classmethod
    def init_with_params(cls, cur_node, target_nodes):
        return cls(cur_node, target_nodes)


class RouterManager:
    @staticmethod
    def get_router(router_id: int) -> Router:
        from nlpbridge.config import CONFIG
        session = MySqlDBClient(CONFIG).get_session()
        return CRUDRouter(session).get_by_id(id=router_id)

    def get_graph(self, chat_id: str, llm, router_id: int, condition_cls: Condition = Condition,
                  node_cls: Node = Node, **kwargs) -> Tuple[CompiledGraph, dict]:
        router = RouterManager.get_router(router_id)
        node_ids = router.node_ids
        edge_ids = router.edge_ids
        int_node_ids = [int(num) for num in node_ids.split(',')]
        int_edge_ids = [int(num) for num in edge_ids.split(',')]
        nodes = NodeManager.get_nodes(int_node_ids)
        edges = EdgeManager.get_edges(int_edge_ids)

        runnable_nodes = self.convert_to_runnable_node(nodes, edges, llm, chat_id, node_cls, **kwargs)
        graph = self._create_graph(runnable_nodes, edges, condition_cls)
        cfg = {"configurable": {"thread_id": router_id}}
        graph.update_state(config=cfg, values={"nodes": nodes})
        return graph, cfg

    def _create_graph(self, nodes: List[Node], edges: List[Edge], condition_cls: Condition) -> CompiledGraph:
        graph = StateGraph(GraphState)
        for node in nodes:
            node_name = self.get_node_name(node)
            graph.add_node(node_name, node)
        # fixme confirm the start_node and end_node storage
        start_node = nodes[0]
        graph.set_entry_point(self.get_node_name(start_node))
        self._create_conditional_edges(graph, nodes, edges, condition_cls)
        return graph.compile(checkpointer=memory)

    def _create_conditional_edges(self, graph: StateGraph, nodes: List[Node], edges: List[Edge],
                                  condition_cls: Condition) -> StateGraph:
        exist_start_ids = []
        for edge in edges:
            start_id = edge.start_id
            if start_id in exist_start_ids:
                continue
            exist_start_ids.append(start_id)

            target_edges = [edge for edge in edges if edge.start_id == start_id]
            target_ids = [edge.end_id for edge in target_edges]
            target_nodes = [node for node in nodes if node.id in target_ids]
            target_node_names = [self.get_node_name(node) for node in target_nodes]

            cur_node = self.find_node(nodes, edge.start_id)
            cur_node_name = self.get_node_name(cur_node)
            path_map = {name: name for name in target_node_names}
            path_map[cur_node_name] = cur_node_name

            graph.add_conditional_edges(
                cur_node_name,
                condition_cls.init_with_params(cur_node, target_nodes),
                path_map
            )
        return graph

    @staticmethod
    def get_node_name(node: Node) -> str:
        node_name = node.name
        if node_name == "unnamed":
            if isinstance(node, Runnable):
                node_name = getattr(node, "__name__", node.__class__.__name__)
        return node_name

    @staticmethod
    def find_node(nodes: List[Node], start_id: str) -> Node:
        return next((node for node in nodes if node.id == start_id), None)

    @staticmethod
    def convert_to_runnable_node(nodes: List[NodeModel], edges: List[Edge], llm, chat_id: str, node_cls: Node, **kwargs) -> List[
        Node]:
        runnable_nodes = []
        for node in nodes:
            system_template_ids = [int(template_id) for template_id in node.system_template_ids.split(",")]
            user_template_ids = [int(template_id) for template_id in node.user_template_ids.split(",")]
            system_templates = TemplateManager.get_templates(system_template_ids)
            user_templates = TemplateManager.get_templates(user_template_ids)
            in_edges = [edge for edge in edges if edge.end_id == node.id]
            out_edges = [edge for edge in edges if edge.start_id == node.id]
            tools = [tool_list[name] for name in node.tool_names.split(",")]

            runnable_node = node_cls.init_with_params(
                node.id,
                node.name,
                node.description,
                node.goal,
                node.chat_limit,
                system_template_ids,
                user_template_ids,
                system_templates,
                user_templates,
                tools,
                in_edges,
                out_edges,
                llm,
                chat_id,
                **kwargs
            )
            runnable_nodes.append(runnable_node)
        return runnable_nodes
