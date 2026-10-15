import json
import sys
import threading
from typing import Any
from pathlib import Path

# Add project root to sys.path so 'assistant' package can be imported directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
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

UPLOAD_DIR = PROJECT_ROOT / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


def extract_file_text(file_path: Path, filename: str) -> tuple[str, str]:
    """Extract readable text and metadata summary from uploaded file."""
    suffix = file_path.suffix.lower()
    text = ""
    file_type = "document"

    if suffix == ".pdf":
        file_type = "pdf"
        try:
            import pypdf
            reader = pypdf.PdfReader(str(file_path))
            pages = []
            for idx, page in enumerate(reader.pages[:25]):
                t = page.extract_text() or ""
                if t:
                    pages.append(f"--- Page {idx+1} ---\n{t.strip()}")
            text = "\n\n".join(pages)
        except Exception as e:
            text = f"Failed to extract PDF text: {e}"

    elif suffix in {".docx", ".doc"}:
        file_type = "docx"
        try:
            import docx
            doc = docx.Document(str(file_path))
            paras = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paras)
        except Exception as e:
            text = f"Failed to extract Word document: {e}"

    elif suffix in {".csv", ".tsv"}:
        file_type = "data"
        try:
            import pandas as pd
            sep = "\t" if suffix == ".tsv" else ","
            df = pd.read_csv(str(file_path), sep=sep, nrows=100)
            text = (
                f"Data file with {len(df.columns)} columns: {list(df.columns)}\n"
                f"Preview (first 10 rows):\n{df.head(10).to_string()}\n"
                f"Summary statistics:\n{df.describe().to_string()}"
            )
        except Exception as e:
            try:
                text = file_path.read_text(encoding="utf-8", errors="replace")[:8000]
            except Exception:
                text = f"Failed to parse CSV: {e}"

    elif suffix in {".xlsx", ".xls"}:
        file_type = "excel"
        try:
            import pandas as pd
            df = pd.read_excel(str(file_path), nrows=100)
            text = (
                f"Excel spreadsheet with {len(df.columns)} columns: {list(df.columns)}\n"
                f"Preview:\n{df.head(10).to_string()}"
            )
        except Exception as e:
            text = f"Excel spreadsheet: {filename}. (Could not parse tables: {e})"

    elif suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}:
        file_type = "image"
        text = f"[Image file attached: {filename} saved at {file_path}]"

    else:
        file_type = "code" if suffix in {".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".json", ".sql", ".sh"} else "text"
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            text = f"Could not read text: {e}"

    return text, file_type


class AttachedFile(BaseModel):
    filename: str
    file_path: str
    extracted_text: str | None = None
    file_type: str | None = None
    file_size: int | None = None


class ChatRequest(BaseModel):
    message: str = ""
    files: list[AttachedFile] | None = None


class ChatResponse(BaseModel):
    reply: str
    provider: str


class VoiceResponse(BaseModel):
    text: str
    reply: str


class WorkflowRequest(BaseModel):
    name: str


class UserProfileRequest(BaseModel):
    name: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "provider": agent.provider_label(),
        "model": agent.model,
    }


@app.get("/user/profile")
def get_profile():
    from assistant.agent import get_user_name
    return {"name": get_user_name()}


@app.post("/user/profile")
def set_profile(req: UserProfileRequest):
    new_name = req.name.strip()
    if new_name:
        agent.memory.set_preference("user_name", new_name)
    from assistant.agent import get_user_name
    return {"name": get_user_name()}


def _build_chat_prompt(req: ChatRequest) -> tuple[str, str]:
    """Build full prompt for LLM and a clean display prompt for history."""
    cleaned = (req.message or "").strip()
    if not cleaned and not req.files:
        raise HTTPException(status_code=400, detail="Message or attached file is required.")

    if not req.files:
        return cleaned, cleaned

    file_blocks = []
    file_names = []
    for f in req.files:
        preview = (f.extracted_text or "")[:2000]
        file_names.append(f.filename)
        file_blocks.append(
            f"--- ATTACHED FILE: {f.filename} ---\n"
            f"Type: {f.file_type or 'document'}\n"
            f"Extracted Content:\n{preview}\n"
            f"--- END OF ATTACHED FILE: {f.filename} ---"
        )

    user_prompt = cleaned if cleaned else f"Please examine and analyze the attached file: {', '.join(file_names)}."
    full_message = (
        "\n\n".join(file_blocks)
        + "\n\n(Note: The attached file excerpt is already provided above. Answer and summarize directly from this excerpt — do NOT call read_document or summarize_document again for this file.)"
        + f"\n\nUser Question/Instruction:\n{user_prompt}"
    )

    display_message = (
        f"[📎 {', '.join(file_names)}] {cleaned}" if cleaned else f"[📎 Attached: {', '.join(file_names)}]"
    )
    return full_message, display_message


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file, save it to uploads directory, and extract its content."""
    try:
        clean_filename = Path(file.filename or "attachment.txt").name
        dest_path = UPLOAD_DIR / clean_filename

        # If file exists, generate unique name
        if dest_path.exists():
            import time
            stem = Path(clean_filename).stem
            suffix = Path(clean_filename).suffix
            dest_path = UPLOAD_DIR / f"{stem}_{int(time.time())}{suffix}"

        content = await file.read()
        with open(dest_path, "wb") as f:
            f.write(content)

        extracted_text, file_type = extract_file_text(dest_path, dest_path.name)

        return {
            "status": "success",
            "filename": dest_path.name,
            "original_name": clean_filename,
            "file_path": str(dest_path).replace("\\", "/"),
            "file_size": len(content),
            "file_type": file_type,
            "extracted_text": extracted_text[:8000],
            "total_chars": len(extracted_text),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    full_msg, disp_msg = _build_chat_prompt(req)
    reply = agent.run(full_msg, display_input=disp_msg)
    return ChatResponse(reply=reply, provider=agent.provider_label())


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    """Real-time token streaming via Server-Sent Events (SSE)."""
    full_msg, disp_msg = _build_chat_prompt(req)

    def event_stream():
        try:
            for chunk in agent.run_stream(full_msg, display_input=disp_msg):
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


@app.post("/todos")
def create_todo(data: dict[str, Any]):
    """Create a new todo task."""
    title = data.get("title", "").strip()
    due_date = data.get("due_date", "").strip()
    if not title:
        return {"success": False, "error": "Title required"}
    new_id = agent.memory.add_todo(title, due_date)
    return {"success": True, "id": new_id}


@app.delete("/todos/{todo_id}")
def remove_todo(todo_id: int):
    """Delete a todo task by ID."""
    ok = agent.memory.delete_todo(todo_id)
    return {"success": ok}


@app.post("/todos/{todo_id}/toggle")
def toggle_todo(todo_id: int):
    """Toggle a todo status between pending and completed."""
    with agent.memory._connect() as conn:
        row = conn.execute("SELECT status FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if not row:
            return {"success": False, "error": "Not found"}
        new_status = "pending" if row["status"] == "completed" else "completed"
        conn.execute("UPDATE todos SET status = ? WHERE id = ?", (new_status, todo_id))
    return {"success": True, "status": new_status}


@app.get("/events")
def get_events():
    """Retrieve upcoming calendar events."""
    events = agent.memory.list_events(limit=15)
    return {"events": events}


@app.post("/events")
def create_event(data: dict[str, Any]):
    """Create a new calendar event."""
    title = data.get("title", "").strip()
    date = data.get("date", "").strip()
    time = data.get("time", "").strip()
    notes = data.get("notes", "").strip()
    if not title or not date:
        return {"success": False, "error": "Title and date are required"}
    new_id = agent.memory.add_event(title, date, time, notes)
    return {"success": True, "id": new_id}


@app.delete("/events/{event_id}")
def remove_event(event_id: int):
    """Delete a calendar event by ID."""
    ok = agent.memory.delete_event(event_id)
    return {"success": ok}


@app.get("/system/resources")
def get_system_resources():
    """Retrieve live CPU, RAM, and disk statistics."""
    from assistant.tools.system_tools import system_resource_inspector
    return system_resource_inspector()


@app.post("/workflows/run")
def trigger_workflow(req: WorkflowRequest):
    result = run_workflow(req.name)
    return result


class GmailConfigRequest(BaseModel):
    gmail_address: str
    gmail_app_password: str


class GmailDraftRequest(BaseModel):
    recipient: str
    subject: str
    body: str


@app.get("/gmail/status")
def get_gmail_status():
    """Check whether Gmail is configured and test IMAP connection."""
    from assistant.tools.email_tools import _connect_imap, _get_credentials

    email_addr, app_pw = _get_credentials()
    if not email_addr or not app_pw:
        return {"configured": False, "email": "", "connected": False, "message": "Not configured"}

    mail, err = _connect_imap()
    if err:
        return {"configured": True, "email": email_addr, "connected": False, "message": err}
    try:
        mail.logout()
    except Exception:
        pass
    return {"configured": True, "email": email_addr, "connected": True, "message": "Connected"}


@app.post("/gmail/config")
def set_gmail_config(req: GmailConfigRequest):
    """Save user Gmail address and app password to environment and .env file."""
    import os
    from assistant.config import PROJECT_ROOT

    clean_pw = req.gmail_app_password.strip().replace(" ", "")
    clean_email = req.gmail_address.strip()
    os.environ["GMAIL_ADDRESS"] = clean_email
    os.environ["GMAIL_APP_PASSWORD"] = clean_pw

    env_path = PROJECT_ROOT / ".env"
    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    updated_email = False
    updated_pw = False
    new_lines = []
    for line in lines:
        if line.startswith("GMAIL_ADDRESS="):
            new_lines.append(f"GMAIL_ADDRESS={clean_email}")
            updated_email = True
        elif line.startswith("GMAIL_APP_PASSWORD="):
            new_lines.append(f"GMAIL_APP_PASSWORD={clean_pw}")
            updated_pw = True
        else:
            new_lines.append(line)

    if not updated_email:
        new_lines.append(f"GMAIL_ADDRESS={clean_email}")
    if not updated_pw:
        new_lines.append(f"GMAIL_APP_PASSWORD={clean_pw}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    from assistant.tools.email_tools import _connect_imap

    mail, err = _connect_imap()
    if err:
        return {"success": False, "connected": False, "error": err}
    try:
        mail.logout()
    except Exception:
        pass
    return {"success": True, "connected": True, "email": clean_email}


@app.post("/gmail/disconnect")
def disconnect_gmail():
    """Disconnect Gmail and remove credentials from .env and environment."""
    import os
    from assistant.config import PROJECT_ROOT

    os.environ.pop("GMAIL_ADDRESS", None)
    os.environ.pop("GMAIL_APP_PASSWORD", None)

    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
        new_lines = [
            l for l in lines
            if not l.startswith("GMAIL_ADDRESS=") and not l.startswith("GMAIL_APP_PASSWORD=")
        ]
        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    return {"success": True, "message": "Gmail account disconnected successfully."}



@app.get("/gmail/messages")
def get_gmail_messages(folder: str = "INBOX", limit: int = 10, unread_only: bool = False):
    """Retrieve recent emails from inbox."""
    from assistant.tools.email_tools import list_gmail_messages

    return list_gmail_messages(folder=folder, unread_only=unread_only, limit=limit)


@app.post("/gmail/draft")
def make_gmail_draft(req: GmailDraftRequest):
    """Create draft in Gmail."""
    from assistant.tools.email_tools import create_gmail_draft

    return create_gmail_draft(recipient=req.recipient, subject=req.subject, body=req.body)


@app.post("/gmail/send")
def send_gmail_direct(req: GmailDraftRequest):
    """Send an email immediately."""
    from assistant.tools.email_tools import send_gmail_message

FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")


def main():
    import uvicorn

    uvicorn.run("api.server:app", host=API_HOST, port=API_PORT, reload=False)


if __name__ == "__main__":
    main()
