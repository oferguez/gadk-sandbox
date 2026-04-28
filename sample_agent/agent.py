"""
aaa
"""

from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from google.adk.models import Gemini
from google.genai import types

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)

root_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config
    ),
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge.' \
    ' If needed use Google Search and tell the user what youve searched and where',
    tools=[google_search]
)

if __name__ == "__main__":
    print('roro')
    