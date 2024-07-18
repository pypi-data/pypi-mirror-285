# from  langchain_community.llms.fake import FakeListLLM


# plugin_interface.py

# from  langchain_community.llms.fake import FakeListLLM


from langchain.agents import AgentType, initialize_agent, load_tools


# plugin_interface.py

import logging

class PluginInterface(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    @abstractmethod
    def terminate(self):
        pass


# plugin_interface.py

from abc import ABC, abstractmethod

class GUAIPlugin(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def deploy(self, *args, **kwargs):
        pass

    @abstractmethod
    def excute(self, *args, **kwargs):
        pass

    @abstractmethod
    def terminate(self):
        pass


class baseNLP(GUAIPlugin):
    def initialize(self):
        print("baseNLP plugin initialized")

    def deploy(self):
        """Support remotely deploy and locally deploy"""
        """
        if remote:
            # deploy to remote server
        else:
            # deploy to local server
        """
        self.logger.info(f"VoiceRecognition plugin deployed")

    def execute(self, text, question):
        # Assume there's an external NLP service API
        # Here we just simulate the service call
        self.logger.info(f"Processing text: {text} with question: {question}")
        answer = "simulated answer from NLP model"
        return answer

    def terminate(self):
        self.logger.info(f"baseNLP plugin terminated")


# voice_recognition.py
class VoiceRecognition(GUAIPlugin):
    def initialize(self):
        self.logger.info(f"VoiceRecognition plugin initialized")

    def deploy(self):
        """Support remotely deploy and locally deploy"""
        """
        if remote:
            # deploy to remote server
        else:
            # deploy to local server
        """
        self.logger.info(f"VoiceRecognition plugin deployed")

    def execute(self, audio_data):
        # Assume there's an external service API for voice recognition
        # Here we just simulate the service call
        self.logger.info(f"Processing audio data: {audio_data}")
        recognized_text = "simulated recognized text from audio"
        return recognized_text

    def terminate(self):
        self.logger.info(f"VoiceRecognition plugin terminated")




tools = load_tools(["python_repl"])

responses = ["Action: Python REPL\nAction Input: print(2 + 2)", "Final Answer: 4"]






import logging

# plugin_interface.py

from abc import ABC, abstractmethod

class GUAIPlugin(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def deploy(self, *args, **kwargs):
        pass

    @abstractmethod
    def excute(self, *args, **kwargs):
        pass

    @abstractmethod
    def terminate(self):
        pass


class baseNLP(GUAIPlugin):
    def initialize(self):
        print("baseNLP plugin initialized")

    def deploy(self):
        """Support remotely deploy and locally deploy"""
        """
        if remote:
            # deploy to remote server
        else:
            # deploy to local server
        """
        self.logger.info(f"VoiceRecognition plugin deployed")

    def execute(self, text, question):
        # Assume there's an external NLP service API
        # Here we just simulate the service call
        self.logger.info(f"Processing text: {text} with question: {question}")
        answer = "simulated answer from NLP model"
        return answer

    def terminate(self):
        self.logger.info(f"baseNLP plugin terminated")


# voice_recognition.py
class VoiceRecognition(GUAIPlugin):
    def initialize(self):
        self.logger.info(f"VoiceRecognition plugin initialized")

    def deploy(self):
        """Support remotely deploy and locally deploy"""
        """
        if remote:
            # deploy to remote server
        else:
            # deploy to local server
        """
        self.logger.info(f"VoiceRecognition plugin deployed")

    def execute(self, audio_data):
        # Assume there's an external service API for voice recognition
        # Here we just simulate the service call
        self.logger.info(f"Processing audio data: {audio_data}")
        recognized_text = "simulated recognized text from audio"
        return recognized_text

    def terminate(self):
        self.logger.info(f"VoiceRecognition plugin terminated")




tools = load_tools(["python_repl"])

responses = ["Action: Python REPL\nAction Input: print(2 + 2)", "Final Answer: 4"]


llm = FakeListLLM(responses=responses)

agent = initialize_agent(
    tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
) 

agent.invoke("whats 2 + 2")



