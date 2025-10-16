import base64
import mimetypes
from pathlib import Path

def parse_user(user_input: str):
    """
    Converts user input into LangChain v1-alpha multimodal message format.
    Supports: text-only, image, audio, video, and file content.
    """
    tokens = user_input.strip().split(maxsplit=2)
    role = "user"
    content_blocks = []

    if len(tokens) >= 2 and tokens[0].startswith("/"):
        command = tokens[0].lstrip("/")
        path = Path(tokens[1]).expanduser()
        prompt_text = tokens[2] if len(tokens) > 2 else f"Analyze this {command} file."

        if not path.exists():
            return {"role": role, "content": [{"type": "text", "text": user_input}]}

        mime_type, _ = mimetypes.guess_type(path)
        if not mime_type:
            mime_type = "application/octet-stream"

        category = {
            "img": "image",
            "file": "file",
            "audio": "audio",
            "video": "video"
        }.get(command, "file")

        b64 = base64.b64encode(path.read_bytes()).decode("utf-8")

        content_blocks = [
            {"type": "text", "text": prompt_text},
            {
                "type": category,
                "base64": b64,
                "mime_type": mime_type
            },
        ]
    else:
        content_blocks = [{"type": "text", "text": user_input}]
    return {"role": role, "content": content_blocks}
