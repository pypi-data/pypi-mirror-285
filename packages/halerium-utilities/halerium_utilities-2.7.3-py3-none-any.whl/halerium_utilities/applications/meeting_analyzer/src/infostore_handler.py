# infrastructure imports
import uuid
from datetime import datetime

# halerium_utilities imports
from halerium_utilities.prompt.models import call_model
from halerium_utilities.stores.api import (
    get_workspace_information_stores,
    get_information_store_info,
    add_chunks_to_vectorstore
)


TARGET_CHUNK_LEN = 4000
MAX_CHUNK_LEN = 5000

SYSTEM_MESSAGE_SUMMARIES = """
You are given the results of a meeting (e.g. meeting minutes, todos etc.).
Your task is to extract the title of the meeting. If no title is given in the data create a concise title based on the content.
ANSWER WITH THE MEETING TITLE ONLY! 
"""


def fetch_infostore(name: str):
    """
    Fetches the information store with the given name.

    Args:
        name (str): Name of the information store to fetch.

    Returns:
        str: Information store id.
    """
    # retrieve the information stores of the current workspace
    stores = get_workspace_information_stores()['items']

    # get the corresponding info store id
    info_store_id = None
    for store in stores:
        if store.get('name') == name:
            info_store_id = store.get('uuid')
            break

    # get the vectorstore id
    store_info = get_information_store_info(info_store_id)
    vectorstore_id = store_info["item"]["vectorstores"][0]["id"]
    return vectorstore_id


def push_summaries_to_infostore(list_of_text: list, info_store_name: str = "SummariesStore"):
    """
    Pushes the given list of text to the information store with the given name.

    Args:
        list_of_text (list): List of text to push to the information store.
        info_store_name (str, optional): Name of the information store to push the text to. Defaults to "testStore".
    """
    # get the vectorstore id
    vectorstore_id = fetch_infostore(info_store_name)

    # prepare metadata
    today = datetime.now().strftime("%Y-%m-%d")
    meeting_id = str(uuid.uuid4())[:8]

    try:
        # meeting title
        body = {
            "messages": [
                {"role": "system", "content": SYSTEM_MESSAGE_SUMMARIES},
                {"role": "user",
                 "content": "\n\n".join(list_of_text)}
            ],
            "temperature": 0
        }
        # build up the metadata
        gen = call_model("chat-gpt-35", body=body, parse_data=True)
        meeting_title = ""
        for sse in gen:
            meeting_title += sse.data.get("chunk", "")
        meeting_title = meeting_title.strip()
    except:
        meeting_title = "unknown title"

    # prepare the chunks
    chunks = []
    for i, chunk in enumerate(list_of_text):

        # build the entry
        entry = {
            "content": chunk,
            "metadata": {"date": f"{today}",
                         "meeting": f"{meeting_title}",
                         "meeting_id": f"{meeting_id}",
                         "type": "summary",
                         "chunk_number": f"{i+1}",
                         "total_chunks": f"{len(list_of_text)}"}
        }
        chunks.append(entry)

    # push the information to the vectorstore
    add_chunks_to_vectorstore(vectorstore_id, chunks)

    return meeting_title, meeting_id


def push_transcript_to_infostore(transcript: str, info_store_name: str = "TranscriptsStore",
                                 meeting_title=None, meeting_id=None):
    """
    Pushes the given transcript to the information store with the given name.

    Args:
        transcript (str): Transcript to push to the information store.
        info_store_name (str, optional): Name of the information store to push the transcript to. Defaults to "transStore".
        meeting_title (str, optional): The title of the meeting to be used in the metadata
        meeting_id (str, optional): The id of the meeting to be used in the metadata
    """
    # get the vectorstore id
    vectorstore_id = fetch_infostore(info_store_name)

    # prepare metadata
    today = datetime.now().strftime("%Y-%m-%d")

    split_text = [
        line.split(" ") for line in transcript.split("\n")
    ]

    text_chunks = [""]
    for line in split_text:
        if len(text_chunks[-1]) >= TARGET_CHUNK_LEN:
            text_chunks.append("")

        # case 1: whole line fits in chunk
        joined_line = " ".join(line)
        if len(text_chunks[-1] + joined_line) < MAX_CHUNK_LEN:
            text_chunks[-1] += joined_line + "\n"
        # case 2: partial line fits in chunk
        else:
            for word in line:
                if len(text_chunks[-1]) < TARGET_CHUNK_LEN:
                    if text_chunks[-1]:  # Add a space if the chunk is not empty
                        text_chunks[-1] += " "
                    text_chunks[-1] += word
                else:
                    text_chunks.append("")
                    break

    chunks = []
    for i, content in enumerate(text_chunks):
        entry = {
            "content": content,
            "metadata": {
                "date": f"{today}",
                "meeting": f"{meeting_title}",
                "meeting_id": f"{meeting_id}",
                "type": "transcript",
                "chunk_number": f"{i+1}",
                "total_chunks": f"{len(text_chunks)}"
            }
        }

        chunks.append(entry)

    # push the information to the vectorstore
    add_chunks_to_vectorstore(vectorstore_id, chunks)

