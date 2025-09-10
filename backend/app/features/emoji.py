import re
import emoji

EMOJI_REGEX = emoji.get_emoji_regexp()

def extract_emojis(text: str) -> list[str]:
    if not text:
        return []
    return [e for e in EMOJI_REGEX.findall(text)]
