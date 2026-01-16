import logging
import os
import json
import warnings
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

# Suppress experimental warnings for A2A components
warnings.filterwarnings("ignore", message=r".*\[EXPERIMENTAL\].*", category=UserWarning)

# Suppress runner app name mismatch warning
logging.getLogger("google_adk.google.adk.runners").setLevel(logging.ERROR)
logging.getLogger("google.adk.runners").setLevel(logging.ERROR)

# Suppress Google Auth warnings
warnings.filterwarnings("ignore", message=".*Your application has authenticated using end user credentials.*")

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, export
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from pydantic import BaseModel

from app.agent import app as adk_app

class Feedback(BaseModel):
    score: float
    text: str | None = None
    run_id: str | None = None
    user_id: str | None = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

provider = TracerProvider()
processor = export.SimpleSpanProcessor(ConsoleSpanExporter())
trace.set_tracer_provider(provider)

runner = Runner(
    app=adk_app,
    artifact_service=InMemoryArtifactService(),
    session_service=InMemorySessionService(),
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimpleChatRequest(BaseModel):
    message: str
    user_id: str = "test_user"
    session_id: str = "test_session"

@app.post("/api/chat_stream")
async def chat_stream(request: SimpleChatRequest):
    """Streaming chat endpoint."""
    try:
        session = await runner.session_service.get_session(
            session_id=request.session_id, app_name=adk_app.name, user_id=request.user_id
        )
    except Exception:
        session = None
    if not session:
        session = await runner.session_service.create_session(
            app_name=adk_app.name,
            user_id=request.user_id,
            session_id=request.session_id,
        )

    user_msg = genai_types.Content(
        role="user", parts=[genai_types.Part.from_text(text=request.message)]
    )

    async def event_generator():
        final_text = ""
        content_builder_events = []
        
        async for event in runner.run_async(
            user_id=request.user_id, session_id=session.id, new_message=user_msg
        ):
            # Send progress updates based on which agent is active
            if event.author == "researcher":
                 yield json.dumps({"type": "progress", "text": "🔍 Researcher is gathering information..."}) + "\n"
            elif event.author == "judge":
                 yield json.dumps({"type": "progress", "text": "⚖️ Judge is evaluating findings..."}) + "\n"
            elif event.author == "content_builder":
                 yield json.dumps({"type": "progress", "text": "✍️ Content Builder is writing the content..."}) + "\n"
                 # Collect content_builder events separately
                 if event.content and event.content.parts:
                     content_builder_events.append(event)

            # Accumulate final text from all events
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        final_text += part.text

        # Get the final session to access the state
        final_session = await runner.session_service.get_session(
            session_id=request.session_id, app_name=adk_app.name, user_id=request.user_id
        )
        
        # Priority 1: Try to get content from session state (content_output)
        content_output = None
        if final_session and final_session.state:
            content_output = final_session.state.get("content_output")
            print(f"[SERVER] Session state content_output: {content_output is not None} (length: {len(content_output) if content_output else 0})")
            
        # Priority 2: If no state, try the last content_builder event
        if not content_output and content_builder_events:
            print(f"[SERVER] No state content, checking {len(content_builder_events)} content_builder events")
            last_event = content_builder_events[-1]
            if last_event.content and last_event.content.parts:
                content_output = last_event.content.parts[0].text
                print(f"[SERVER] Using last event content (length: {len(content_output) if content_output else 0})")
        
        print(f"[SERVER] Final accumulated text length: {len(final_text)}")
        print(f"[SERVER] Content output type: {type(content_output)}")
        print(f"[SERVER] Content output value: {content_output}")
        
        # Priority 3: Fall back to accumulated text
        # Handle both string and dict content from agents
        if isinstance(content_output, dict):
            # If content_builder returns JSON, extract the main content
            # Look for common keys that might contain the main content
            if 'constitution' in content_output:
                result_text = content_output['constitution']
            elif 'content' in content_output:
                result_text = content_output['content']
            elif 'document' in content_output:
                result_text = content_output['document']
            elif 'text' in content_output:
                result_text = content_output['text']
            else:
                # If no obvious content key, convert the whole dict to JSON string
                result_text = json.dumps(content_output, indent=2)
        else:
            result_text = content_output if content_output else final_text.strip()
        
        # Ensure result_text is a string and handle None case
        if result_text is None:
            result_text = "Error: No content generated"
        elif not isinstance(result_text, str):
            result_text = str(result_text) if result_text else "Error: No content generated"
        
        # Debug logging with safe string handling
        print(f"[SERVER] Final content length: {len(result_text)}")
        print(f"[SERVER] Content type: {type(result_text)}")
        print(f"[SERVER] Content preview: {result_text[:200] if len(result_text) > 0 else 'EMPTY'}...")
        
        # Send final result
        yield json.dumps({"type": "result", "text": result_text}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    logger.info(f"Feedback received: {feedback.model_dump()}")
    return {"status": "success"}

# Mount frontend from the copied location
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)