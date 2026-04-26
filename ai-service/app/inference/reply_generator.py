from typing import List
import random

class ReplyGenerator:
    def __init__(self):
        self.reply_templates = {
            "Hạnh phúc": [
                "Anh cũng rất vui!",
                "Em làm anh hạnh phúc quá!",
                "Cảm ơn em đã làm anh vui!"
            ],
            "Yêu thương": [
                "Anh cũng yêu em nhiều lắm!",
                "Em là tất cả của anh!",
                "Anh yêu em!"
            ],
            "Quan tâm": [
                "Cảm ơn em đã quan tâm!",
                "Anh cũng luôn nghĩ về em!",
                "Em thật chu đáo!"
            ],
            "Buồn": [
                "Anh ở đây với em!",
                "Đừng buồn nữa em nhé!",
                "Anh sẽ luôn bên em!"
            ],
            "Lo lắng": [
                "Đừng lo, mọi chuyện sẽ ổn thôi!",
                "Anh sẽ giúp em!",
                "Cùng nhau vượt qua nhé!"
            ]
        }
    
    def generate(self, text: str, emotion: str) -> List[str]:
        """Generate suggested replies based on emotion"""
        # Get templates for emotion
        templates = self.reply_templates.get(
            emotion,
            ["Cảm ơn em!", "Anh hiểu rồi!", "Được em!"]
        )
        
        # Return 3 random suggestions
        return random.sample(templates, min(3, len(templates)))
