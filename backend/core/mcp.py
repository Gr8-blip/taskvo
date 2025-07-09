import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

with open("core/rules.txt", encoding="utf-8") as f:
    behavior = f.read()
    

def ai_response(user_message):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://127.0.0.1:8000/dashboard/",  # or your dev domain
        "X-Title": "TaskVO MCP Agent",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mixtral-8x7b-instruct", 
        "messages": [
            {"role": "system", "content": f"{behavior}"},
            {"role": "user", "content": f"{user_message}"}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        try:
            data = response.json()
            if 'choices' in data and data['choices']:
                return data['choices'][0]['message']['content']
            else:
                return '{"command": "none", "message": "Oops! No valid response from AI."}'
        except Exception as e:
            return f'{{"command": "none", "message": "Error parsing AI response: {str(e)}"}}'
    else:
        return f'{{"command": "none", "message": "Request failed with status code {response.status_code}"}}'