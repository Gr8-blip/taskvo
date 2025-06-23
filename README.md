# 🧠 TaskVO – AI-Powered Productivity Assistant

TaskVO is your **MCP-powered (Model Context Protocol)** productivity tool that uses **OpenRouter AI** to turn natural language into actionable tasks.

It's built with **Django**, supports user authentication, task management, motivational quotes, and a JSON-speaking AI assistant that turns text into structured commands.  
All in one tidy package. 🎯

---

## ⚙️ Features

- ✅ User Authentication (Register/Login)
- ✅ Daily Motivational Quotes from ZenQuotes API
- ✅ Add, complete, and delete tasks
- ✅ Task categories (Work, Personal, Other, etc.)
- ✅ 🧠 AI Assistant powered by OpenRouter (Mistral / Nous Hermes)
- ✅ Friendly fallback JSON response for non-task messages
- ✅ Sleek, modern UI using Tailwind CSS and FontAwesome icons
- ✅ Floating Assistant button (chat-style popup)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Gr8-blip/taskvo
cd taskvo
```

### 2. Set up a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# OR
source venv/bin/activate  # On Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the `backend` directory:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```
> 🔑 Get your free API key from [https://openrouter.ai](https://openrouter.ai)
---

### 5. Run the App

```bash
python manage.py migrate
python manage.py runserver
```

Visit the app at 👉 `http://127.0.0.1:8000`

---

## 🧠 AI Assistant Behavior

The AI lives inside `rules.txt` and follows strict JSON rules.

### ✨ If you say:

```
Remind me to submit homework tomorrow
```

It responds:

```json
{
  "command": "add",
  "title": "Submit homework",
  "due": "tomorrow"
}
```

---

### 😎 If you say:

```
Yo wassup?!
Can you code?
What’s your name?
```

It responds with friendly fallback JSON:

```json
{
  "command": "none",
  "message": "I’m TaskVO’s assistant! Try something like: 'Remind me to drink water today 💧'"
}
```

> ✅ Rules are injected dynamically from `rules.txt` to guide the AI's behavior.

---

## 🌐 Tech Stack

* 🧩 Django + SQLite
* 🎨 HTML + TailwindCSS + JS
* 🖼 FontAwesome for icons
* 🧠 OpenRouter AI API (Mistral / Nous Hermes)
* 📜 ZenQuotes.io for motivational quotes

---

## 👨‍🚀 Author

Built by **Great** — a 13-year-old full-stack innovator building AI, web apps, and space-age tech from the future 🚀
[GitHub](https://github.com/Gr8-blip) · [X (Twitter)](https://x.com/GreatTheCoder) · [LinkedIn](https://www.linkedin.com/in/great-uvomata-411aab327/)
