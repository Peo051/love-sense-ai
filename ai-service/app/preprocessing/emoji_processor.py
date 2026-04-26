import re

class EmojiProcessor:
    def __init__(self):
        self.emoji_meanings = {
            "❤️": "yêu",
            "😊": "vui",
            "😢": "buồn",
            "😍": "yêu thích",
            "😘": "hôn",
            "🥰": "yêu",
            "😭": "khóc",
            "😡": "giận",
            "🤗": "ôm"
        }
    
    def extract_emojis(self, text: str) -> list:
        """Extract emojis from text"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.findall(text)
    
    def convert_to_text(self, text: str) -> str:
        """Convert emojis to text meanings"""
        for emoji, meaning in self.emoji_meanings.items():
            text = text.replace(emoji, f" {meaning} ")
        return text.strip()
    
    def remove_emojis(self, text: str) -> str:
        """Remove all emojis from text"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub(r'', text)
