import os
from typing import List
import google.auth
from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.tools import google_search
from pydantic import BaseModel, Field

# --- Configuration ---
try:
    _, project_id = google.auth.default()
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
except Exception:
    pass

os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "europe-west1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

MODEL = "gemini-2.5-pro"

# --- Data Models (The New "Contract") ---
class GovernancePrinciple(BaseModel):
    name: str = Field(..., description="Name of the principle (e.g., 'Data Minimization', 'Non-Maleficence')")
    source: str = Field(..., description="The real-world framework this comes from (e.g., 'GDPR', 'Asimov', 'NIST AI Risk Framework')")
    definition: str = Field(..., description="A concise definition of the rule.")

class ResearchFindings(BaseModel):
    """The mandatory structure for the Researcher's output."""
    context_summary: str = Field(..., description="Brief summary of the specific AI use case provided by the user.")
    applicable_frameworks: List[str] = Field(..., description="List of relevant laws or ethical frameworks found (e.g. 'HIPAA', 'Geneva Convention').")
    proposed_principles: List[GovernancePrinciple] = Field(..., description="The specific rules extracted from search.")
    known_risks: List[str] = Field(..., description="List of specific failure modes or risks for this use case.")

# --- Researcher Agent ---
researcher = Agent(
    name="researcher",
    model=MODEL,
    description="Specialist that gathers governance principles and legal frameworks.",
    
    # Updated Instruction for the Constitution Use Case
    instruction="""
    You are an AI Governance Research Specialist.
    The user will provide a specific "AI Use Case" (e.g., "A Medical Diagnosis Bot" or "A Military Drone").

    **Your Task:**
    1.  **Identify Frameworks:** Use Google Search to find relevant real-world frameworks (e.g., HIPAA for med, Geneva Convention for military, EU AI Act for general).
    2.  **Extract Principles:** Find the core ethical and legal rules that apply to this domain.
    3.  **Identify Risks:** What are the specific worst-case scenarios? (e.g., "Misdiagnosis leading to death").

    **Constraint:**
    Do not write the constitution. Just gather the raw "Legal Ingredients" for the Judge to review.
    """,
    
    # This enforces the Python object return type
    output_schema=ResearchFindings,
    tools=[google_search],
)

app = App(root_agent=researcher, name="researcher")