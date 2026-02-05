🎙️ AI Audio / AI Sales Coach Backend

A FastAPI-powered backend for an AI-driven audio and sales coaching application.
This service integrates Groq LLMs, follows a clean service-based architecture, and is production-ready for deployment on Render. The frontend can be hosted on Vercel or Render Static Sites.

🚀 Features

FastAPI async backend

AI agent orchestration using Groq

Clean and modular project structure

Auto-generated API documentation

Secure environment variable handling

Render-ready deployment configuration

🧱 Tech Stack

Backend Framework: FastAPI
Server: Uvicorn
LLM Provider: Groq
Language: Python 3.11
Deployment: Render
Frontend: Vercel (recommended)
Config Management: pydantic-settings

📂 Project Structure

AI-audio/
│
├── backend/
│ ├── app/
│ │ ├── main.py # FastAPI entry point
│ │ ├── api/
│ │ │ └── routes.py # API routes
│ │ ├── services/
│ │ │ └── agent_service.py # AI agent logic
│ │ └── core/
│ │ └── config.py # Environment settings
│ │
│ ├── requirements.txt
│ ├── .env.example
│
├── infrastructure/
├── .gitignore
└── README.md

🛠️ Local Setup
Clone the repository

git clone https://github.com/Navadeep1817/AI-audio.git

cd AI-audio

Create and activate virtual environment

python -m venv .venv

Windows:
.venv\Scripts\activate

macOS / Linux:
source .venv/bin/activate

Install dependencies

pip install -r backend/requirements.txt

Environment variables

Create a .env file inside the backend/ directory:

GROQ_API_KEY=your_groq_api_key_here

Do NOT commit .env files to GitHub.

Run locally

uvicorn backend.app.main:app --reload

App runs at:
http://127.0.0.1:8000

Swagger Docs:
http://127.0.0.1:8000/docs

☁️ Deploy on Render
Render configuration

Service Type: Web Service
Runtime: Python 3.11

Build Command:
pip install -r backend/requirements.txt

Start Command:
uvicorn backend.app.main:app --host 0.0.0.0 --port 10000

Environment Variables (Render Dashboard)

GROQ_API_KEY=your_groq_api_key

🌐 Access After Deployment

Base URL:
https://<your-service-name>.onrender.com

Swagger Docs:
https://<your-service-name>.onrender.com/docs

🔗 Frontend Integration

For a Vite / React frontend, set:

VITE_API_URL=https://<your-service-name>.onrender.com

Example usage:

fetch(${import.meta.env.VITE_API_URL}/api/your-endpoint)

🔐 Security Best Practices

Never commit .env files

Use .env.example for reference

Store secrets in Render or Vercel environment variables

GitHub push protection enabled

🧪 Common Issues

Render shows “No open ports detected”
→ Ensure Uvicorn uses --host 0.0.0.0

Module not found error
→ Verify requirements.txt

Secrets blocked by GitHub
→ Remove .env from git history

405 Method Not Allowed on /
→ Add a root GET endpoint in FastAPI

📌 Future Enhancements

Real-time audio processing

Conversational memory for agents

Authentication (JWT / OAuth)

Usage analytics dashboard

Unit and integration testing
