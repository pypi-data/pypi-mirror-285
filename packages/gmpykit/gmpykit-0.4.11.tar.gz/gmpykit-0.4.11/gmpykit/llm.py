import requests
import json

default_url = 'http://localhost:11434/api/generate'
default_llm_name = 'llama3'

def ask_llm(prompt, ollama_server_url='http://localhost:11434/api/generate', ollama_llm_name='llama3'):
    response = requests.post(ollama_server_url, json={'model': ollama_llm_name, 'prompt': prompt, 'option': {'temperature': 0}})
    text = response.text.strip()
    lines = text.split('\n')
    tokens = list(map(lambda line: json.loads(line)['response'], lines))
    formated = ''.join(tokens)
    answer = formated.strip()
    return answer
