import openai
from abc import ABC, abstractmethod
from importlib import import_module
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")


class OpenAIService(ABC):
    def __init__(self):
        self.model = "gpt-4"
        self.custom_functions = self.load_custom_functions()

    def load_custom_functions(self):
        custom_functions = {}
        functions_path = os.path.join(os.path.dirname(__file__), 'functions')
        for filename in os.listdir(functions_path):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = f"feature_service.openai_service.functions.{filename[:-3]}"
                module = import_module(module_name)
                custom_functions[filename[:-3]] = getattr(module, 'run')
        return custom_functions

    @abstractmethod
    def get_completion(self, prompt, section, previous_summary):
        pass

    @abstractmethod
    def summarize_section(self, content, section):
        pass

    def run_custom_function(self, function_name, *args, **kwargs):
        if function_name in self.custom_functions:
            return self.custom_functions[function_name](*args, **kwargs)
        raise ValueError(f"Custom function {function_name} not found.")


class GPTService(OpenAIService):
    def get_completion(self, prompt, section, previous_summary):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"{prompt}\n\n### Previous summary:\n{previous_summary}\n\nPlease provide the content for the {section}."}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"An error occurred: {e}"

    def summarize_section(self, content, section):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Please provide a concise summary for the following {section} section:\n{content}"}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"An error occurred: {e}"