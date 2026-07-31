"""
LangGraph workflow for DEVFORGE Student Support AI Agent.

Flow:
  Student message
    -> classify_node   (decide: related / unrelated)
    -> related    -> ollama_node   (Ollama Cloud model answers)
    -> unrelated  -> safe_response_node (polite refusal)
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

from app.ollama_client import ask_ollama_cloud

# ---------------------------------------------------------------------
# Topics DEVFORGE agent is allowed to answer
# ---------------------------------------------------------------------
ALLOWED_KEYWORDS = [
    "devforge",
    "internship",
    "intern",
    "ai engineering",
    "artificial intelligence",
    "machine learning",
    "ml",
    "deep learning",
    "web development",
    "web dev",
    "html",
    "css",
    "javascript",
    "react",
    "node",
    "python",
    "fastapi",
    "flask",
    "django",
    "langchain",
    "langgraph",
    "github",
    "git ",
    "render",
    "deploy",
    "deployment",
    "task",
    "assignment",
    "certificate",
    "certification",
    "project",
    "api",
    "backend",
    "frontend",
    "database",
    "sql",
    "docker",
    "code",
    "coding",
    "programming",
    "debug",
    "error",
    "llm",
    "ollama",
    "agent",
    "chatbot",
]

SAFE_RESPONSE = (
    "I'm the DEVFORGE Student Support AI Agent, and I can only help with "
    "DEVFORGE internships, AI Engineering, Web Development, Python, FastAPI, "
    "LangChain, LangGraph, GitHub, Render deployment, student tasks, "
    "certificates, and technical project guidance. "
    "Could you please rephrase your question around one of these topics?"
)


class AgentState(TypedDict):
    message: str
    category: str
    response: str


def classify_node(state: AgentState) -> AgentState:
    """Decide whether the message is related to DEVFORGE support topics."""
    text = state["message"].lower()
    is_related = any(keyword in text for keyword in ALLOWED_KEYWORDS)
    state["category"] = "related" if is_related else "unrelated"
    return state


def route_after_classify(state: AgentState) -> Literal["related", "unrelated"]:
    return "related" if state["category"] == "related" else "unrelated"


def ollama_node(state: AgentState) -> AgentState:
    """Related question -> Ollama Cloud AI model."""
    state["response"] = ask_ollama_cloud(state["message"])
    return state


def safe_response_node(state: AgentState) -> AgentState:
    """Unrelated question -> Safe support response."""
    state["response"] = SAFE_RESPONSE
    return state


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("classify", classify_node)
    workflow.add_node("ollama_node", ollama_node)
    workflow.add_node("safe_response_node", safe_response_node)

    workflow.set_entry_point("classify")

    workflow.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "related": "ollama_node",
            "unrelated": "safe_response_node",
        },
    )

    workflow.add_edge("ollama_node", END)
    workflow.add_edge("safe_response_node", END)

    return workflow.compile()


# Compiled graph, reused across requests
agent_graph = build_graph()


def run_agent(message: str) -> dict:
    result = agent_graph.invoke({"message": message, "category": "", "response": ""})
    return {
        "message": message,
        "category": result["category"],
        "response": result["response"],
    }
