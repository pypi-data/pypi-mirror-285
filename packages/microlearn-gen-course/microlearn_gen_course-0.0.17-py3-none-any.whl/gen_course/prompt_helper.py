from dataclasses import dataclass
import os
from typing import Optional
import promptlayer as pl
from regex import P


@dataclass
class PromptInfo:
    input_vars: list
    system_prompt: str
    user_prompt: str


class PromptHelper:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PromptHelper, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self, pl_api_key: str = None):
        pl.api_key = pl_api_key or os.getenv('PROMPTLAYER_API_KEY')
    
    def get_prompt(self, prompt_name:str, lang:Optional[str]):
        if lang and lang != "en":
            prompt_name = f"{prompt_name}_{lang}"
        template = pl.templates.get(prompt_name, params={"label": "prod"})
        input_vars = template["prompt_template"]["input_variables"]
        system_prompt = None
        user_prompt = None
        for message in template["prompt_template"]["messages"]:
            if message["role"] == "system":
                system_prompt = message["content"][0]["text"]
            elif message["role"] == "user":
                user_prompt = message["content"][0]["text"]
        
        return PromptInfo(input_vars, system_prompt, user_prompt)
