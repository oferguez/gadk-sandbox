# pylint: disable=missing-docstring
import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

from env_loader import load_env_local

load_env_local()

firecrawl_api_key = os.environ.get("FIRECRAWL_API_KEY")
if not firecrawl_api_key:
    raise RuntimeError("FIRECRAWL_API_KEY must be set in the environment.")

if "GOOGLE_API_KEY" not in os.environ and "GEMINI_API_KEY" in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

if "GOOGLE_API_KEY" not in os.environ:
    raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY must be set in the environment.")

firecrawl_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "firecrawl-mcp"],
            env={
                "FIRECRAWL_API_KEY": firecrawl_api_key,
            },
        )
    )
)

fc_agent = LlmAgent(
    model="gemini-2.5-flash-lite",
    name="firecrawl_research_agent",
    instruction="""
    You are a web research agent.

    Use Firecrawl when the user asks you to:
    - read a live web page
    - search the web
    - scrape documentation
    - map or crawl a website
    - extract structured information from pages

    Always summarise clearly and include source URLs when available.
    """,
    tools=[firecrawl_tools],
)

root_agent = fc_agent
