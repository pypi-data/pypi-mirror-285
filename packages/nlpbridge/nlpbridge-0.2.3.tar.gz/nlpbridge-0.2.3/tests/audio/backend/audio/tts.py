from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from typing import List, Union
import re
import httpx
import ssl

app = FastAPI()
router = APIRouter()


async def call_tts_service(text: str):
    url = "https://172.22.121.6:40123/text-to-speech?text=" + text
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with httpx.AsyncClient(verify=ssl_context, timeout=30) as client:
        try:
            response = await client.get(url, timeout=60)
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} for text: {text}")
        except httpx.RequestError as e:
            print(f"Request error: {e} for text: {text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e} for text: {text}")
        return None


@router.post("/synthesizer")
async def synthesizer(input_type: int, text: Union[str, None] = None,
                      texts: Union[List[str], None] = None):
    if input_type == 0 and text is not None:
        texts = re.split(r'[，,。？！.!?]', text)
    elif input_type == 1 and texts is not None:
        pass
    else:
        raise HTTPException(status_code=400, detail="Invalid input")

    async def audio_stream():
        for segment in texts:
            segment = segment.strip()
            if segment:
                audio_bytes = await call_tts_service(segment)
                if audio_bytes:
                    print(f"Generated audio for segment: {segment}")
                    yield audio_bytes
                else:
                    print(f"No audio generated for segment: {segment}")

    return StreamingResponse(audio_stream(), media_type="audio/wav")
