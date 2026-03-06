"""
Executor Agent — Autonomous Literature Review via TinyFish

Takes an inferred research intent and uses specialized scout agents
to autonomously search academic sites in parallel, then synthesizes 
the results into a structured markdown report.
"""

import asyncio
import json
import logging
from textwrap import dedent
from typing import List, Dict, Any

from agno.agent import Agent
from agno.models.mistral import MistralChat
from tools.tinyfish import TinyFishTools

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Specialized Scout Agents
# ─────────────────────────────────────────────────────────────

def create_scout_agent(name: str, source_name: str) -> Agent:
    instructions = dedent(f"""\
        You are LitPilot's {source_name} Scout. Your only job is to search 
        {source_name} for academic papers matching the user's research intent.

        Rules:
        1. Use your search tool to find the requested number of papers.
        2. Extract: Title, Authors, Year, Abstract/Snippet, and Link.
        3. Output exactly what you find — do not synthesize yet.
        4. If {source_name} is unavailable or returns no results, report it clearly.
    """)
    return Agent(
        name=name,
        model=MistralChat(id="mistral-large-latest"),
        tools=[TinyFishTools()],
        instructions=instructions,
        markdown=False, # JSON/Structured output preferred for internal step
    )

scholar_scout = create_scout_agent("Scholar Scout", "Google Scholar")
arxiv_scout = create_scout_agent("arXiv Scout", "arXiv")
semantic_scout = create_scout_agent("Semantic Scout", "Semantic Scholar")

# ─────────────────────────────────────────────────────────────
# Synthesis Agent
# ─────────────────────────────────────────────────────────────

SYNTHESIS_INSTRUCTIONS = dedent("""\
    You are LitPilot's Senior Research Librarian. You will receive raw paper
    extraction results from several scouting agents.

    Your task:
    1. **De-duplicate** — identify and merge entries for the same paper found
       across different sources.
    2. **Synthesize** — Identify major themes or methodology trends across 
       all found papers.
    3. **Format** — Produce a high-quality Markdown report with:
       - Clear title and executive summary.
       - A summary table of all unique papers.
       - Detailed sections for each paper (link, abstract snippet, year).
       - A "Research Gaps & Future Directions" section based on the findings.

    Rules:
    - Maintain academic rigor.
    - Ensure all links are preserved.
    - Be concise but thorough.
""")

synthesis_agent = Agent(
    name="Research Synthesizer",
    model=MistralChat(id="mistral-large-latest"),
    instructions=SYNTHESIS_INSTRUCTIONS,
    markdown=True,
    add_datetime_to_context=True,
)

# ─────────────────────────────────────────────────────────────
# Orchestration Logic
# ─────────────────────────────────────────────────────────────

async def scout_task(agent: Agent, intent: str) -> str:
    """Helper to run an agent in a thread for parallel execution."""
    loop = asyncio.get_event_loop()
    # agno.agent.run is likely blocking, run in thread to avoid blocking loop
    response = await loop.run_in_executor(None, agent.run, intent)
    return response.content if response else f"No results from {agent.name}"

async def execute_research_async(intent: Dict[str, Any]) -> str:
    """
    Parallel orchestration of scouts + synthesis.
    """
    intent_str = intent.get("inferred_intent", str(intent))
    logger.info(f"Orchestrating parallel research for: {intent_str}")

    # Run scouts in parallel
    scout_names = ["Google Scholar", "arXiv", "Semantic Scholar"]
    scouts = [scholar_scout, arxiv_scout, semantic_scout]
    
    results = await asyncio.gather(*[scout_task(s, intent_str) for s in scouts])
    
    combined_results = "\n\n".join([
        f"### Results from {name}:\n{res}" 
        for name, res in zip(scout_names, results)
    ])

    logger.info("Scouting complete. Synthesizing final report...")
    
    # Synthesis (usually one final pass)
    synthesis_prompt = (
        f"Research Intent: {intent_str}\n\n"
        f"Raw Results:\n{combined_results}"
    )
    
    loop = asyncio.get_event_loop()
    final_response = await loop.run_in_executor(None, synthesis_agent.run, synthesis_prompt)
    
    return final_response.content if final_response else "Synthesis failed."

def execute_research(intent: Any) -> str:
    """Synchronous wrapper for AgentOS integration."""
    return asyncio.run(execute_research_async(intent))
