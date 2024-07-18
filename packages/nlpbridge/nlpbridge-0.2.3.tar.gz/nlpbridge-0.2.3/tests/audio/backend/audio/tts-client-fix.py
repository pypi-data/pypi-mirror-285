import asyncio
import aiohttp
from pydub import AudioSegment
import io
import simpleaudio as sa


async def play_audio_chunk(chunk):
    try:
        # 使用 pydub 重新处理音频片段
        audio_segment = AudioSegment.from_file(io.BytesIO(chunk), format="wav")

        # 将重新处理后的音频片段导出到内存中的 BytesIO 对象
        exported_chunk = io.BytesIO()
        audio_segment.export(exported_chunk, format="wav")
        exported_chunk.seek(0)
        # 使用 simpleaudio 播放处理后的音频片段
        play_obj = sa.play_buffer(
            exported_chunk.read(),
            num_channels=audio_segment.channels,
            bytes_per_sample=audio_segment.sample_width,
            sample_rate=audio_segment.frame_rate
        )
        play_obj.wait_done()
    except Exception as e:
        print(f"Error playing audio chunk: {e}")


async def fetch_audio(session, url, input_type, text=None, texts=None):
    params = {'input_type': input_type}
    if input_type == 0 and text:
        params['text'] = text
    elif input_type == 1 and texts:
        params['texts'] = texts

    try:
        async with session.post(url, params=params) as response:
            if response.status != 200:
                print(f"Request failed with status {response.status}")
                return b""

            audio_chunks = []
            try:
                async for chunk in response.content.iter_any():
                    if chunk:
                        print(f"Received chunk of size: {len(chunk)}")
                        await play_audio_chunk(chunk)
                        audio_chunks.append(chunk)

                print("Received all chunks successfully")
                return b"".join(audio_chunks)
            except aiohttp.ClientPayloadError as e:
                print(f"ClientPayloadError: {e}")
                return b""
            except Exception as e:
                print(f"An error occurred: {e}")
                return b""
    except aiohttp.ClientError as e:
        print(f"Aiohttp client error: {e}")
        return b""


async def main():
    url = "http://localhost:9999/api/v1/audio/synthesizer"
    input_type = 0  # 使用 text 字段
    text = (
        """随着科技的迅速发展，教育领域也经历了巨大的变革。科技不仅改变了教学和学习的方式，还扩展了教育的可能性和边界。
        从在线课程到交互式学习工具，科技为学生和教师提供了前所未有的资源和机遇。科技使得个性化学习成为可能。
        通过智能学习系统和适应性学习技术，教育内容可以根据学生的学习速度和能力进行定制。"""
    )
    async with aiohttp.ClientSession() as session:
        await fetch_audio(session, url, input_type, text=text)


if __name__ == "__main__":
    asyncio.run(main())
