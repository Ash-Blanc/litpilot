"""
Knowledge Agent — Contextual Research & Historical Recall

Provides tools for the agent to 'remember' and build upon existing
research papers (PDFs, Zotero links) and RECALL past manual research
sessions from rough notes or logs.
"""

import os
import json
import logging
from typing import List, Optional, Dict, Any
from textwrap import dedent

from agno.agent import Agent
from agno.models.mistral import MistralChat

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Persistent History & Milestones
# ─────────────────────────────────────────────────────────────

class HistoryManager:
    """Manages the storage and retrieval of past research milestones."""
    
    def __init__(self, storage_path: str = "./research_data/history"):
        self.storage_path = storage_path
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)

    def save_milestone(self, milestone: Dict[str, Any]) -> str:
        """Save a reconstructed research milestone."""
        timestamp = milestone.get("date", "unknown_date").replace(" ", "_")
        file_path = os.path.join(self.storage_path, f"milestone_{timestamp}.json")
        with open(file_path, "w") as f:
            json.dump(milestone, f, indent=2)
        return f"Milestone saved to {file_path}"

    def get_past_context(self) -> str:
        """Retrieves a summary of all past milestones for the agent's context."""
        milestones = []
        for filename in os.listdir(self.storage_path):
            if filename.startswith("milestone_") and filename.endswith(".json"):
                with open(os.path.join(self.storage_path, filename), "r") as f:
                    milestones.append(json.load(f))
        
        if not milestones:
            return "No previous research sessions found in the history."
            
        summary = "PREVIOUS RESEARCH MILESTONES FOUND:\n"
        for m in milestones:
            summary += f"- {m.get('date')}: {m.get('summary')}\n  Key Topics: {', '.join(m.get('topics', []))}\n"
        return summary

history_manager = HistoryManager()

# ─────────────────────────────────────────────────────────────
# Archaeology Agent — Retrospective Intent Reconstruction
# ─────────────────────────────────────────────────────────────

ARCHAEOLOGY_INSTRUCTIONS = dedent("""\
    You are LitPilot's Archaeology Agent. Your expertise is in "Retrospective 
    Intent Reconstruction." 

    Researchers often have manual logs, rough notes, or browser history from 
    days or weeks ago. Your task is to analyze these disconnected fragments 
    and reconstruct the coherent research trajectory.

    Output format: A JSON object representing the reconstructed milestone:
    {
      "date": "Estimated time period of this research",
      "summary": "Coherent summary of what the researcher was trying to do.",
      "reconstructed_intent": "A precise research goal derived from the notes.",
      "topics": ["topic1", "topic2"],
      "extracted_entities": ["paper names", "authors", "URLs"],
      "confidence": 0.0-1.0
    }

    Rules:
    1. Fill in the blanks — if notes are sparse, use your general academic 
       knowledge to infer the likely research direction.
    2. Be actionable — the `reconstructed_intent` should be usable by the 
       Execution Agent to 'continue' the work.
    3. Output ONLY valid JSON.
""")

archaeology_agent = Agent(
    name="Archaeology Agent",
    model=MistralChat(id="mistral-large-latest"),
    instructions=ARCHAEOLOGY_INSTRUCTIONS,
    markdown=False
)

# ─────────────────────────────────────────────────────────────
# Knowledge Tools
# ─────────────────────────────────────────────────────────────

def reconstruct_past_research(notes: str) -> Dict[str, Any]:
    """
    Take manual notes and reconstruct the research intent and milestones.
    """
    logger.info("Archaeology Agent: Reconstructing past research from notes")
    response = archaeology_agent.run(notes)
    
    try:
        data = json.loads(response.content)
        history_manager.save_milestone(data)
        return data
    except Exception as e:
        logger.error(f"Failed to parse archaeology results: {e}")
        return {"error": "Failed to reconstruct history", "raw": response.content}

def get_historical_context() -> str:
    """Returns a string summary of past research to inject into current agents."""
    return history_manager.get_past_context()

# ─────────────────────────────────────────────────────────────
# Agent Definition
# ─────────────────────────────────────────────────────────────

knowledge_agent = Agent(
    name="Research Librarian",
    model=MistralChat(id="mistral-large-latest"),
    instructions=dedent("""\
        You are LitPilot's Knowledge Librarian. You bridge the gap between
        past manual research and current autonomous work.
    """),
    tools=[
        reconstruct_past_research,
        get_historical_context
    ],
    markdown=True
)
