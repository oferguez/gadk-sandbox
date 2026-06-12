# pylint: disable=missing-docstring disable=broad-except


"""
Cafe Finder Agent
=================
Uses Google ADK + Firecrawl /interact to find top cafes near a location
by navigating and scraping Timeout London.

Requirements:
    pip install google-adk firecrawl-py

Environment variables:
    FIRECRAWL_API_KEY   your Firecrawl key  (e.g. fc-xxxx)
    GOOGLE_API_KEY      your Gemini API key
    GEMINI_API_KEY      optional fallback if GOOGLE_API_KEY is not set
"""

import os
from firecrawl import Firecrawl
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from env_loader import load_env_local

load_env_local()

# ── API keys ──────────────────────────────────────────────────────────────────
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")
if not FIRECRAWL_API_KEY:
    raise RuntimeError("FIRECRAWL_API_KEY must be set in the environment.")

if "GOOGLE_API_KEY" not in os.environ and "GEMINI_API_KEY" in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

if "GOOGLE_API_KEY" not in os.environ:
    raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY must be set in the environment.")

firecrawl = Firecrawl(api_key=FIRECRAWL_API_KEY)


# ── Firecrawl tools ───────────────────────────────────────────────────────────

def scrape_timeout_cafes(location: str) -> dict:
    """
    Opens the Timeout London best-cafes page and uses Firecrawl's /interact
    to search for and extract the top cafes near the given location or postcode.

    Args:
        location: A London neighbourhood name or postcode, e.g. "Shoreditch" or "E1 6RF".

    Returns:
        A dict with keys:
          - cafes: list of dicts, each with name, description, address
          - raw_output: the raw text returned by Firecrawl
          - error: error message if something went wrong (else None)
    """
    url = "https://www.timeout.com/london/food-drink"

    try:
        # Step 1: Scrape the page to open a live browser session
        print(f"[firecrawl] Scraping {url} ...")
        result = firecrawl.scrape(url, formats=["markdown"])
        scrape_id = result.metadata.scrape_id
        print(f"[firecrawl] Session opened — scrape_id: {scrape_id}")

        # Step 2: Ask Firecrawl to search/filter for cafes near the location
        print(f"[firecrawl] Searching for cafes near '{location}' ...")
        firecrawl.interact(
            scrape_id,
            prompt=(
                f"Search or filter the page for cafes near '{location}' in London. "
                "If there is a location search or filter, use it."
            ),
        )

        # Step 3: Extract structured cafe data
        print("[firecrawl] Extracting cafe listings ...")
        extraction = firecrawl.interact(
            scrape_id,
            prompt=(
                "List the top 10 cafes shown on this page. "
                "For each one give: name, a one-sentence description, and address if available. "
                "Format each entry as: NAME | DESCRIPTION | ADDRESS"
            ),
        )

        raw_output = extraction.output or ""

        # Step 4: Parse the pipe-delimited lines into structured dicts
        cafes = []
        for line in raw_output.splitlines():
            line = line.strip()
            if "|" in line:
                parts = [p.strip() for p in line.split("|")]
                cafes.append({
                    "name":        parts[0] if len(parts) > 0 else "",
                    "description": parts[1] if len(parts) > 1 else "",
                    "address":     parts[2] if len(parts) > 2 else "",
                })

        return {"cafes": cafes, "raw_output": raw_output, "error": None}

    except Exception as e:
        return {"cafes": [], "raw_output": "", "error": str(e)}

    finally:
        # Always close the Firecrawl session to stop billing
        try:
            firecrawl.stop_interaction(scrape_id)
            print("[firecrawl] Session closed.")
        except Exception:
            pass


def format_cafe_results(cafes: list, location: str) -> str:
    """
    Formats a list of cafe dicts into a readable string for the user.

    Args:
        cafes:    List of dicts with keys name, description, address.
        location: The location the search was for.

    Returns:
        A formatted string listing the cafes.
    """
    if not cafes:
        return f"No cafes found near {location}."

    lines = [f"Top cafes near {location}:\n"]
    for i, cafe in enumerate(cafes, 1):
        lines.append(f"{i}. {cafe['name']}")
        if cafe["description"]:
            lines.append(f"   {cafe['description']}")
        if cafe["address"]:
            lines.append(f"   📍 {cafe['address']}")
        lines.append("")

    return "\n".join(lines)


# ── ADK Agent ─────────────────────────────────────────────────────────────────

root_agent = Agent(
    name="cafe_finder",
    model="gemini-2.0-flash",
    description="Finds the best cafes in London near a given location using Timeout London.",
    instruction=(
        "You help users find great cafes in London near their location. "
        "When a user gives you a neighbourhood or postcode, use the scrape_timeout_cafes tool "
        "to fetch the results, then use format_cafe_results to present them clearly. "
        "Always tell the user you're fetching live data from Timeout London."
    ),
    tools=[scrape_timeout_cafes, format_cafe_results],
)


# ── Runner (CLI entry point) ───────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio

    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="cafe_finder",
        session_service=session_service,
    )

    async def main():
        session = await session_service.create_session(
            app_name="cafe_finder",
            user_id="user_1",
        )

        location = input("Enter a London neighbourhood or postcode: ").strip()
        if not location:
            location = "Shoreditch"

        print(f"\nSearching for cafes near '{location}'...\n")

        message = types.Content(
            role="user",
            parts=[types.Part(text=f"Find me the best cafes near {location} in London.")]
        )

        async for event in runner.run_async(
            user_id="user_1",
            session_id=session.id,
            new_message=message,
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        print(part.text)

    asyncio.run(main())
