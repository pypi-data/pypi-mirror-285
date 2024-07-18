from fastapi import APIRouter
from audio import asr
from audio import asrStream
from audio import tts

router = APIRouter()

router.include_router(asr.router, prefix="/audio", tags=["audio"])
router.include_router(asrStream.router, prefix="/audio", tags=["audio"])
router.include_router(tts.router, prefix="/audio", tags=["audio"])
