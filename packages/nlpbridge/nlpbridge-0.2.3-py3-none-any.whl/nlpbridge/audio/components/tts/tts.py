r"""text to speech component."""
import base64
import traceback
from abc import abstractmethod
from typing import Literal

from nlpbridge.audio._client import HTTPClient
from nlpbridge.audio._exception import GZUServerException
from nlpbridge.audio.component import AudioBase
from nlpbridge.audio.components.tts.model import TTSInMsg, TTSOutMsg, TTSRequest, TTSResponse
from nlpbridge.audio.message import Message


class BaseTTS(AudioBase):
    def __init__(self, config: dict = None, service_name: str = 'gzu-tts'):
        from nlpbridge.config import CONFIG
        self.config = config if config else CONFIG.dict_config
        self.config = self.config['tts'][service_name]
        self.gateway = self.config['gateway']
        self.service = self.config['service']
        self.url = self.gateway + self.service
        super().__init__(gateway=self.gateway)

    @abstractmethod
    def run(self, *inputs, **kwargs):
        raise NotImplementedError


class TTS4Gzu(BaseTTS):
    @HTTPClient.check_param
    def run(
            self,
            message: Message,
            timeout: float = None,
            retry: int = 0
    ):
        inp = TTSInMsg(**message.content)
        url = self.url + "?text=" + inp.text
        if retry != self.http_client.retry.total:
            self.http_client.retry.total = retry
        auth_header = self.http_client.auth_header()
        response = self.http_client.session.get(url, timeout=timeout, headers=auth_header, verify=False)
        return response


class TTS4Baidu(BaseTTS):
    @HTTPClient.check_param
    def run(self,
            message: Message,
            model: Literal["baidu-tts", "paddlespeech-tts"] = "baidu-tts",
            speed: int = 5,
            pitch: int = 5,
            volume: int = 5,
            person: int = 0,
            audio_type: Literal["mp3", "wav", "pcm"] = "mp3",
            timeout: float = None,
            retry: int = 0,
            stream: bool = False) -> Message:
        inp = TTSInMsg(**message.content)
        request = TTSRequest()
        request.tex = inp.text
        request.spd = speed
        request.pit = pitch
        request.vol = volume
        request.per = person
        request.stream = stream
        if audio_type == "mp3":
            request.aue = 3
        elif audio_type == "wav" or audio_type == "pcm":
            request.aue = 6
        if stream:
            return Message(content=self.__synthesis(request=request, stream=True, retry=retry))
        else:
            response = self.__synthesis(request=request, timeout=timeout, retry=retry)
            out = TTSOutMsg(audio_binary=response.binary, audio_type=audio_type)
            return Message(content=out.model_dump())

    def __synthesis(self,
                    request: TTSRequest,
                    stream: bool = False,
                    timeout: float = None,
                    retry: int = 0
                    ) -> TTSResponse:
        request.ctp = "1"
        request.lan = "zh"
        request.cuid = "1"
        request.tp_project_id = "paddlespeech"
        request.tp_per_id = "100001"
        if retry != self.http_client.retry.total:
            self.http_client.retry.total = retry
        auth_header = self.http_client.auth_header()
        auth_header['Content-type'] = "application/json"
        if not stream:
            response = self.http_client.session.post(self.url, json=TTSRequest.to_dict(request),
                                                     timeout=timeout, headers=auth_header)
        if stream:
            response = self.http_client.session.post(self.url, json=TTSRequest.to_dict(request), timeout=(10, 200),
                                                     headers=auth_header, stream=True)

        self.http_client.check_response_header(response)
        content_type = response.headers.get("Content-Type", "application/json")
        request_id = self.http_client.response_request_id(response)
        if content_type.find("application/json") != -1:
            data = response.json()
            self.http_client.check_response_json(data)
            self.__class__.__check_service_error(request_id, data)
        if not stream:
            return TTSResponse(binary=response.content, request_id=request_id, aue=request.aue)
        else:
            return self.__class__._iterate_chunk(request_id, response)

    @staticmethod
    def __check_service_error(request_id: str, data: dict):
        if "err_no" in data or "err_msg" in data or 'sn' in data or 'idx' in data:
            raise GZUServerException(
                request_id=request_id,
                service_err_code=data.get("err_no", 0),
                service_err_message="{} . {} . {}]".
                format(data.get("err_msg", ""),
                       data.get("sn", ""),
                       data.get("idx", ""))
            )

    @staticmethod
    def _iterate_chunk(request_id, response):
        try:
            for line in response.iter_lines():
                chunk = line.decode('utf-8')
                if chunk.startswith('data:'):
                    chunk = chunk.replace('data: ', '')
                    yield base64.b64decode(chunk)
        except Exception as e:
            raise GZUServerException(request_id=request_id, message=traceback.format_exc())
        finally:
            response.close()


TTS_SYNTHESISERS = {
    'baidu-tts': TTS4Baidu,
    'gzu-tts': TTS4Gzu
}


class TTS:
    def __init__(self, service_name='gzu-tts', config: dict = None):
        self.config = config
        self.service_name = service_name.lower()
        self.synthesisers = TTS_SYNTHESISERS

    def run(self, message: Message, **kwargs):
        synthesis = self.getSynthesiser()(config=self.config, service_name=self.service_name)
        return synthesis.run(message, **kwargs)

    def getSynthesiser(self):
        if self.service_name not in self.synthesisers:
            raise ValueError(f"Synthesis service '{self.service_name}' is not supported.")
        return self.synthesisers[self.service_name]
