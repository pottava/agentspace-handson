import os

import google.auth
from google.adk.agents import LlmAgent

from .tools import calculator_tools


_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


root_agent = LlmAgent(
    name="calculator_agent",
    model="gemini-2.5-flash",
    description="四則演算エージェント",
    instruction="あなたは四則演算を支援するアシスタントです",
    tools=calculator_tools,
)
