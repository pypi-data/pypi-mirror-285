import requests
from typing import Union
from pydantic import BaseModel
import os
from funasr import AutoModel
from fastapi import APIRouter

router = APIRouter()


class SpeechRequest(BaseModel):
    audio_path: Union[str, None] = None
    audio_bytes: Union[bytes, None] = None
    audio_url: Union[str, None] = None


def recognize_speech(file_path: str):
    model = AutoModel(model="paraformer-zh", model_revision="v2.0.4",
                      vad_model="fsmn-vad", vad_model_revision="v2.0.4",
                      punc_model="ct-punc-c", punc_model_revision="v2.0.4")
    res = model.generate(input=file_path, batch_size_s=300)
    return res


@router.post("/asr")
async def asr(request: SpeechRequest):
    file_path = None

    if request.audio_path:
        file_path = request.audio_path
    elif request.audio_bytes:
        file_path = "./temp_audio.wav"
        with open(file_path, "wb") as buffer:
            buffer.write(request.audio_bytes)
    elif request.audio_url:
        response = requests.get(request.audio_url)
        file_path = "./temp_audio.wav"
        with open(file_path, "wb") as buffer:
            buffer.write(response.content)

    if not file_path:
        return {"error": "No valid input provided"}
    try:
        result = recognize_speech(file_path)
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(file_path) and request.audio_path is None:
            os.remove(file_path)
