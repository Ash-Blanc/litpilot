"""
Executor Agent — Autonomous Literature Review via TinyFish

Takes an inferred research intent and uses TinyFish Web Agent tools
to autonomously search academic sites, extract papers, and compile
a structured markdown report.
"""

from textwrap import dedent

from agno.agent import Agent
from agno.models.mistral import MistralChat

from tools.tinyfish import TinyFishTools

# ─────────────────────────────────────────────────────────────
# Executor Agent
# ─────────────────────────────────────────────────────────────

EXECUTOR_INSTRUCTIONS = dedent("""\
You are LitPilot's Execution Agent — an autonomous research assistant
that performs literature reviews on live academic websites.

You have access to web automation tools that let you search and extract
data from Google Scholar, arXiv, and Semantic Scholar.

## Workflow

Given a research intent (goal), follow these steps:

1. **Parse the intent** — understand the topic, scope (number of papers,
   year range), and desired output format.

2. **Search multiple sources** — use your tools to search at least 2 of:
   Google Scholar, arXiv, Semantic Scholar.  Use the key topics from the
   intent as search queries.

3. **Extract paper details** — for each paper, collect:
   - Title
   - Authors
   - Year
   - Abstract / summary snippet
   - Citation count (if available)
   - Link / DOI

4. **Compile the report** — produce a clean Markdown report with:
   - A title and date
   - A summary of the search methodology
   - A table of all papers found
   - For each paper: title, authors, year, abstract snippet, link
   - A brief synthesis/themes section at the end

## Rules
- Always search for at least the number of papers specified in the intent.
- De-duplicate papers that appear in multiple sources.
- If a search fails, try an alternative query or source.
- Report any errors transparently.
- Be thorough but efficient — do not over-search.
""")

executor_agent = Agent(
    name="LitPilot Executor",
    model=MistralChat(id="mistral-large-latest"),
    tools=[TinyFishTools()],
    instructions=EXECUTOR_INSTRUCTIONS,
    markdown=True,
    add_datetime_to_context=True,
)


def execute_research(intent: str) -> str:
    """
    Run the executor agent with the given research intent.

    Args:
        intent: The inferred research intent string.

    Returns:
        str: The final markdown report.
    """
    prompt = (
        f"Execute the following research intent and produce a complete "
        f"literature review report:\n\n{intent}"
    )
    response = executor_agent.run(prompt)
    return response.content
