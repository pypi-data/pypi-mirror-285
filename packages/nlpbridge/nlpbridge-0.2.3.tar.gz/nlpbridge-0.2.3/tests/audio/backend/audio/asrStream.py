from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.params import Query
from pydantic import BaseModel
import soundfile
from io import BytesIO
import requests
from funasr import AutoModel
from fastapi import APIRouter

router = APIRouter()
app = FastAPI()


# 定义请求参数模型
class AudioRequest(BaseModel):
    audio_url: str = Query(None)
    audio_path: str = Query(None)


# 定义语音识别函数
def recognize_speech(speech, sample_rate, chunk_size, encoder_chunk_look_back, decoder_chunk_look_back):
    model = AutoModel(model="paraformer-zh-streaming", model_revision="v2.0.4")
    chunk_stride = chunk_size[1] * 960  # 600ms
    cache = {}
    total_chunk_num = int(len(speech) / chunk_stride + 1)

    def generate_chunks():
        for i in range(total_chunk_num):
            speech_chunk = speech[i * chunk_stride:(i + 1) * chunk_stride]
            is_final = i == total_chunk_num - 1
            res = model.generate(input=speech_chunk, cache=cache, is_final=is_final,
                                 chunk_size=chunk_size,
                                 encoder_chunk_look_back=encoder_chunk_look_back,
                                 decoder_chunk_look_back=decoder_chunk_look_back)
            yield res

    return generate_chunks()


@router.post("/asr-stream")
async def asr_stream(audio_request: AudioRequest):
    if audio_request.audio_url:
        response = requests.get(audio_request.audio_url)
        response.raise_for_status()
        wav_file = BytesIO(response.content)
    elif audio_request.audio_path:
        try:
            with open(audio_request.audio_path, 'rb') as f:
                wav_file = BytesIO(f.read())
        except FileNotFoundError:
            raise ValueError("Audio file not found")
    speech, sample_rate = soundfile.read(wav_file)
    chunk_size = [0, 10, 5]  # 600ms
    encoder_chunk_look_back = 4
    decoder_chunk_look_back = 1
    chunks = recognize_speech(speech, sample_rate, chunk_size, encoder_chunk_look_back, decoder_chunk_look_back)

    def stream_response(chunks):
        for chunk in chunks:
            yield f"data: {chunk}\n"

    return StreamingResponse(stream_response(chunks), media_type="text/event-stream; charset=utf-8")
