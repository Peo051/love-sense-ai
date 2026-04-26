from typing import Optional, Dict

class ProfileContext:
    @staticmethod
    def build_context(user_profile: Optional[dict] = None) -> Dict:
        """Build context from user profile"""
        context = {}
        
        if user_profile:
            if "communication_style" in user_profile:
                context["communication_style"] = user_profile["communication_style"]
            if "age" in user_profile:
                context["age"] = user_profile["age"]
        
        return context
