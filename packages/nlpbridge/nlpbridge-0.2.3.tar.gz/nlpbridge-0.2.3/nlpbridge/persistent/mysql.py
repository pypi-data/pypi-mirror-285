from typing import List, Any, Dict, TypeVar, Generic, Union
import sys, os
sys.path.append(os.getcwd())

from nlpbridge.persistent.mysql_dataschema import Template, Router, Node, Edge, Chat, Customer, Tag
from sqlmodel import insert, update, select, delete, func
from sqlmodel import SQLModel
from sqlmodel import Session


ModelType = TypeVar("ModelType", bound=SQLModel)


class MySqlDBClient():
    def __init__(self, config) -> None:
        super().__init__()
        try:
            import sqlalchemy
        except ImportError:
            raise ImportError(
                "Could not import sqlalchemy python package. "
                "Please install it with `pip install SQLAlchemy`."
            )

        self.mysql_config = config.dict_config['mysql']
        self.user = self.mysql_config['user']
        self.url = self.mysql_config['host']
        self.port = self.mysql_config['port']
        self.password = self.mysql_config['password']
        self.db = self.mysql_config['db']

        self.client = sqlalchemy.engine.create_engine(f"mysql+pymysql://{self.user}:{self.password}@{self.url}:{self.port}/{self.db}")
        self.db_session = Session(self.client)


    def get_session(self):
        return self.db_session


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: type[ModelType], db_session: Union[Session, None] = None) -> None:
        self.model = model
        self.db_session = db_session


    def get_by_id(self, *, id: int, db_session: Union[Session, None] = None) ->Union[ModelType, None]:
        db_session = db_session or self.db_session
        query = select(self.model).where(self.model.id == id)
        response = db_session.exec(query)
        return response.one_or_none()
    

    def get_by_ids(self, *, list_ids: list[int], db_session: Union[Session, None] = None) -> Union[list[ModelType], None]:
        db_session = db_session or self.db_session
        response = db_session.exec(
            select(self.model).where(self.model.id.in_(list_ids))
        )
        return response.all()


    def get_count(self, db_session: Union[Session, None] = None) -> Union[int, None]:
        db_session = db_session or self.db_session
        response = db_session.exec(select(func.count()).select_from(select(self.model).subquery()))
        return response.one_or_none()


    def get_multi(self, *, skip: int = 0, limit: int = 100, db_session: Union[Session, None] = None) -> list[ModelType]:
        db_session = db_session or self.db_session
        query = select(self.model).offset(skip).limit(limit).order_by(self.model.id)
        response = db_session.exec(query)
        return response.all()


    def create(self, *, obj_in: Union[ModelType, Dict], db_session: Union[Session, None] = None) -> ModelType:
        db_session = db_session or self.db_session
        db_obj = self.model.model_validate(obj_in)  # type: ignore            

        db_session.add(db_obj)
        db_session.commit()
        db_session.refresh(db_obj)
        return db_obj
    

    def update(self, *, obj_current: ModelType, obj_new: Union[ModelType, Dict[str, Any]], db_session: Union[Session, None] = None) -> ModelType:
        db_session = db_session or self.db_session

        if isinstance(obj_new, dict):
            update_data = obj_new
        else:
            update_data = obj_new.model_dump(
                exclude_unset=True
            )  # This tells Pydantic to not include the values that were not sent
        for field in update_data:
            setattr(obj_current, field, update_data[field])

        db_session.add(obj_current)
        db_session.commit()
        db_session.refresh(obj_current)
        return obj_current
    

    def delete(self, *, id: int, db_session: Union[Session, None] = None) -> ModelType:
        db_session = db_session or self.db_session
        response = db_session.exec(
            select(self.model).where(self.model.id == id)
        )
        obj = response.one()
        db_session.delete(obj)
        db_session.commit()
        return obj


class CRUDTemplate(CRUDBase):
    def __init__(self, db_session: Union[Session, None] = None) -> None:
        super().__init__(model=Template, db_session=db_session)


    def get_by_name(self, *, name: str, db_session: Union[Session, None] = None) -> Union[Template, None]:
        templates = db_session.exec(
            select(Template).where(Template.name == name)
        )
        return templates.one()


class CRUDRouter(CRUDBase):
    def __init__(self, db_session: Union[Session, None] = None) -> None:
        super().__init__(model=Router, db_session=db_session)


class CRUDNode(CRUDBase):
    def __init__(self, db_session: Union[Session, None] = None) -> None:
        super().__init__(model=Node, db_session=db_session)


class CRUDEdge(CRUDBase):
    def __init__(self, db_session: Union[Session, None] = None) -> None:
        super().__init__(model=Edge, db_session=db_session)


class CRUDChat(CRUDBase):
    def __init__(self, db_session: Union[Session, None] = None) -> None:
        super().__init__(model=Chat, db_session=db_session)
    

    def get_user_chats(self, *, user_id: int, db_session: Union[Session, None] = None):
        chats = db_session.exec(
            select(Chat).where(Chat.uid == user_id).order_by(Chat.ctime)
        )
        return chats.all()


    def get_router_user_chats(self, *, router_id: int, user_id: int, db_session: Union[Session, None] = None):
        chats = db_session.exec(
            select(Chat).where((Chat.router_id == router_id) & (Chat.uid == user_id)).order_by(Chat.ctime)
        )
        return chats.all()


class CRUDCustomer(CRUDBase):
    def __init__(self, db_session: Session | None = None) -> None:
        super().__init__(model=Customer, db_session=db_session)


class CRUDTag(CRUDBase):
    def __init__(self, db_session: Session | None = None) -> None:
        super().__init__(model=Tag, db_session=db_session)