import google.generativeai as genai
from config import GEMINI_API_KEY


class AIService:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = self._load_working_model()

    def _load_working_model(self):
        """
        Automatically find a Gemini model that supports generateContent
        in the current installed package / API account.
        """
        try:
            available_models = genai.list_models()

            preferred_models = [
                "models/gemini-1.5-flash",
                "models/gemini-1.5-flash-latest",
                "models/gemini-1.5-pro",
                "models/gemini-pro"
            ]

            supported_model_names = []

            for m in available_models:
                # only models that support generateContent
                if "generateContent" in m.supported_generation_methods:
                    supported_model_names.append(m.name)

            # first try preferred list
            for model_name in preferred_models:
                if model_name in supported_model_names:
                    return genai.GenerativeModel(model_name)

            # otherwise use first supported model
            if supported_model_names:
                return genai.GenerativeModel(supported_model_names[0])

            raise Exception("No Gemini model with generateContent support was found.")

        except Exception as e:
            raise Exception(f"Model loading failed: {str(e)}")

    def ask_ai(self, user_prompt):
        try:
            prompt = f"""
You are Jarvis, a smart, helpful, professional AI voice assistant.
Answer the user clearly, naturally, and in a concise way.
If possible, keep answers beginner-friendly.

User question:
{user_prompt}
"""
            response = self.model.generate_content(prompt)

            if response and hasattr(response, "text") and response.text:
                return {
                    "success": True,
                    "response_text": response.text.strip()
                }
            else:
                return {
                    "success": False,
                    "response_text": "Sorry, I could not generate an AI response right now."
                }

        except Exception as e:
            return {
                "success": False,
                "response_text": f"AI error: {str(e)}"
            }
