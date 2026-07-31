# DEVFORGE Student Support AI Agent

FastAPI + LangGraph agent that answers student questions about DEVFORGE
internships, AI Engineering, Web Development, Python, FastAPI, LangChain,
LangGraph, GitHub, Render deployment, student tasks, certificates, and
technical project guidance. Unrelated questions get a polite refusal.

Uses **Ollama Cloud** (`https://ollama.com`) — NOT local Ollama — so it works
correctly once deployed on Render.

## Workflow

```
Student sends a message
  -> FastAPI receives the request (/chat)
  -> LangGraph classify_node checks the message category
     -> related    -> Ollama Cloud AI model (qwen3.5:cloud)
     -> unrelated  -> Safe support response
  -> FastAPI returns JSON response
  -> Render hosts the API publicly
```

## Project structure

```
devforge-agent/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, /chat endpoint
│   ├── graph.py         # LangGraph classify + route logic
│   └── ollama_client.py # Ollama Cloud HTTP client
├── requirements.txt
├── render.yaml
├── .env.example
└── README.md
```

## 1. Get your Ollama Cloud API key

1. Go to https://ollama.com and sign in / sign up.
2. Open your account settings and create an API key.
3. Confirm you have access to a cloud model (e.g. `qwen3.5:cloud`) — check
   your Ollama account's model list and use the exact cloud model name shown
   there.

## 2. Run locally

```bash
cd devforge-agent
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your real OLLAMA_API_KEY

# load env vars (bash example)
export $(grep -v '^#' .env | xargs)

uvicorn app.main:app --reload
```

Test it:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I deploy a FastAPI app on Render?"}'
```

Unrelated example:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the recipe for biryani?"}'
```

## 3. Deploy to Render

1. Push this project to a GitHub repository.
2. In Render, click **New +** → **Web Service** → connect your GitHub repo.
3. Render will detect `render.yaml` automatically (Blueprint), or set manually:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in Render's dashboard:
   - `OLLAMA_API_KEY` = your real Ollama Cloud key (mark as secret)
   - `OLLAMA_CLOUD_URL` = `https://ollama.com/api/chat`
   - `OLLAMA_MODEL` = `qwen3.5:cloud` (or your available cloud model)
5. Click **Deploy**. Once live, your endpoint will be:
   `https://<your-service-name>.onrender.com/chat`

## 4. API reference

### `POST /chat`
Request body:
```json
{ "message": "How do I use LangGraph with FastAPI?" }
```

Response body:
```json
{
  "message": "How do I use LangGraph with FastAPI?",
  "category": "related",
  "response": "Here's how you can integrate LangGraph with FastAPI..."
}
```

### `GET /health`
Simple health check for uptime monitors: `{"status": "ok"}`

## Notes

- Never hardcode your `OLLAMA_API_KEY` in code — always use environment
  variables (`.env` locally, Render's env var dashboard in production).
- To widen or narrow allowed topics, edit `ALLOWED_KEYWORDS` in `app/graph.py`.
- To change the model, update `OLLAMA_MODEL` to any cloud model name
  available in your Ollama account.
