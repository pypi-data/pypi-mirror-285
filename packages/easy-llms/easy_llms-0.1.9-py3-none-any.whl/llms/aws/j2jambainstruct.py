# j2jambainstruct.py
from .aws import AWS

class J2JambaInstruct(AWS):
    name = "j2_jamba_instruct"
    model = "ai21.jamba-instruct-v1:0"  # Override class variable
    chat = False # NOTE: A21 J2 does NOT support Chat

    def __init__(self, temperature=0.2, max_tokens=4096, **model_kwargs):
        super().__init__(**model_kwargs)

        self.model_kwargs = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            **model_kwargs
        }

        # Override AUTHENTICATION per Model
        try:
            self.auth(self.__class__.name.lower())
        except Exception as e:
            print(f"Error during authentication: {e}")

        try:
            self.updateLLM(self.chat)
        except Exception as e:
            print(f"Error updating LLM in {self.__class__.__name__}: {e}")

