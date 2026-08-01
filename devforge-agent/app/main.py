from dotenv import load_dotenv

load_dotenv()  # loads OLLAMA_API_KEY etc. from a local .env file, if present

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.graph import run_agent

app = FastAPI(
    title="DEVFORGE Student Support AI Agent",
    description="AI agent for DEVFORGE internships, AI Engineering, Web Dev, "
    "Python, FastAPI, LangChain, LangGraph, GitHub, Render, tasks & certificates.",
    version="1.0.0",
)

# Allow requests from any frontend (adjust in production if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str
    category: str
    response: str


@app.get("/")
def root():
    return {
        "status": "online",
        "agent": "DEVFORGE Student Support AI Agent",
        "usage": "POST /chat with JSON body {\"message\": \"your question\"}. "
        "Or open /ui in your browser for a chat page.",
    }


# Serve the simple chat frontend at /ui (e.g. http://127.0.0.1:8000/ui)
_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/ui", StaticFiles(directory=_frontend_dir, html=True), name="ui")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = run_agent(request.message)
    return result
