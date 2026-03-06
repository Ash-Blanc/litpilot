"""
Intent Extraction Agents — Decomposed Two-Stage Method

Implements the approach from the EMNLP 2025 paper:
  "Small Models, Big Results: Achieving Superior Intent Extraction
   through Decomposition"

Stage 1 (Summarizer): Breaks each described step into structured
  summaries (screen description, action taken, context).
Stage 2 (Aggregator): Chains summaries to infer the precise high-level
  research goal.
"""

from textwrap import dedent
from typing import List, Dict, Any, Optional
import copy
import logging

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.openrouter import OpenRouter
from agno.models.mistral import MistralChat

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Stage 1 — Summarizer (Vision Fallback)
# ─────────────────────────────────────────────────────────────

SUMMARIZER_INSTRUCTIONS = dedent("""\
You are an expert at analyzing descriptions of research browsing sessions.

Given a user's step-by-step textual description of their partial research
session (e.g. "Searched Google Scholar for X, opened a PDF, highlighted the
methods section") and optional screenshots, produce a structured JSON array of summaries.

For EACH described step, output an object with:
- "step_number": integer
- "screen": what the user was likely looking at (e.g. "Google Scholar search results page")
- "action": what the user did (e.g. "Clicked on the third result PDF link")
- "context": inferred research context (e.g. "Looking for methodology details on X")
- "entities": key entities mentioned (paper names, topics, authors, URLs)

Rules:
1. Be precise — infer only what is clearly supported by the description or images.
2. If the user provides screenshots, extract relevant entities and context from them.
3. Output ONLY valid JSON — no markdown fences, no explanation.
4. Order steps chronologically as described.
""")

try:
    from pydantic import BaseModel, Field
    class StepSummary(BaseModel):
        step_number: int
        screen: str
        action: str
        context: str
        entities: List[str]
except ImportError:
    StepSummary = dict # fallback

# Vision agent (OpenRouter) used ONLY when images are present
vision_summarizer_agent = Agent(
    name="Intent Summarizer Vision (Stage 1)",
    model=OpenRouter(
        id="nvidia/llama-nemotron-embed-vl-1b-v2:free",
    ),
    instructions=SUMMARIZER_INSTRUCTIONS,
    markdown=False,
    add_datetime_to_context=True,
    # response_model=List[StepSummary], # OpenRouter free models can struggle with strict structured outputs, using prompt instructions instead
)

# Text agent (Mistral) used for standard text modality
text_summarizer_agent = Agent(
    name="Intent Summarizer Text (Stage 1)",
    model=MistralChat(id="mistral-large-latest"),
    instructions=SUMMARIZER_INSTRUCTIONS,
    markdown=False,
    add_datetime_to_context=True,
)

# ─────────────────────────────────────────────────────────────
# Stage 2 — Aggregator
# ─────────────────────────────────────────────────────────────

AGGREGATOR_INSTRUCTIONS = dedent("""\
You are an expert at inferring precise research intents from structured
browsing session summaries.

You will receive a JSON array of step summaries from a user's partial
research session. Each summary has: step_number, screen, action, context,
entities.

Your task: Analyze all summaries together and infer the user's precise
high-level research GOAL. Think about:
- What topic are they researching?
- What kind of output do they want? (lit review, comparison table, survey)
- What scope? (time range, number of papers, specific venues)
- What depth? (abstracts only, methods, full analysis)

Respond with a JSON object:
{
  "inferred_intent": "A single, precise sentence describing what the user
    wants to accomplish. E.g.: Compile a literature review on decomposed
    intent extraction for web agents: gather 10 papers since 2023, extract
    methods/results/citations into markdown with comparison table.",
  "confidence": 0.0-1.0,
  "key_topics": ["topic1", "topic2"],
  "suggested_sources": ["Google Scholar", "arXiv", "Semantic Scholar"],
  "output_format": "markdown_report | comparison_table | annotated_bibliography",
  "scope": {
    "num_papers": 10,
    "year_range": "2023-present",
    "venues": ["any"]
  }
}

Rules:
1. Be specific and actionable in the inferred_intent.
2. Default to 10 papers, 2023-present if not clear from context.
3. Output ONLY valid JSON — no markdown fences, no explanation.
""")

# Stage 2 — Aggregators (Multi-Model)
# We use multiple models to get diverse perspectives on the research goal.

aggregator_mistral = Agent(
    name="Aggregator (Mistral)",
    model=MistralChat(id="mistral-large-latest"),
    instructions=AGGREGATOR_INSTRUCTIONS,
    markdown=False,
    add_datetime_to_context=True,
)

aggregator_gpt = Agent(
    name="Aggregator (GPT-4o)",
    model=OpenRouter(id="openai/gpt-4o-mini"),
    instructions=AGGREGATOR_INSTRUCTIONS,
    markdown=False,
    add_datetime_to_context=True,
)

aggregator_gemini = Agent(
    name="Aggregator (Gemini Flash)",
    model=OpenRouter(id="google/gemini-flash-1.5-8b"),
    instructions=AGGREGATOR_INSTRUCTIONS,
    markdown=False,
    add_datetime_to_context=True,
)

# ─────────────────────────────────────────────────────────────
# Stage 3 — Consensus & Synthesis
# ─────────────────────────────────────────────────────────────

CONSENSUS_INSTRUCTIONS = dedent("""\
You are LitPilot's Research Director. You will receive several inferred
research goals from different AI specialist models. 

Your task: Compare these goals, identify common requirements, resolve any
contradictions (e.g. if one model missed a specific paper venue mentioned
by others), and synthesize the final, most robust research intent.

Input format: A JSON object with model names as keys and their inferred intents as values.

Output format: A single JSON object with:
{
  "inferred_intent": "Final synthesized goal sentence.",
  "confidence": 0.0-1.0,
  "key_topics": [...],
  "suggested_sources": [...],
  "output_format": "...",
  "scope": { ... },
  "synthesis_notes": "What was resolved or emphasized during consensus."
}

Rules:
1. Be the 'Source of Truth' — synthesize for maximum utility and clarity.
2. Ensure the final `inferred_intent` contains all necessary parameters for the Execution Agent.
3. Output ONLY valid JSON.
""")

consensus_agent = Agent(
    name="Consensus Director (Stage 3)",
    model=MistralChat(id="mistral-large-latest"),
    instructions=CONSENSUS_INSTRUCTIONS,
    markdown=False,
    add_datetime_to_context=True,
)


# ─────────────────────────────────────────────────────────────
# Pipeline helper
# ─────────────────────────────────────────────────────────────

def infer_intent(user_description: str, images: Optional[List[Dict[str, str]]] = None) -> dict:
    """
    Run the two-stage intent decomposition pipeline.

    Args:
        user_description: The user's textual description of their partial
            research session.
        images: Optional list of base64 images to pass to the vision model.
            e.g. [{"url": "data:image/jpeg;base64,..."}]

    Returns:
        dict with keys: summaries (str), intent (dict parsed from Stage 2).
    """
    logger.info("Stage 1: Running Summarizer Agent")
    prompt_text = (
        f"Here is the user's description of their research session:\n\n"
        f"{user_description}\n\n"
        f"Produce the structured JSON summaries for each step."
    )
    if images and len(images) > 0:
        logger.info(f"Adding {len(images)} images to prompt (routing to vision model)")
        content = [{"type": "text", "text": prompt_text}]
        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {"url": img["url"]}
            })
        stage1_response = vision_summarizer_agent.run(content)
    else:
        logger.info("Text only prompt (routing to Mistral text model)")
        stage1_response = text_summarizer_agent.run(prompt_text)
        
    summaries_text = stage1_response.content

    # Stage 2: Parallel Aggregation
    logger.info("Stage 2: Running Multi-Model Aggregation")
    stage2_prompt = (
        f"Here are the structured step summaries from a user's research session:\n\n"
        f"{summaries_text}\n\n"
        f"Infer the user's precise high-level research goal."
    )
    
    # Run aggregations
    intent_m = aggregator_mistral.run(stage2_prompt).content
    intent_g = aggregator_gpt.run(stage2_prompt).content
    intent_f = aggregator_gemini.run(stage2_prompt).content

    # Stage 3: Consensus Synthesis
    logger.info("Stage 3: Running Consensus Synthesis")
    consensus_prompt = json.dumps({
        "expert_mistral": intent_m,
        "detail_gpt4o": intent_g,
        "speed_gemini": intent_f
    }, indent=2)

    stage3_response = consensus_agent.run(consensus_prompt)
    final_intent_text = stage3_response.content

    # Try to parse JSON
    try:
        if "```json" in final_intent_text:
            cleaned = final_intent_text.split("```json")[1].split("```")[0].strip()
            final_data = json.loads(cleaned)
        else:
            final_data = json.loads(final_intent_text)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON synthesis: {final_intent_text}")
        final_data = {"inferred_intent": final_intent_text, "confidence": 0.5}

    return {
        "summaries": summaries_text,
        "intent": final_data,
        "raw_responses": {
            "mistral": intent_m,
            "gpt4o": intent_g,
            "gemini": intent_f
        }
    }
