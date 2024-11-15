from openai import api_key
from pandasai import Agent
import os
import json
with open('api_key.json', 'r') as secret_key:
    API_KEY = json.load(secret_key)['api_key']
    os.environ["PANDASAI_API_KEY"] = API_KEY

def sanitize_input(text):
    # Remove ou substitua caracteres potencialmente sensíveis
    return text.replace("os", "").replace("io", "").replace("b64decode", "").strip("?")

def return_response(dataframe, prompt):
    agent = Agent(dataframe)
    return agent.chat(prompt)