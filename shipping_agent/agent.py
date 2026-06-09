#pylint: disable=unused-import,missing-docstring
import asyncio
import base64
import os
from pathlib import Path

import uuid
from google.genai import types

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from google.adk.apps.app import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool
from google.adk.runners import InMemoryRunner



if "GOOGLE_API_KEY" not in os.environ:
    raise RuntimeError("GOOGLE_API_KEY must be set in the environment.")

print("✅ ADK components imported successfully.")

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

print(f"✅ retry_config: {retry_config}")

# MCP integration with Everything Server
mcp_image_server = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",  # Run MCP server via npx
            args=[
                "-y",  # Argument for npx to auto-confirm install
                "@modelcontextprotocol/server-everything",
            ],
            tool_filter=["getTinyImage"],
        ),
        timeout=30,
    )
)
print(f"✅ MCP Tool created: {mcp_image_server}")

# Create image agent with MCP integration
image_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="image_agent",
    instruction="Use the MCP Tool to generate images for user queries",
    tools=[mcp_image_server],
)
print(f"✅ image agent created: {image_agent}")

runner = InMemoryRunner(agent=image_agent)


def save_image_from_base64(image_data, output_dir="outputs"):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    image_path = output_path / f"tiny-image-{uuid.uuid4().hex}.png"
    image_path.write_bytes(base64.b64decode(image_data))
    return image_path


async def main():
    try:
        response = await runner.run_debug("Provide a sample tiny image", verbose=True)
        print(response)
    finally:
        await runner.close()

    for event in response:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "function_response") and part.function_response:
                    for item in part.function_response.response.get("content", []):
                        if item.get("type") == "image":
                            image_path = save_image_from_base64(item["data"])
                            print(f"Saved image to {image_path}")


if __name__ == "__main__":
    asyncio.run(main())
