# LitPilot: Autonomous Research Agent for Literature Reviews

**TinyFish $2M Pre-Accelerator Hackathon 2026 Entry**  
**Builder:** Ash(win) — @noob_contrarian (solo)  
**Hack Period:** Feb 25 – Mar 29, 2026 (original work during hack; deadline Mar 29, 2026 11:59 PM IST)  
**Core Tech:** TinyFish Web Agent API + decomposed intent extraction from EMNLP 2025 paper

## Overview
LitPilot is a web-based AI agent that takes your short text description (or optional screenshots) of a partial research session, uses a decomposed two-stage method to accurately infer your high-level goal, then autonomously completes the literature review on live web sites via TinyFish — turning hours of manual work into minutes.

Just describe your start (e.g., "Searched Scholar for X, opened PDF, highlighted methods"), review the inferred intent, and watch the agent execute.

## The Problem
Researchers, PhD students, analysts, and R&D teams burn 10–20+ hours per lit review: searching Scholar/arXiv/Semantic Scholar, handling pagination/paywalls/pop-ups, extracting from PDFs, cross-referencing citations, and synthesizing notes. Tools like Elicit help with search, but none truly understand partial user flows and then perform complex, multi-step web actions autonomously on real, dynamic sites.

## The Solution
LitPilot delivers true agentic research autopilot:

1. **User Demo Input** (privacy-safe & simple):  
   - Web app form: Textarea for step-by-step description + optional screenshot uploads.  
   - Ephemeral: Processed once in API routes, no storage or browser monitoring.

2. **Decomposed Intent Understanding** (SOTA from research):  
   - **Stage 1 (Summarization)**: Model breaks each described step into structured summaries (screen/action/context).  
   - **Stage 2 (Aggregation & Inference)**: Chains summaries to infer precise goal, e.g., "Compile literature review on decomposed intent extraction for web agents: gather 10 papers since 2023, extract methods/results/citations into markdown with table."  
   - Directly from EMNLP 2025 paper **"Small Models, Big Results: Achieving Superior Intent Extraction through Decomposition"**

3. **Autonomous Execution** via TinyFish Web Agent API:  
   - Streams real-time progress (SSE from /v1/automation/run-sse).  
   - Performs multi-step live web work: search Scholar/arXiv, paginate results, extract titles/abstracts/snippets from previews/PDFs, compile structured markdown report.  
   - Handles real complexities: dynamic UIs, sessions, pagination — no mocks.

## Key Features
- Privacy-by-design: User-entered data only; ephemeral in-memory processing; HTTPS; no persistent logs.  
- Streaming UI: Live agent progress ("Navigating to Scholar...", "Extracted paper 1...").  
- Output: Clean markdown report in-app (titles, authors, abstracts, citations).  
- Stretch: Screenshot vision via Qwen2-VL, Google Docs export via TinyFish.

## Tech Stack
- [x] **Frontend:** Vue.js 3 (Vite) + vanilla CSS (glassmorphic dark theme)
- [x] **Backend:** FastAPI + Agno SDK (AgentOS)
- [x] **Intent Engine:** Mistral Large for text/reasoning, OpenRouter (`nvidia/llama-nemotron-embed-vl-1b-v2:free`) for vision fallback
- [x] **Execution:** TinyFish Web Agent API (`/v1/automation/run-sse` for SSE streaming)
- [x] **Deployment:** Vercel (frontend) / any Python host (backend)
- [x] **Inspiration:** EMNLP 2025 paper + TinyFish cookbook examples

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Backend
```bash
cd backend
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and TINYFISH_API_KEY
uv sync
uv run python server.py
# Backend runs at http://localhost:7777
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Frontend runs at http://localhost:5173
```

### Environment Variables
| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key (if needed by Agno default integrations) |
| `MISTRAL_API_KEY` | Mistral API key for text/reasoning intent and execution agents |
| `OPENROUTER_API_KEY` | OpenRouter API key for vision/screenshot fallback (`llama-nemotron-embed-vl`) |
| `TINYFISH_API_KEY` | TinyFish Web Agent API key for autonomous execution |

## Project Structure
```
litpilot/
├── backend/
│   ├── agents/
│   │   ├── intent.py       # Stage 1 (Summarizer) + Stage 2 (Aggregator)
│   │   └── executor.py     # Research executor with TinyFish tools
│   ├── tools/
│   │   └── tinyfish.py     # Custom Agno Toolkit for TinyFish API
│   ├── server.py           # FastAPI + CORS + SSE endpoints
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   └── HomePage.vue       # Main workflow page
│   │   ├── components/
│   │   │   ├── InputForm.vue      # Research description input
│   │   │   ├── IntentReview.vue   # Inferred intent review card
│   │   │   ├── ExecutionStream.vue # Live SSE event log
│   │   │   └── ReportDisplay.vue  # Markdown report renderer
│   │   ├── composables/
│   │   │   └── useApi.js          # Backend API client
│   │   ├── router/
│   │   │   └── index.js           # Vue Router config
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css              # Design system
│   ├── index.html
│   └── package.json
└── README.md
```

## Demo (Submission Video)
- 2–3 min raw recording (post publicly on X tagging @Tiny_fish):  
  - Open web app → input demo text → infer & display intent → "Execute" → stream events → final report displayed.  
- Highlights real multi-step web agency on live academic sites.

## Why This Wins / Business Angle
- Aligns with TinyFish: Real, autonomous multi-step web work (beyond simple APIs).  
- High utility: Automates tedious lit reviews for academia, biotech, tech R&D — massive market.  
- SaaS potential: Freemium web tool (free tier limited reports, paid unlimited/advanced).  
- Edge: Applies fresh 2025 research for smarter intent → better agent performance.  
- Ethical: Privacy-focused, small-model efficiency.

Built in Kolkata during the TinyFish hack sprint — automating the boring parts of research! 🚀

**Public Demo Video:** [Insert X post/video link here before submission]  
**Questions/feedback:** DM @noob_contrarian on X.

Last updated: March 2026