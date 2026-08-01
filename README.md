# DEVFORGE Student Support AI Agent

FastAPI + LangGraph agent that answers student questions about DEVFORGE
internships, AI Engineering, Web Development, Python, FastAPI, LangChain,
LangGraph, GitHub, Render deployment, student tasks, certificates, and
technical project guidance. Unrelated questions get a polite refusal.

Uses **Ollama Cloud** (`https://ollama.com`) for the AI model itself — NOT
local Ollama — but the FastAPI server runs entirely on your own machine /
local network. No Render or any other hosting website is required.

✅ **Status: confirmed working** — tested end-to-end locally (both the
related-question path via Ollama Cloud and the unrelated-question refusal
path), using the model `gpt-oss:120b-cloud`.

## Workflow

```
Student sends a message
  -> FastAPI receives the request (/chat)
  -> LangGraph classify_node checks the message category
     -> related    -> Ollama Cloud AI model (gpt-oss:120b-cloud)
     -> unrelated  -> Safe support response
  -> FastAPI returns JSON response
  -> Your own PC hosts the API on the local network
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
├── render.yaml           # not needed for local hosting, safe to ignore/delete
├── .env.example
└── README.md
```

## 1. Get your Ollama Cloud API key

1. Go to https://ollama.com and sign in / sign up.
2. Open your account settings and create an API key.
3. **Not every cloud model is included on every plan.** Model pages on
   Ollama's site list a usage tier (e.g. "Low Usage", "Medium Usage") but
   don't guarantee it's included in your specific plan. `qwen3.5:cloud`,
   for example, returned a `"this model requires a subscription"` error on
   a Free-tier account, while `gpt-oss:120b-cloud` worked immediately with
   the same key. **Always confirm your model works with a direct test
   (Step 2b below) before wiring it into the app.**

## 2. Run on your machine (Windows / PowerShell)

```powershell
cd devforge-agent
python -m venv venv
venv\Scripts\Activate.ps1          # NOT "source" — that's bash/Mac only

pip install -r requirements.txt
```

> If `Activate.ps1` is blocked by execution policy, run this once:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

> **Anaconda users:** if you see errors mentioning
> `C:\Users\...\anaconda3\Lib\site-packages\...` in a traceback, your
> `venv` isn't actually active — you're still in the `(base)` Anaconda
> environment. Run `conda deactivate` first, then activate `venv` again,
> then reinstall: `pip install -r requirements.txt`.

### 2a. Set your environment variables (every new terminal needs this)

PowerShell variables (`$env:...`) only exist in the terminal window they
were set in — closing/reopening PowerShell, or opening a second window,
clears them. Set these **in the same terminal**, right before starting the
server:

```powershell
$env:OLLAMA_API_KEY = "paste-your-real-key-here"
$env:OLLAMA_CLOUD_URL = "https://ollama.com/api/chat"
$env:OLLAMA_MODEL = "gpt-oss:120b-cloud"
```

Sanity check it's actually set (should print your key back, not blank):
```powershell
$env:OLLAMA_API_KEY
```

**To avoid retyping these every session**, copy `.env.example` to `.env`,
fill in your real values, and they'll load automatically (the app already
uses `python-dotenv` for this) — see Step 2c.

### 2b. (Recommended) Test your key + model directly before running the app

This isolates "is my key/model valid?" from "is my app code working?":

```powershell
$headers = @{ "Authorization" = "Bearer $env:OLLAMA_API_KEY"; "Content-Type" = "application/json" }
$body = '{"model": "gpt-oss:120b-cloud", "messages": [{"role": "user", "content": "hello"}], "stream": false}'
Invoke-RestMethod -Uri "https://ollama.com/api/chat" -Method Post -Headers $headers -Body $body
```

- Response with real message content → key + model are good, proceed.
- `{"error":"Unauthorized"}` → your key is wrong/empty in this terminal, or
  you pasted placeholder text instead of your real key.
- `{"error":"this model requires a subscription..."}` → that specific
  model needs a paid plan; try a different cloud model (`gpt-oss:120b-cloud`
  is confirmed working on Free tier as of this writing).

### 2c. Start the server, bound to your local network

By default `--reload` binds only to `127.0.0.1` (your own PC). To make it
reachable from **other devices on the same Wi-Fi/LAN** (phone, another
laptop, a teammate's PC), bind to `0.0.0.0` and use a fixed port:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
<!-- http://127.0.0.1:8000/ui/ -->

You'll see `INFO: Application startup complete.` — **this is correct and
expected.** The server is now running and will occupy this terminal; it
will not return you to a prompt. Leave this window open.

### 2d. Find your PC's local IP address

In a **second** terminal:

```powershell
ipconfig
```

Look for **IPv4 Address** under your active adapter (Wi-Fi or Ethernet),
e.g. `192.168.1.25`. Other devices on the same network can now reach your
agent at:

```
http://192.168.1.25:8000
```

> **Windows Firewall:** the first time you run this, Windows may prompt to
> allow Python through the firewall for private networks — click **Allow**.
> If other devices still can't connect, check Windows Defender Firewall →
> Allow an app through firewall → make sure Python/uvicorn is allowed on
> **Private** networks.

### 2e. Test it

**From your own PC**, open `http://127.0.0.1:8000/docs` (or
`http://192.168.1.25:8000/docs` using your real IP) in your browser.

1. Click **POST /chat** → **Try it out**.
2. Enter a request body, e.g.:
   ```json
   { "message": "How do I deploy FastAPI on Render?" }
   ```
3. Click **Execute** and check the Response body.

**From another device on the same network** (e.g. your phone connected to
the same Wi-Fi), open a browser and go to:
```
http://192.168.1.25:8000/docs
```
(replace with your actual IP from Step 2d) and test `/chat` the same way.

A browser can only send GET requests, so visiting `/chat` directly (not
via `/docs`) gives `{"detail":"Method Not Allowed"}` — that's expected.

Confirmed test cases:

| Input message | Expected `category` | Expected `response` |
|---|---|---|
| "How do I deploy FastAPI on Render?" | `related` | Full AI-generated answer from Ollama Cloud |
| "What is the recipe for biryani?" | `unrelated` | Polite refusal message |

### 2f. (Alternative) Test via a second PowerShell terminal

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/chat -Method Post -ContentType "application/json" -Body '{"message": "How do I deploy FastAPI on Render?"}'
```

(Real `curl` syntax doesn't work as-is in PowerShell — `curl` there is
aliased to `Invoke-WebRequest` with different syntax — so use
`Invoke-RestMethod` instead.)

## 3. Keeping it running (local hosting notes)

Since there's no external host like Render, the agent is only reachable
while:
- Your PC is turned on and awake (disable sleep mode if others need to
  reach it over time),
- The `uvicorn` terminal window stays open,
- Your PC stays connected to the same network as the devices calling it.

If you close the terminal or your PC sleeps, the API goes offline until you
restart Step 2c. If you need it always-on regardless of your PC's state,
that requires an external host (like Render) — outside the scope of this
local setup.

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
Simple health check: `{"status": "ok"}`

## 5. Troubleshooting (issues encountered + fixes)

| Symptom | Cause | Fix |
|---|---|---|
| `source : command not found` | `source` is bash/Mac syntax | Use `venv\Scripts\Activate.ps1` on Windows |
| Server "hangs" at `Application startup complete` | Not a bug — that's the running server | Leave it running; open a **second** terminal or browser tab to send requests |
| `Invoke-RestMethod : Internal Server Error` (500) | An exception occurred server-side | Check the traceback printed in the uvicorn terminal for the real cause |
| `AttributeError: module 'langchain' has no attribute 'debug'` | Version mismatch, often from an Anaconda base env with an old `langchain` install | `conda deactivate`, activate `venv`, then `pip install --upgrade langchain langchain-core langgraph` |
| `{"detail":"Method Not Allowed"}` on `/chat` | Visiting a POST-only endpoint via plain browser GET | Use `/docs` Swagger UI, or send a real POST request |
| `401 Unauthorized` from Ollama Cloud | API key blank/wrong in this terminal, or literal placeholder text was sent instead of a real key | Re-set `$env:OLLAMA_API_KEY` (or `$headers`) in the **current** terminal with your real key; verify with `echo $env:OLLAMA_API_KEY` |
| `"this model requires a subscription"` | That specific cloud model isn't included in your plan | Test other models (e.g. `gpt-oss:120b-cloud`, `minimax-m2.5:cloud`, `kimi-k2.5:cloud`, `glm-5:cloud`) directly with `Invoke-RestMethod` until one succeeds |
| `uvicorn : not recognized` | Virtual environment isn't active in this terminal (prompt shows `PS ...` not `(venv) PS ...`) | Run `venv\Scripts\Activate.ps1` again |
| Env vars "disappear" between commands | PowerShell variables (`$env:...`, `$myKey`) only live in the terminal session they were set in | Re-set them every time you open a new terminal, or switch to a `.env` file loaded via `python-dotenv` |
| Other devices on Wi-Fi can't reach the API | Server bound to `127.0.0.1` only, or firewall blocking it | Use `--host 0.0.0.0`, allow Python through Windows Firewall on Private networks, confirm both devices are on the same network |

## Notes

- Never hardcode your `OLLAMA_API_KEY` in code — always use environment
  variables (`.env` file, loaded via `python-dotenv`).
- To widen or narrow allowed topics, edit `ALLOWED_KEYWORDS` in `app/graph.py`.
- To change the model, update `OLLAMA_MODEL` to any cloud model name
  available in your Ollama account — but confirm it works with a direct
  test first (see Step 2b), since not all listed models are included on
  every plan.
- `render.yaml` is left in the project in case you want to deploy publicly
  later, but it is not used for local/LAN hosting and can be safely ignored
  or deleted.

## Related questions (should route to Ollama Cloud)

## DEVFORGE / internship specific

"What is the DEVFORGE internship program about?"
"What tasks are usually assigned during a DEVFORGE internship?"
"How do I get my DEVFORGE certificate after finishing tasks?"

## AI Engineering / LangChain / LangGraph

"What's the difference between LangChain and LangGraph?"
"How do I add a conditional branch in LangGraph?"
"What is a StateGraph in LangGraph?"
"How do AI agents decide which tool to use?"

## Python / FastAPI

"What's the difference between a list and a tuple in Python?"
"How do I add request validation in FastAPI using Pydantic?"
"How do I handle errors properly in a FastAPI endpoint?"
"What is async/await used for in Python?"

## Web development

"What's the difference between frontend and backend development?"
"How does CORS work in a web app?"

GitHub / Render / deployment

"How do I push my project to GitHub for the first time?"
"What's the difference between git push and git pull?"
"How do environment variables work when deploying on Render?"

## Student tasks / project guidance

"How should I structure my Python project folders?"
"What should I include in my README file for a project submission?"
Unrelated questions (should get the polite refusal)
"What's the recipe for biryani?"
"Who won the cricket match yesterday?"
"Can you recommend a good movie?"
"What's the weather like today?"
