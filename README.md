# 🚀 AI Email Agent — Automated Gmail Classifier & Auto-Reply System

An intelligent email automation backend built using **Django**, **LangGraph**, **OpenAI**, **Gmail API**, **Celery**, and **Redis**.

This agent automatically:

- ✔️ Syncs emails from Gmail  
- ✔️ Classifies intent using AI  
- ✔️ Generates professional auto-replies  
- ✔️ Saves replies directly as Gmail Drafts  
- ✔️ Stores all metadata in the database  
- ✔️ Exposes APIs for a Next.js dashboard  

---

## 📂 Project Structure

backend/
│── accounts/ # Gmail OAuth, token storage
│── emails/ # Email sync + AI pipeline + LLM tools
│ ├── langgraph/
│ │ ├── nodes/ # Agent nodes
│ │ ├── reply_graph.py
│ │ └── full_agent_graph.py
│ ├── services.py # Gmail API wrappers
│ ├── tasks.py # Celery background jobs
│── backend/
│ ├── settings.py
│ ├── celery.py
│── manage.py
│── .env # NOT committed
│── requirements.txt

markdown
Copy code

---

## ⚙️ Features

### ⭐ 1. Gmail OAuth Login
Users authenticate and authorize Gmail access.

### ⭐ 2. Gmail Email Sync
A Celery task fetches and saves emails in the database.

### ⭐ 3. AI Intent Classification  
Classifies emails into:

- meeting  
- billing  
- complaint  
- follow-up  
- inquiry  
- marketing  
- personal  
- spam  
- task  

### ⭐ 4. Auto-Reply Generation
The LangGraph pipeline handles:

1. Cleaning email  
2. Understanding intent  
3. GPT reply generation  
4. HTML formatting  
5. Creating Gmail draft  
6. Saving in EmailMessage row  

### ⭐ 5. REST API (Frontend Ready)

GET /emails/list/
GET /emails/detail/<id>/
POST /emails/agent/reply/<id>/
POST /emails/agent/full/
GET /emails/sync/

yaml
Copy code

---

## 🛠 Tech Stack

### Backend
- Django REST Framework  
- LangGraph  
- OpenAI API  
- Gmail API  
- Celery  
- Redis  
- SQLite/PostgreSQL  

### Frontend (not included)
- Next.js  
- TailwindCSS  

---

## 🔧 Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/narsi-2208/ai-email-agent-backend.git
cd ai-email-agent-backend/backend
2️⃣ Create environment
bash
Copy code
conda create -n aiagent python=3.10
conda activate aiagent
3️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Create .env file
ini
Copy code
DJANGO_SECRET_KEY=your-secret
DEBUG=True

GOOGLE_CLIENT_ID=xxxx
GOOGLE_CLIENT_SECRET=xxxx
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/accounts/google/callback/

OPENAI_API_KEY=sk-xxxxx

REDIS_URL=redis://localhost:6379/0
5️⃣ Run migrations
bash
Copy code
python manage.py migrate
6️⃣ Start Redis
bash
Copy code
redis-server
7️⃣ Start Celery Worker
bash
Copy code
celery -A backend worker -l info -P solo
8️⃣ Start Celery Beat
bash
Copy code
celery -A backend beat -l info
9️⃣ Start Django backend
bash
Copy code
python manage.py runserver
⚡ How the AI Agent Works (Flow)
mathematica
Copy code
Gmail Sync → Intent Classification → Reply Generation
         → Format HTML → Save Gmail Draft → Save in DB
📌 API Endpoints
Email List
bash
Copy code
GET /emails/list/
Email Detail
bash
Copy code
GET /emails/detail/<id>/
Run Reply Agent
bash
Copy code
POST /emails/agent/reply/<id>/
Run Full Inbox Agent
swift
Copy code
POST /emails/agent/full/
Sync Emails
bash
Copy code
GET /emails/sync/
🚨 Important Notes
Do NOT commit:
.env

db.sqlite3

celerybeat-schedule*

__pycache__/

virtual environments

OAuth tokens

API keys

Your .gitignore already covers these.
