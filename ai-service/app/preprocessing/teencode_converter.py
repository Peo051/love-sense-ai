class TeencodeConverter:
    def __init__(self):
        self.teencode_dict = {
            # Common Vietnamese teencode
            "ko": "không",
            "k": "không",
            "hok": "không",
            "hong": "không",
            "dc": "được",
            "đc": "được",
            "vs": "với",
            "v": "với",
            "nx": "nữa",
            "nz": "nữa",
            "j": "gì",
            "z": "gì",
            "mk": "mình",
            "m": "mày",
            "t": "tôi",
            "iu": "yêu",
            "ik": "đi",
            "r": "rồi",
            "bik": "biết",
            "bit": "biết",
            "lm": "làm",
            "lun": "luôn",
            "wa": "quá",
            "wá": "quá",
            "zui": "vui",
            "zay": "vậy",
            "ntn": "như thế nào",
            "sao": "sao",
            "thik": "thích",
            "uk": "ừ",
            "uh": "ừ",
            "uhm": "ừm",
            "hum": "hôm",
            "h": "giờ",
            "trc": "trước",
            "sau": "sau",
            "nay": "này",
            "kia": "kia",
            "đó": "đó",
            "đây": "đây"
        }
    
    def convert(self, text: str) -> str:
        """Convert teencode to standard Vietnamese"""
        words = text.lower().split()
        converted = []
        
        for word in words:
            if word in self.teencode_dict:
                converted.append(self.teencode_dict[word])
            else:
                converted.append(word)
        
        return " ".join(converted)
