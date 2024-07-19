from io import BytesIO
from pathlib import Path

import pydub
from injected_utils.injected_cache_utils import sqlite_cache, async_cached
from openai import AsyncOpenAI
from pinjected import Injected, injected,instances


@injected
async def a_transcribe_bytes(async_openai_client: AsyncOpenAI, /, sound_bytes: bytes) -> str:
    response = await async_openai_client.audio.transcriptions.create(
        model="whisper-1",
        file=sound_bytes,
    )
    return response['text']


@async_cached(
    cache=sqlite_cache(injected("cache_root_path") / "transcribe_mp3_file.sqlite"),
)
@injected
async def a_transcribe_mp3_file(a_transcribe_bytes, /, file: Path, start_sec: float = None,
                                end_sec: float = None) -> str:
    segment = pydub.AudioSegment.from_file(file, format="mp3")
    out_bytes = BytesIO()
    if start_sec is None:
        start_millis = 0
    else:
        start_millis = min(start_sec * 1000, len(segment) - 1)

    if end_sec is None:
        end_millis = len(segment) - 1
    else:
        end_millis = min(end_sec * 1000, len(segment) - 1)
    segment[start_millis:end_millis].export(out_f=out_bytes)
    out_bytes.seek(0)
    text = await a_transcribe_bytes(out_bytes.read())
    return text


test_transcribe: Injected = a_transcribe_mp3_file(Path("recording.mp3"))

__meta_design__ = instances(
)



