class CLIArgs:
    args = {
        "TEMPLATE": {
            "name_or_flags": ["-b", "--board"],
            "type": str,
            "help": "Path to the analyzer template board.",
            "required": True,
        },
        "MEETINGSPATH": {
            "name_or_flags": ["-m", "--meetings_path"],
            "type": str,
            "help": "Path to the folder in which the meeting analyses are stored.",
            "required": False,
            "default": "./meetings",
        },
        "UPLOADPATH": {
            "name_or_flags": ["-u", "--upload_path"],
            "type": str,
            "help": "Path to the folder in which uploaded audio files are stored.",
            "required": False,
            "default": "./uploads",
        },
        "PORT": {
            "name_or_flags": ["-o", "--port"],
            "type": int,
            "help": "Port to start API on. Defaults to 8501.",
            "required": False,
        },
        "CHATBOTPORT": {
            "name_or_flags": ["-c", "--cbport"],
            "type": int,
            "help": "Port under which to find the corresponding chatbot.",
            "required": True,
        },
        "SUMMARYSTORE": {
            "name_or_flags": ["-s", "--summary_store"],
            "type": str,
            "help": "Name of the information store in which meeting summaries are stored.",
            "required": False,
            "default": "SummariesStore",
        },
        "TRANSCRIPTSTORE": {
            "name_or_flags": ["-t", "--transcript_store"],
            "type": str,
            "help": "Name of the information store in which meeting summaries are stored.",
            "required": False,
            "default": "TranscriptsStore",
        },
    }
