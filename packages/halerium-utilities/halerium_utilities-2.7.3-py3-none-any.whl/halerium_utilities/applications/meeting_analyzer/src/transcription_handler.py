import base64
import httpx
import json
import logging
from pathlib import Path
import ssl
from typing import AsyncGenerator


class TranscriptionHandler:
    """
    TranscriptionHandler class for handling transcription of audio files.
    """

    @staticmethod
    async def transcribe_audio(path) -> AsyncGenerator[str | bool, None]:
        """
        Sends an audio file to the Whisper for transcription.

        Args:
            path (str): Path to the audio file.

        Returns:
            str: The transcript.
        """
        logger = logging.getLogger(__name__)

        try:
            ssl_context = ssl.create_default_context()
            timeout = httpx.Timeout(60.0, connect=60.0)
            n_chunk = 0
            audio_b64 = base64.b64encode(open(path, "rb").read()).decode("utf-8")

            # use the halerium prompt server for response generation
            endpoint = ""
            headers = ""
            payload = ""

            async with httpx.AsyncClient(verify=ssl_context, timeout=timeout) as client:
                async with client.stream(
                    method="POST", url=endpoint, json=payload, headers=headers
                ) as response:
                    async for chunk in response.aiter_lines():
                        logger.debug(f"transcript: {chunk}")
                        if "data: " in chunk:
                            content = json.loads(chunk[len("data: ") :])
                            n_chunk += 1
                            chunk = content.get("chunk")
                            completed = content.get("completed")
                            if chunk:
                                logger.debug(f"yielding transcript: {chunk}")
                                yield chunk
                            elif completed:
                                logger.debug(f"yielding status update: {completed}")
                                if content.get("error"):
                                    logger.error(
                                        f"There has been an error transcribing an audio file: {content.get('error')}"
                                    )
                                    yield f"I'm sorry, there has been an error transcribing your recording!"
                                yield completed

        except Exception as e:
            logger.error(f"There has been an error transcribing an audio file: {e}")
            yield f"I'm sorry, there has been an error transcribing your recording!"
