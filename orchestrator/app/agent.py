import os
import json
import warnings
from typing import AsyncGenerator, Any
import google.auth
from google.adk.agents import BaseAgent, LoopAgent, SequentialAgent

# Suppress experimental warnings
warnings.filterwarnings("ignore", message=".*\[EXPERIMENTAL\].*", category=UserWarning)

from google.adk.apps.app import App
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.callback_context import CallbackContext

# --- Configuration ---
try:
    _, project_id = google.auth.default()
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
except Exception:
    pass

os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# --- Callbacks ---
def create_save_output_callback(key: str):
    """Creates a callback to save the agent's final response to session state."""
    def callback(callback_context: CallbackContext, **kwargs) -> None:
        ctx = callback_context
        # Find the last event from this agent that has content
        for event in reversed(ctx.session.events):
            if event.author == ctx.agent_name and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text:
                    # Try to parse as JSON if it looks like it (for judge_feedback)
                    # This handles the JSON string returned by the remote agent
                    if text.strip().startswith("{"):
                        try:
                            # Parse JSON string into a Dictionary
                            data = json.loads(text)
                            ctx.state[key] = data
                            print(f"[{ctx.agent_name}] Successfully parsed JSON output.")
                        except json.JSONDecodeError:
                            print(f"[{ctx.agent_name}] Warning: Output looked like JSON but failed parse.")
                            ctx.state[key] = text
                    else:
                        ctx.state[key] = text
                    
                    print(f"[{ctx.agent_name}] Saved output to state['{key}']")
                    return
    return callback

# --- Remote Agents ---
# Update descriptions to match the new Constitution use case
researcher_url = os.environ.get("RESEARCHER_AGENT_CARD_URL", "http://localhost:8001/.well-known/agent.json")
researcher = RemoteA2aAgent(
    name="researcher",
    agent_card=researcher_url,
    description="AI Governance Specialist. Returns structured legal principles and risk frameworks.",
    after_agent_callback=create_save_output_callback("research_findings")
)

judge_url = os.environ.get("JUDGE_AGENT_CARD_URL", "http://localhost:8002/.well-known/agent.json")
judge = RemoteA2aAgent(
    name="judge",
    agent_card=judge_url,
    description="Supreme Court Justice. Evaluates principles and issues binding verdicts.",
    after_agent_callback=create_save_output_callback("judge_feedback")
)

content_builder_url = os.environ.get("CONTENT_BUILDER_AGENT_CARD_URL", "http://localhost:8003/.well-known/agent.json")
content_builder = RemoteA2aAgent(
    name="content_builder",
    agent_card=content_builder_url,
    description="Constitutional Drafter. Transforms approved principles into a formal document.",
    after_agent_callback=create_save_output_callback("content_output")
)

# --- Local Orchestration Agents ---

class EscalationChecker(BaseAgent):
    """Checks the judge's feedback and breaks the loop if 'overall_status' is 'pass'."""

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        feedback = ctx.session.state.get("judge_feedback")

        print(f"[EscalationChecker] Checking Feedback: {feedback}")

        should_escalate = False

        # Case A: Feedback is a Dictionary (Parsed JSON)
        if isinstance(feedback, dict):
            # CHECK FOR 'overall_status' (The new field name)
            if feedback.get("overall_status") == "pass":
                should_escalate = True
            # Fallback for legacy code support
            elif feedback.get("status") == "pass":
                should_escalate = True

        # Case B: Feedback is a String (Failed parse or raw text)
        elif isinstance(feedback, str):
            if '"overall_status": "pass"' in feedback or '"status": "pass"' in feedback:
                 should_escalate = True

        if should_escalate:
            print("[EscalationChecker] Judge approved. Moving to Content Builder.")
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            print("[EscalationChecker] Judge rejected (or no feedback). Loop continues.")
            yield Event(author=self.name)

escalation_checker = EscalationChecker(name="escalation_checker")

# --- Orchestration ---

research_loop = LoopAgent(
    name="governance_loop",
    description="Iteratively researches governance principles and judges them until approved.",
    sub_agents=[researcher, judge, escalation_checker],
    max_iterations=3,
)

root_agent = SequentialAgent(
    name="constitution_pipeline",
    description="A pipeline that researches AI governance and drafts a constitution.",
    sub_agents=[research_loop, content_builder],
)

app = App(root_agent=root_agent, name="orchestrator_app")