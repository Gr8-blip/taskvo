# 🧠 TaskVO – AI-Powered Productivity Assistant

TaskVO is your MCP-powered (Model Context Protocol) productivity tool that leverages OpenRouter AI to transform natural language into actionable tasks. Whether you're juggling work deadlines, personal errands, or random ideas, TaskVO interprets your words and turns them into structured, manageable to-dos—all while keeping you motivated and organized.

Built on Django for a robust backend, it now includes seamless Google OAuth for quick logins and Celery for automated task reminders. This means no more forgotten deadlines; TaskVO nudges you via email when things are due. It's a complete, self-contained package that's easy to set up and infinitely extensible. 🎯🚀

## ⚙️ Features

✅ **User Authentication**: Secure register/login via email, plus one-click Google OAuth for effortless access.  
✅ **Daily Motivational Quotes**: Pulled fresh from the ZenQuotes API to kickstart your day with inspiration.  
✅ **Task Management**: Add, complete, delete, and categorize tasks (e.g., Work, Personal, Other) with due dates and priorities.  
✅ **AI Assistant**: Powered by OpenRouter (using models like Mistral or Nous Hermes) to parse natural language into JSON commands.  
✅ **Friendly Fallbacks**: Non-task messages get witty, helpful JSON responses instead of errors.  
✅ **Automated Reminders**: Celery handles background task scheduling, sending daily email alerts for due items.  
✅ **Modern UI**: Sleek design with Tailwind CSS, FontAwesome icons, and a floating chat-style assistant popup for on-the-fly interactions.  
✅ **Extensible Architecture**: Easy to customize rules, add more integrations, or scale for teams.

## 🚀 Getting Started

Ready to dive in? Follow these steps to get TaskVO running locally in minutes. We've kept it simple, but with pro tips for troubleshooting.

### 1. Clone the Repository

```bash
git clone https://github.com/Gr8-blip/taskvo
cd taskvo
```

### 2. Set up a Virtual Environment

Isolate your dependencies like a pro:

```bash
python -m venv venv
# Activate it:
venv\Scripts\activate  # On Windows
# OR
source venv/bin/activate  # On Mac/Linux
```

**Pro Tip**: If you're on Python 3.12+, this ensures compatibility with all libraries.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This pulls in Django, Celery, Redis, Django-AllAuth for Google Auth, and more. If you hit version conflicts, try `pip install --upgrade pip` first.

### 4. Configure Environment Variables

Create a `.env` file in the backend directory (or root if specified in your settings). This keeps sensitive info secure and out of your codebase.

```env
# AI Integration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Google OAuth (for social login)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Email Setup (for Celery reminders)
EMAIL_HOST_USER=youremail@gmail.com
EMAIL_HOST_PASSWORD=your_app_password_here  # Use Gmail App Password for security
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Django Secret Key (generate a strong one!)
SECRET_KEY=your_django_secret_key_here  # Run: python -c "import secrets; print(secrets.token_urlsafe(50))"

# Celery Broker (Redis URL)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

🔑 **OpenRouter API Key**: Sign up for free at [openrouter.ai](https://openrouter.ai) and grab your key from the dashboard.  
🔑 **Google Client ID/Secret**: Head to [Google Cloud Console](https://console.cloud.google.com), create an OAuth 2.0 Client ID for web apps, and add authorized redirect URIs (see Google Auth section below).  
🔑 **Gmail App Password**: If using Gmail, generate one [here](https://myaccount.google.com/apppasswords) to avoid 2FA issues.  

**Pro Tip**: Use a tool like `python-decouple` if you want to load these vars more flexibly in production.

### 5. Run Migrations and Start the Server

Apply database schema changes:

```bash
python manage.py migrate
```

Then fire it up:

```bash
python manage.py runserver
```

Head to 👉 **http://127.0.0.1:8000** in your browser. Boom—you're in!

If you see errors, check your `.env` file or console logs for clues (e.g., missing keys).

## 🔑 Google Authentication Setup & How It Works

TaskVO uses Django-AllAuth for handling authentication, making Google OAuth integration plug-and-play. This lets users log in with their Google account in seconds, skipping traditional email/password hassles. It's secure, reduces friction, and ties into Google's ecosystem for profile data.

### Step-by-Step Setup

1. **Create Google Credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com).
   - Enable the "Google+ API" (legacy but required for AllAuth) or "People API" if prompted.
   - Under **APIs & Services > Credentials**, create an **OAuth 2.0 Client ID** (select "Web application").
   - Set **Authorized JavaScript origins**: `http://127.0.0.1:8000` (local) or your domain.
   - Set **Authorized redirect URIs**:
     - Local: `http://127.0.0.1:8000/accounts/google/login/callback/`
     - Production (e.g., on Render): `https://your-domain.com/accounts/google/login/callback/`

2. **Copy Credentials**: Paste the Client ID and Secret into your `.env` file.

3. **Configure in Django**:
   - In `settings.py`, AllAuth is already set up with `SOCIALACCOUNT_PROVIDERS` for Google.
   - Run migrations if needed: `python manage.py migrate`.

### How It Works Under the Hood:

- When a user clicks "Login with Google," they're redirected to Google's auth page.
- Google verifies and sends back an access token.
- AllAuth handles the callback, creates/links a user account, and logs them in.
- **Benefits**: No password management, auto-fills user info (email, name), and enhances security with OAuth2 protocols.
- **Edge Cases**: If a user already has an email account, AllAuth can merge them—check docs for custom behaviors.

**Test it**: On the login page, click the Google button. If it fails, double-check URIs and enable "Less secure app access" if using older Gmail settings (but prefer App Passwords).

## ⏰ Celery Setup (Automated Task Reminders) & How It Works

Celery is a distributed task queue that runs background jobs asynchronously—perfect for TaskVO's daily reminders without blocking the main app. It uses Redis as a broker to store and manage tasks, ensuring reliability even if your server restarts.

This setup sends email reminders for tasks due today, running automatically every morning. It's scalable: Add more workers for heavier loads or complex schedules.

### Step-by-Step Setup

1. **Install Redis** (the message broker):
   - **Mac**: `brew install redis`
   - **Linux**: `sudo apt-get install redis-server`
   - **Windows**: Download from [Microsoft's Redis archive](https://github.com/microsoftarchive/redis/releases) or use WSL.
   - **Verify**: Run `redis-cli ping`—should respond "PONG".

2. **Start Redis**:
   ```bash
   redis-server
   ```
   (Run in background: `redis-server &` or use a service manager.)

3. **Start Celery Workers**:
   - In a new terminal (for processing tasks):
     ```bash
     celery -A taskvo worker -l info
     ```
   - In another terminal (for scheduled beats):
     ```bash
     celery -A taskvo beat -l info
     ```

### How It Works Under the Hood:

- **Task Definition**: In `tasks.py`, we define functions like `send_reminder_emails()` which queries due tasks and emails users.
- **Scheduling**: Configured in `settings.py` under `CELERY_BEAT_SCHEDULE`. Example: Runs `send_reminder_emails` daily at 7:00 AM UTC via a cron-like schedule (`schedule=crontab(hour=7, minute=0)`).
- **Broker Flow**: When a task is triggered (e.g., by the beat scheduler), Celery pushes it to Redis. Workers pull from the queue, execute, and store results back in Redis.
- **Email Integration**: Uses Django's `send_mail()` with your Gmail creds. Reminders include task details like title, due date, and a link back to the app.
- **Benefits**: Offloads heavy work (e.g., querying DB, sending emails) from the web server, preventing slowdowns. Scalable to cloud (e.g., Redis Labs) for production.
- **Customization**: Edit `CELERY_BEAT_SCHEDULE` for different times or add tasks like weekly summaries. Monitor with `celery -A taskvo events` or Flower dashboard.

**Pro Tip**: In production, use `supervisor` or `systemd` to daemonize workers. For testing, trigger tasks manually: `from tasks import send_reminder_emails; send_reminder_emails.delay()` in a Django shell.

## 🧠 AI Assistant Behavior

The AI is the brain of TaskVO, guided by rules in `rules.txt` for strict JSON outputs. It injects context dynamically to stay focused on tasks.

### ✨ Task Example:
**Input**: `Remind me to submit homework tomorrow`  
**Output**:
```json
{
  "command": "add",
  "title": "Submit homework",
  "due": "tomorrow"
}
```
The app parses this to create a task with parsed due date (e.g., tomorrow = current date +1).

### 😎 Non-Task Example:
**Input**: `Yo wassup?! Can you code? What's your name?`  
**Output**:
```json
{
  "command": "none",
  "message": "I'm TaskVO's assistant! Try something like: 'Remind me to drink water today 💧'"
}
```

**How It Works**: OpenRouter API receives your message + `rules.txt` as system prompt. Models like Mistral ensure JSON compliance. Tweak `rules.txt` for new behaviors without code changes.

## 🌐 Tech Stack

- 🧩 **Backend**: Django + SQLite (easy swap to Postgres for scale)
- 🎨 **Frontend**: HTML, Tailwind CSS, JavaScript for dynamic UIs
- 🖼 **Icons**: FontAwesome for that polished look
- 🧠 **AI**: OpenRouter API (Mistral / Nous Hermes models)
- 📜 **Quotes**: ZenQuotes.io API
- 🟢 **Async Tasks**: Celery + Redis for reminders and background jobs
- 🔑 **Auth**: Django-AllAuth for Google OAuth and social logins

## 👨‍🚀 Author

Built by **Great** — a 13-year-old full-stack innovator crafting AI, web apps, and space-age tech from the future 🚀  
[GitHub](https://github.com/Gr8-blip) · [X (Twitter)](https://twitter.com/yourhandle) · [LinkedIn](https://linkedin.com/in/yourprofile)

---
