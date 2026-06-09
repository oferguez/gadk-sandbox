from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.models import Gemini
from google.adk.tools import FunctionTool
from google.genai import types


retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


def exit_loop():
    """Signal that the refinement loop should stop."""
    return {"status": "approved"}


initial_writer_agent = Agent(
    name="InitialWriterAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config,
    ),
    instruction=(
        "Based on the user's prompt, write a short story of around 100-150 words. "
        "Return only the story text."
    ),
    output_key="current_story",
)


critic_agent = Agent(
    name="CriticAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config,
    ),
    instruction=(
        "Review the story below.\n"
        "Story: {current_story}\n\n"
        "Evaluate the plot, characters, and pacing.\n"
        'If the story is strong and complete, respond with exactly "APPROVED".\n'
        "Otherwise, provide 2-3 short, actionable suggestions."
    ),
    output_key="critique",
)


refiner_agent = Agent(
    name="RefinerAgent",
    model=Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config,
    ),
    instruction=(
        "You refine the story using the critique.\n\n"
        "Story Draft: {current_story}\n"
        "Critique: {critique}\n\n"
        'If the critique is exactly "APPROVED", call `exit_loop` and do not rewrite the story.\n'
        "Otherwise, rewrite the story so it addresses the critique and return only the revised story."
    ),
    output_key="current_story",
    tools=[FunctionTool(exit_loop)],
)


story_refinement_loop = LoopAgent(
    name="StoryRefinementLoop",
    sub_agents=[critic_agent, refiner_agent],
    max_iterations=2,
)


root_agent = SequentialAgent(
    name="story_writer_agent",
    sub_agents=[initial_writer_agent, story_refinement_loop],
    description="Writes and lightly refines a short story from the user's prompt.",
)
