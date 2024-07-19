from halerium_utilities.prompt.models import call_model
import json


def transcribe_audio(audio_b64: str) -> dict:

    body = {
        "audio": audio_b64,
        "diarize": True,
    }
    r = call_model("nova2", body=body, parse_data=True)

    ans = ""
    for sse in r:
        # print(sse.data.get("paragraphs")) # for debugging
        # print(json.dumps(sse.data, indent=4)) # for debugging

        paragraphs = sse.data.get("paragraphs")
        if isinstance(paragraphs, dict):
            transcript = paragraphs.get("transcript")
            if transcript is not None:
                ans += transcript

    return ans
