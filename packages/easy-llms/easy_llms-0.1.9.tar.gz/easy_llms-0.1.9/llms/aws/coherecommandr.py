# coherecommandr.py
from .aws import AWS
import sys
from langchain_core.prompts import PromptTemplate

class CohereCommandR(AWS):
    name = "cohere_command_r"
    model = "cohere.command-r-v1:0"  # Override class variable
    chat = False # NOTE: Cohere Command does NOT support Chat

    def __init__(self, temperature=0.2, max_tokens=4096, **model_kwargs):
        super().__init__(**model_kwargs)

        self.model_kwargs = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            **model_kwargs
        }

        # Override - Cohere Command R requires a different input template
        try:
            system_message = "You are a helpful assistant. Answer all questions to the best of your ability.\n{question}"
            self.prompt_template = PromptTemplate(
                input_variables=["question"], 
                template=system_message
            )
        except Exception as e:
            print(f"Error initializing prompt template: {e}")
            sys.exit(1)


        # Override AUTHENTICATION per Model
        try:
            self.auth(self.__class__.name.lower())
        except Exception as e:
            print(f"Error during authentication: {e}")


        try:
            self.updateLLM(self.chat)
        except Exception as e:
            print(f"Error updating LLM in {self.__class__.__name__}: {e}")


    # Override - Cohere Command R requires a different input template
    def run(self, prompt):
        print("OVERRIDE!")
        print(self.chain)
        try:
            response = self.chain.invoke(prompt)
            return response
        except Exception as e:
            print(f"Error invoking the chain: {e}")
            return None

