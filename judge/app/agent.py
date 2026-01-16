import os
from typing import Literal, List
import google.auth
from google.adk.agents import Agent
from google.adk.apps.app import App
from pydantic import BaseModel, Field

# --- Configuration ---
try:
    _, project_id = google.auth.default()
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
except Exception:
    pass

os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

MODEL = "gemini-2.5-pro"

# --- Data Models (The Contract) ---

class PrincipleVerdict(BaseModel):
    """The decision for a single proposed principle."""
    principle_name: str = Field(..., description="The name of the principle being evaluated.")
    status: Literal["approved", "rejected", "amended"] = Field(..., description="The verdict.")
    reasoning: str = Field(..., description="Why this decision was made. If rejected, explain why.")
    amendment_text: str = Field(None, description="If status is 'amended', provide the new, stricter wording here.")

class JudgeFeedback(BaseModel):
    """The formal output from the Supreme Court (Judge Agent)."""
    
    overall_status: Literal["pass", "fail"] = Field(
        description="Select 'pass' if we have enough approved principles to draft a constitution. Select 'fail' if the research was garbage."
    )
    
    verdicts: List[PrincipleVerdict] = Field(
        ..., description="List of decisions for every principle proposed by the Researcher."
    )
    
    mandatory_constraints: List[str] = Field(
        ..., description="A list of strict 'Red Lines' or formatting rules the Builder MUST follow (e.g. 'Do not allow military targeting')."
    )
    
    interpretive_guidance: str = Field(
        ..., description="Instructions for the Builder on the tone (e.g., 'Use strict, formal legalese')."
    )

# --- Judge Agent ---
judge = Agent(
    name="judge",
    model=MODEL,
    description="Supreme Court Justice of AI Governance. Evaluates principles for enforceability.",
    
    instruction="""
    You are the Supreme Court Justice of AI Governance.
    You will receive a list of "Proposed Principles" and "Context" from the Researcher.

    **Your Task:**
    Evaluate every proposed principle for the specific AI Use Case.

    **Evaluation Criteria:**
    1.  **Relevance:** Does the principle actually apply to this specific AI? (e.g., Don't apply 'HIPAA' to a 'Music Bot').
    2.  **Enforceability:** Is the principle specific enough? (e.g., REJECT "Be nice." APPROVE "Do not output profanity.").
    3.  **Safety:** Does it cover the 'Known Risks' identified by the researcher?

    **Output Requirements:**
    - If a principle is good but vague, mark it **"amended"** and rewrite it in the `amendment_text` field.
    - If a principle is dangerous or irrelevant, mark it **"rejected"**.
    - In `mandatory_constraints`, list the hard rules the Builder must not break.
    """,
    
    output_schema=JudgeFeedback,
    # Disallow transfers as it uses output_schema (Function Call)
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

app = App(root_agent=judge, name="judge")