import json
import traceback
import uuid
from abc import abstractmethod

from nlpbridge.audio._client import HTTPClient
from nlpbridge.audio._exception import GZUServerException
from nlpbridge.audio.component import AudioBase
from nlpbridge.audio.components.asr.model import GzuAsrRequest
from nlpbridge.audio.components.asr.model import ShortSpeechRecognitionRequest, ShortSpeechRecognitionResponse, \
    ASRInMsg, ASROutMsg
from nlpbridge.audio.message import Message


class BaseASR(AudioBase):
    def __init__(self, config: dict = None, service_name: str = 'gzu-asr'):
        from nlpbridge.config import CONFIG
        self.config = config if config else CONFIG.dict_config
        self.config = self.config['asr'][service_name]
        self.gateway = self.config['gateway']
        self.service = self.config['service']
        self.url = self.gateway + self.service
        super().__init__(gateway=self.gateway)

    @abstractmethod
    def run(self, *inputs, **kwargs):
        raise NotImplementedError


class ASR4Gzu(BaseASR):
    @HTTPClient.check_param
    def run(self,
            message: Message,
            timeout: float = None,
            retry: int = 0,
            stream: bool = False
            ) -> Message:
        inp = ASRInMsg(**message.content)
        request = GzuAsrRequest()
        request.audio_url = inp.audio_url
        request.audio_path = inp.audio_path
        response = self.recognize4Gzu(request=request, stream=False, retry=retry, timeout=timeout)
        out = ASROutMsg(result=json.loads(response.content))
        return Message(content=out.model_dump())

    @HTTPClient.check_param
    def runStream(self,
                  message: Message,
                  timeout: float = None,
                  retry: int = 0
                  ) -> Message:
        inp = ASRInMsg(**message.content)
        request = GzuAsrRequest()
        request.audio_url = inp.audio_url
        request.audio_path = inp.audio_path
        return Message(content=self.recognize4Gzu(request=request, stream=True, retry=retry, timeout=timeout))

    def recognize4Gzu(self, request, retry, stream, timeout):
        auth_header = self.http_client.auth_header()
        if retry != self.http_client.retry.total:
            self.http_client.retry.total = retry
        data = GzuAsrRequest.to_dict(request)
        response = self.http_client.session.post(self.url, json=data, timeout=timeout, headers=auth_header,
                                                 verify=False,
                                                 stream=stream)
        request_id = self.http_client.response_request_id(response)
        response.request_id = request_id
        if not stream:
            return response
        else:
            return self.__class__._iterate_chunk(request_id, response)

    @staticmethod
    def _iterate_chunk(request_id, response):
        try:
            for line in response.iter_lines():
                chunk = line.decode('utf-8')
                if chunk.startswith('data:'):
                    chunk = chunk.replace('data: ', '')
                    chunk = chunk.replace("'", "\"")
                    item_list = json.loads(chunk)
                    for item in item_list:
                        yield item['text']
        except Exception as e:
            raise GZUServerException(request_id=request_id, message=traceback.format_exc())
        finally:
            response.close()


class ASR4Baidu(BaseASR):
    @HTTPClient.check_param
    def run(self, message: Message, audio_format: str = "pcm", rate: int = 16000,
            timeout: float = None, retry: int = 0) -> Message:
        inp = ASRInMsg(**message.content)
        request = ShortSpeechRecognitionRequest()
        request.format = audio_format
        request.rate = rate
        request.cuid = str(uuid.uuid4())
        request.dev_pid = "80001"
        request.speech = inp.raw_audio
        response = self._recognize(request, timeout, retry)
        out = ASROutMsg(result=list(response.result))
        return Message(content=out.model_dump())

    def _recognize(self, request: ShortSpeechRecognitionRequest, timeout: float = None,
                   retry: int = 0) -> ShortSpeechRecognitionResponse:
        ContentType = "audio/" + request.format + ";rate=" + str(request.rate)
        headers = self.http_client.auth_header()
        headers['content-type'] = ContentType
        params = {
            'dev_pid': request.dev_pid,
            'cuid': request.cuid
        }
        if retry != self.http_client.retry.total:
            self.http_client.retry.total = retry
        response = self.http_client.session.post(self.url, params=params, headers=headers, data=request.speech,
                                                 timeout=timeout)
        self.http_client.check_response_header(response)
        data = response.json()
        self.http_client.check_response_json(data)
        request_id = self.http_client.response_request_id(response)
        self.__class__._check_service_error(request_id, data)
        response = ShortSpeechRecognitionResponse.from_json(payload=json.dumps(data))
        response.request_id = request_id
        return response

    @staticmethod
    def _check_service_error(request_id: str, data: dict):
        if "err_no" in data and "err_msg" in data:
            if data["err_no"] != 0:
                raise GZUServerException(
                    request_id=request_id,
                    service_err_code=data["err_no"],
                    service_err_message=data["err_msg"]
                )


ASR_RECOGNIZERS = {
    'baidu-asr': ASR4Baidu,
    'gzu-asr': ASR4Gzu,
    'gzu-asr-stream': ASR4Gzu,
}


class ASR:
    def __init__(self, service_name='gzu-asr', config: dict = None):
        self.config = config
        self.service_name = service_name.lower()
        self.recognizers = ASR_RECOGNIZERS

    def run(self, message: Message, **kwargs):
        recognizer = self.getRecognizer()(config=self.config, service_name=self.service_name)
        return recognizer.run(message, **kwargs)

    def runStream(self, message: Message, **kwargs):
        recognizer = self.getRecognizer()(config=self.config, service_name=self.service_name)
        return recognizer.runStream(message, **kwargs)

    def getRecognizer(self):
        if self.service_name not in self.recognizers:
            raise ValueError(f"Recognition service '{self.service_name}' is not supported.")
        return self.recognizers[self.service_name]
