import json
import os

MEMORY_FILE = "ai_memory.json"

def load_memory(user_id, max_messages=None):
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    history = data.get(user_id, [])
    return history if max_messages is None else history[-max_messages:]

def is_task_query(message):
    keywords = ["last task", "recent task", "previous task", "what did i add", "last thing", "most recent"]
    return any(keyword in message.lower() for keyword in keywords)

def is_prompt_query(message):
    keywords = ["last prompt", "what did i say", "previous command", "last command", "last 3 prompts", "recent prompts", "chat history", "all prompts"]
    return any(keyword in message.lower() for keyword in keywords)

def get_last_task(user_id, count=1):
    history = load_memory(user_id, max_messages=10)
    tasks = []
    for i in range(len(history) - 1, -1, -2):
        try:
            ai_response = json.loads(history[i]["message"])
            if ai_response["command"] == "add" and "title" in ai_response:
                tasks.append((ai_response["title"], ai_response["due"]))
            elif ai_response["command"] == "add-multiple" and ai_response["tasks"]:
                tasks.extend((task["title"], task["due"]) for task in ai_response["tasks"][::-1])
            if len(tasks) >= count:
                break
        except:
            continue
    return tasks[-count:] if tasks else []

def get_last_prompts(user_id, count="all"):
    history = load_memory(user_id, max_messages=None if count == "all" else count * 2)
    prompts = [h["message"] for h in history if h["role"] == "user"]
    return prompts if count == "all" else prompts[-count:] if prompts else []

def save_memory(user_id, user_msg, ai_msg):
    if not os.path.exists(MEMORY_FILE):
        data = {}
    else:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
    history = data.get(user_id, [])
    history.append({"role": "user", "message": user_msg})
    history.append({"role": "ai", "message": ai_msg})
    history = history[-10:]
    data[user_id] = history
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)