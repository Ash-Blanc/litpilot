"""
TinyFish Web Agent API — Custom Agno Toolkit

Wraps the TinyFish /v1/automation/run-sse endpoint so Agno agents
can autonomously perform web automation tasks (search Scholar, extract
papers, fill forms, etc.) on live websites.
"""

import json
import os
from typing import Optional

import httpx
from agno.tools import Toolkit
from agno.utils.log import logger

TINYFISH_API_URL = "https://agent.tinyfish.ai/v1/automation/run-sse"


class TinyFishTools(Toolkit):
    """Toolkit for autonomous web automation via TinyFish Web Agent API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 120,
        **kwargs,
    ):
        self.api_key = api_key or os.getenv("TINYFISH_API_KEY", "")
        self.timeout = timeout

        tools = [
            self.run_web_automation,
            self.search_google_scholar,
            self.search_arxiv,
            self.search_semantic_scholar,
        ]
        super().__init__(name="tinyfish_tools", tools=tools, **kwargs)

    # ── helpers ────────────────────────────────────────────────────────

    def _call_tinyfish(self, url: str, goal: str) -> str:
        """Internal: POST to TinyFish run-sse, consume SSE stream, return result."""
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {"url": url, "goal": goal}

        logger.info(f"[TinyFish] url={url}  goal={goal[:80]}…")

        events: list[dict] = []
        final_result = None

        try:
            with httpx.stream(
                "POST",
                TINYFISH_API_URL,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    raw = line[len("data:"):].strip()
                    if not raw:
                        continue
                    try:
                        event = json.loads(raw)
                    except json.JSONDecodeError:
                        continue

                    events.append(event)
                    event_type = event.get("type", "")
                    logger.debug(f"[TinyFish] event type={event_type}")

                    if event_type == "COMPLETE" and event.get("status") == "COMPLETED":
                        final_result = event.get("resultJson") or event.get("result", "")
                        break

        except httpx.HTTPStatusError as exc:
            return json.dumps({
                "error": f"TinyFish HTTP {exc.response.status_code}",
                "detail": exc.response.text[:500],
            })
        except httpx.RequestError as exc:
            return json.dumps({"error": f"TinyFish request failed: {exc}"})

        if final_result is not None:
            if isinstance(final_result, dict):
                return json.dumps(final_result, ensure_ascii=False)
            return str(final_result)

        # If no COMPLETE event, return all collected events
        return json.dumps(
            {"events": events, "note": "No COMPLETE event received"},
            ensure_ascii=False,
        )

    # ── tools (exposed to agent) ──────────────────────────────────────

    def run_web_automation(self, url: str, goal: str) -> str:
        """
        Perform an autonomous web automation task on a given URL.

        Use this tool to navigate to a website and perform a complex,
        multi-step task described in natural language. The web agent will
        interact with the real website (click, type, scroll, extract).

        Args:
            url:  The full URL to navigate to.
            goal: Natural-language description of what to do on that page.

        Returns:
            str: JSON string with the extracted data or result.
        """
        return self._call_tinyfish(url, goal)

    def search_google_scholar(self, query: str, num_results: int = 10) -> str:
        """
        Search Google Scholar for academic papers matching a query.

        Args:
            query:       The search query (e.g. "decomposed intent extraction web agents").
            num_results: How many paper results to extract (default 10).

        Returns:
            str: JSON list of papers with title, authors, year, abstract snippet,
                 citation count, and link.
        """
        url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}"
        goal = (
            f"Extract the first {num_results} paper results as a JSON array. "
            "For each paper include: title, authors, year, abstract_snippet, "
            "citation_count, and link."
        )
        return self._call_tinyfish(url, goal)

    def search_arxiv(self, query: str, num_results: int = 10) -> str:
        """
        Search arXiv for preprints matching a query.

        Args:
            query:       The search query.
            num_results: How many results to extract (default 10).

        Returns:
            str: JSON list of papers with title, authors, abstract, date, arxiv_id, link.
        """
        url = f"https://arxiv.org/search/?searchtype=all&query={query.replace(' ', '+')}"
        goal = (
            f"Extract the first {num_results} paper results as a JSON array. "
            "For each paper include: title, authors, abstract, date, arxiv_id, and link."
        )
        return self._call_tinyfish(url, goal)

    def search_semantic_scholar(self, query: str, num_results: int = 10) -> str:
        """
        Search Semantic Scholar for papers matching a query.

        Args:
            query:       The search query.
            num_results: How many results to extract (default 10).

        Returns:
            str: JSON list of papers with title, authors, year, abstract,
                 citation_count, and link.
        """
        url = f"https://www.semanticscholar.org/search?q={query.replace(' ', '+')}"
        goal = (
            f"Extract the first {num_results} paper results as a JSON array. "
            "For each paper include: title, authors, year, abstract, "
            "citation_count, and link."
        )
        return self._call_tinyfish(url, goal)
