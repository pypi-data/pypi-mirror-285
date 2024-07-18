

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Type,
    TypeVar,
    Union,
)


from abc import ABC, abstractmethod
from functools import lru_cache

from typing_extensions import TypeAlias

from langchain_core._api import deprecated
from langchain_core.messages import (
    AnyMessage,
    BaseMessage,
    MessageLikeRepresentation,
    get_buffer_string,
)
from langchain_core.prompt_values import PromptValue
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain_core.runnables import Runnable, RunnableSerializable
from langchain_core.utils import get_pydantic_field_names




class Client(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def retry(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_response(self, prompt) -> str:
        res = self.retry(prompt)
        pass

    @abstractmethod
    def stop(self):
        pass

from collections import defaultdict

class GZUVoiceRecognitionClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_local = kwargs.get("is_local", False)
        if is_local:
            self.logger.info("VoiceRecognition client initialized locally")
            # Initialize the voice recognition client locally
        else:
            self.logger.info("VoiceRecognition client initialized remotely")
            # Initialize the voice recognition client remotely
            # build connection to remote server
        # TODO: connection pools.
    
    def get_response(self, prompt) -> str:
        # http
        # voice_obj = minio.get_object("voice")
        res = self.retry(prompt)
        return res

