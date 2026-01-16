import os
from typing import List
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

# --- Data Models (The Final Artifact) ---

class ConstitutionArticle(BaseModel):
    title: str = Field(..., description="The article title (e.g., 'Article I: Rights of the System').")
    content: str = Field(..., description="The full text of the article in formal legalese.")

class AIConstitution(BaseModel):
    """The formal output structure for the AI Constitution."""
    title: str = Field(..., description="The official title (e.g., 'The Constitution of Autonomous Medical Bots').")
    preamble: str = Field(..., description="The opening statement establishing purpose and scope.")
    articles: List[ConstitutionArticle] = Field(..., description="The list of articles (I, II, III, etc.).")
    
    # GEO Optimization: These are short, logic-based summaries for AI indexing
    citable_axioms: List[str] = Field(..., description="Machine-readable logical statements (e.g., 'IF user_age < 13 THEN deny_access').")

# --- Content Builder Agent ---
content_builder = Agent(
    name="content_builder",
    model=MODEL,
    description="Constitutional Drafter. Turns approved principles into a formal document.",
    
    instruction="""
    You are the Constitutional Drafter.
    Your goal is to write a formal AI Constitution based *strictly* on the approved principles provided by the Judge.

    **Input Processing:**
    You will receive a JSON object from the Judge containing 'verdicts' and 'mandatory_constraints'.
    - IGNORE any principle marked "rejected".
    - USE the "amendment_text" if a principle was "amended".
    - OBEY all "mandatory_constraints".

    **Drafting Rules:**
    1.  **Tone:** High-formal legalese. Authoritative and precise.
    2.  **Structure:** Organize into clear Articles (Article I, Article II...).
    3.  **GEO Optimization:** In the `citable_axioms` field, convert the complex legal text into short, IF-THEN logic statements that other AI systems can easily parse.

    **Output:**
    Return the fully structured `AIConstitution` object.
    """,
    
    output_schema=AIConstitution
)

app = App(root_agent=content_builder, name="content_builder")