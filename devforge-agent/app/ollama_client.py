"""
Ollama Cloud client.

IMPORTANT: This connects to Ollama CLOUD (https://ollama.com), NOT a local
Ollama instance. Render (or any remote host) cannot reach a laptop's
localhost:11434, so all requests go to the cloud endpoint using your
OLLAMA_API_KEY.
"""

import os
import requests

OLLAMA_CLOUD_URL = os.getenv("OLLAMA_CLOUD_URL", "https://ollama.com/api/chat")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:cloud")

SYSTEM_PROMPT = """You are DEVFORGE Student Support AI Agent.

You ONLY help students with:
- DEVFORGE internships
- AI Engineering
- Web Development
- Python
- FastAPI
- LangChain
- LangGraph
- GitHub
- Render deployment
- Student tasks
- Certificates
- Technical project guidance

Answer clearly, politely, and helpfully, with practical steps or code
examples when useful. Keep answers focused on the student's question.
"""


def ask_ollama_cloud(user_message: str) -> str:
    """Send a chat request to Ollama Cloud and return the model's reply."""
    if not OLLAMA_API_KEY:
        return (
            "Server configuration error: OLLAMA_API_KEY is not set. "
            "Please contact the DEVFORGE admin."
        )

    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_CLOUD_URL, headers=headers, json=payload, timeout=60
        )
        response.raise_for_status()
        data = response.json()

        # Ollama /api/chat response shape: {"message": {"role": "...", "content": "..."}}
        if "message" in data and "content" in data["message"]:
            return data["message"]["content"].strip()

        # Fallback for OpenAI-compatible shape if you switch endpoints
        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()

        return "Sorry, I could not parse a response from the AI model."

    except requests.exceptions.RequestException as e:
        return f"Sorry, I couldn't reach the AI model right now. Error: {e}"
