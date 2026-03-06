"""
LitPilot Backend — FastAPI + AgentOS Server

Custom API routes for the Vue.js frontend:
  POST /api/infer-intent   — run two-stage intent decomposition
  POST /api/execute         — run executor agent (SSE stream)
  GET  /api/health          — health check
"""

from agno.os import AgentOS
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from agents.intent import (
    text_summarizer_agent, vision_summarizer_agent,
    aggregator_mistral, aggregator_gpt, aggregator_gemini,
    consensus_agent
)
from agents.executor import executor_agent
from agents.knowledge import knowledge_agent

# Ensure all agents have string IDs for the API routing
text_summarizer_agent.id = "text-summarizer"
vision_summarizer_agent.id = "vision-summarizer"
aggregator_mistral.id = "aggregator-mistral"
aggregator_gpt.id = "aggregator-gpt"
aggregator_gemini.id = "aggregator-gemini"
consensus_agent.id = "intent-consensus"
executor_agent.id = "litpilot-executor"
knowledge_agent.id = "research-librarian"

agent_os = AgentOS(
    agents=[
        text_summarizer_agent,
        vision_summarizer_agent,
        aggregator_mistral,
        aggregator_gpt,
        aggregator_gemini,
        consensus_agent,
        executor_agent,
        knowledge_agent
    ]
)

app = agent_os.get_app()

# CORS — allow Vue dev server to communicate with the AgentOS API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=7777, reload=True)
