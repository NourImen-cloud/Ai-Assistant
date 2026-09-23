import json
import sys
import threading
from pathlib import Path

# Add project root to sys.path so 'assistant' package can be imported directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from assistant.agent import AssistantAgent
from assistant.config import API_HOST, API_PORT
from assistant.voice.stt import listen
from assistant.voice.tts import speak
from assistant.workflows.engine import WORKFLOWS, run_workflow

app = FastAPI(title="Echo Mind - Personal AI Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = AssistantAgent()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    provider: str


class VoiceResponse(BaseModel):
    text: str
    reply: str


class WorkflowRequest(BaseModel):
    name: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "provider": agent.provider_label(),
        "model": agent.model,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    cleaned = req.message.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    reply = agent.run(cleaned)
    return ChatResponse(reply=reply, provider=agent.provider_label())


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    """Real-time token streaming via Server-Sent Events (SSE)."""
    cleaned = req.message.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    def event_stream():
        try:
            for chunk in agent.run_stream(cleaned):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/reset")
def reset():
    agent.reset()
    return {"status": "ok", "message": "Conversation reset successfully."}


@app.post("/voice", response_model=VoiceResponse)
def voice_command():
    heard = listen()
    if heard.get("status") != "success":
        error_detail = heard.get("message", "Voice input failed.")
        raise HTTPException(status_code=400, detail=error_detail)

    text = heard.get("text", heard.get("message", ""))
    if not text:
        raise HTTPException(status_code=400, detail="No speech transcribed.")

    reply = agent.run(text)

    # Speak output in a non-blocking background thread so HTTP response is instant!
    try:
        threading.Thread(target=speak, args=(reply,), daemon=True).start()
    except Exception:
        pass

    return VoiceResponse(text=text, reply=reply)


@app.get("/history")
def get_history(limit: int = 30):
    """Retrieve recent conversation history from persistent memory."""
    messages = agent.memory.recent_messages(limit=limit)
    return {"history": messages}


@app.get("/memory")
def get_memory():
    """Retrieve saved preferences and projects."""
    prefs = agent.memory.list_preferences()
    projects = agent.memory.list_projects()
    return {"preferences": prefs, "projects": projects}


@app.get("/workflows")
def list_available_workflows():
    """List available automated workflows."""
    return {
        "workflows": [
            {"id": key, "name": key.replace("_", " ").title(), "description": val.get("description", "")}
            for key, val in WORKFLOWS.items()
        ]
    }


@app.get("/todos")
def get_todos():
    """Retrieve personal todos."""
    todos = agent.memory.list_todos(status="all")
    return {"todos": todos}


@app.get("/events")
def get_events():
    """Retrieve upcoming calendar events."""
    events = agent.memory.list_events(limit=15)
    return {"events": events}


@app.get("/system/resources")
def get_system_resources():
    """Retrieve live CPU, RAM, and disk statistics."""
    from assistant.tools.system_tools import system_resource_inspector
    return system_resource_inspector()


@app.post("/workflows/run")
def trigger_workflow(req: WorkflowRequest):
    result = run_workflow(req.name)
    return result


def main():
    import uvicorn

    uvicorn.run("api.server:app", host=API_HOST, port=API_PORT, reload=False)


if __name__ == "__main__":
    main()
