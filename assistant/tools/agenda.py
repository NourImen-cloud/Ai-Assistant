"""Agenda, Todo task manager, calendar scheduling, and email drafting tools."""

from datetime import datetime
from typing import Any

from assistant.tools.memory_tools import get_memory_store


def manage_todo(
    action: str = "list",
    title: str = "",
    task_id: int | None = None,
    due_date: str = "",
) -> dict[str, Any]:
    """Manage your personal to-do tasks (add, list, complete, delete)."""
    store = get_memory_store()
    act = action.strip().lower()

    if act == "add":
        if not title.strip():
            return {"status": "error", "message": "Task title cannot be empty."}
        tid = store.add_todo(title, due_date)
        return {"status": "success", "message": f"Added task #{tid}: '{title}'" + (f" (Due: {due_date})" if due_date else "")}

    elif act in {"complete", "done", "finish"}:
        if task_id is None:
            if title.strip():
                all_todos = store.list_todos(status="all")
                target = title.strip().lower()
                for t in all_todos:
                    if target in t["title"].lower():
                        store.complete_todo(t["id"])
                        return {"status": "success", "message": f"Completed task #{t['id']}: '{t['title']}'."}
                return {"status": "error", "message": f"Could not find any task matching '{title}'."}
            return {"status": "error", "message": "task_id or title is required to complete a task."}
        ok = store.complete_todo(task_id)
        if ok:
            return {"status": "success", "message": f"Completed task #{task_id}."}
        return {"status": "error", "message": f"Task #{task_id} not found."}

    elif act in {"delete", "remove"}:
        if task_id is None:
            if title.strip():
                all_todos = store.list_todos(status="all")
                target = title.strip().lower()
                for t in all_todos:
                    if target in t["title"].lower():
                        store.delete_todo(t["id"])
                        return {"status": "success", "message": f"Deleted task #{t['id']}: '{t['title']}'."}
                return {"status": "error", "message": f"Could not find any task matching '{title}'."}
            return {"status": "error", "message": "task_id or title is required to delete a task."}
        ok = store.delete_todo(task_id)
        if ok:
            return {"status": "success", "message": f"Deleted task #{task_id}."}
        return {"status": "error", "message": f"Task #{task_id} not found."}

    else:  # list
        todos = store.list_todos(status="all")
        if not todos:
            return {"status": "success", "message": "Your to-do list is currently empty."}
        lines = []
        for t in todos:
            status_symbol = "[✓]" if t["status"] == "completed" else "[ ]"
            due_str = f" (Due: {t['due_date']})" if t.get("due_date") else ""
            lines.append(f"{status_symbol} #{t['id']}: {t['title']}{due_str}")
        return {"status": "success", "message": "To-Do Tasks:\n" + "\n".join(lines), "todos": todos}


def manage_calendar(
    action: str = "list",
    title: str = "",
    date: str = "",
    time: str = "",
    notes: str = "",
    event_id: int | None = None,
) -> dict[str, Any]:
    """Manage upcoming calendar appointments, meetings, and deadlines (add, list, delete)."""
    store = get_memory_store()
    act = action.strip().lower()

    if act == "add":
        if not title.strip() or not date.strip():
            return {"status": "error", "message": "Both title and date are required to schedule an event."}
        eid = store.add_event(title, date, time, notes)
        time_str = f" at {time}" if time else ""
        return {"status": "success", "message": f"Scheduled event #{eid}: '{title}' on {date}{time_str}."}

    elif act in {"delete", "remove"}:
        if event_id is None:
            if title.strip():
                all_events = store.list_events(limit=50)
                target = title.strip().lower()
                for e in all_events:
                    if target in e["title"].lower():
                        store.delete_event(e["id"])
                        return {"status": "success", "message": f"Deleted event #{e['id']}: '{e['title']}'."}
                return {"status": "error", "message": f"Could not find any event matching '{title}'."}
            return {"status": "error", "message": "event_id or title is required to delete an event."}
        ok = store.delete_event(event_id)
        if ok:
            return {"status": "success", "message": f"Deleted event #{event_id}."}
        return {"status": "error", "message": f"Event #{event_id} not found."}

    else:  # list
        events = store.list_events(limit=15)
        if not events:
            return {"status": "success", "message": "No upcoming calendar events scheduled."}
        lines = []
        for e in events:
            time_part = f" @ {e['time']}" if e.get("time") else ""
            note_part = f" — {e['notes']}" if e.get("notes") else ""
            lines.append(f"📅 #{e['id']}: {e['date']}{time_part} | {e['title']}{note_part}")
        return {"status": "success", "message": "Upcoming Calendar Events:\n" + "\n".join(lines), "events": events}


def _get_user_name() -> str:
    try:
        from assistant.tools.memory_tools import get_memory_store
        name = get_memory_store().get_preference("user_name")
        if name:
            return name
        import getpass
        return getpass.getuser().capitalize()
    except Exception:
        return "User"


def draft_email(
    recipient: str,
    subject: str,
    key_points: str,
    tone: str = "professional",
) -> dict[str, Any]:
    """Draft a formatted email with a specified tone (professional, friendly, concise, or assertive)."""
    user_name = _get_user_name()
    greeting = f"Dear {recipient}," if recipient else "Hello,"
    signoff = f"Best regards,\n{user_name}"

    points_list = [p.strip() for p in key_points.split("\n") if p.strip()]
    if not points_list:
        points_list = [key_points.strip()]

    tone_guidance = {
        "friendly": "I hope you are doing well!",
        "concise": "I am reaching out regarding the following update:",
        "assertive": "Please find below the immediate action items:",
        "professional": "I hope this email finds you well.",
    }.get(tone.lower(), "I hope this email finds you well.")

    body_bullets = "\n".join([f"- {pt}" for pt in points_list])

    formatted_email = (
        f"Subject: {subject}\n\n"
        f"{greeting}\n\n"
        f"{tone_guidance}\n\n"
        f"{body_bullets}\n\n"
        f"Please let me know if you need any additional details.\n\n"
        f"{signoff}"
    )

    return {
        "status": "success",
        "message": f"Drafted {tone} email to '{recipient}':\n\n{formatted_email}",
        "draft": formatted_email,
    }


def get_daily_briefing() -> dict[str, Any]:
    """Retrieve an aggregated morning/daily briefing: date, pending tasks, events, and PC health."""
    now_str = datetime.now().strftime("%A, %B %d, %Y — %I:%M %p")
    store = get_memory_store()

    # Tasks
    todos = store.list_todos(status="pending")
    todo_lines = [f"- #{t['id']}: {t['title']}" for t in todos[:5]]
    todos_summary = "\n".join(todo_lines) if todo_lines else "No pending tasks."

    # Events
    events = store.list_events(limit=5)
    event_lines = [f"- {e['date']} ({e.get('time') or 'All day'}): {e['title']}" for e in events]
    events_summary = "\n".join(event_lines) if event_lines else "No upcoming events scheduled."

    # System Health
    sys_summary = "System resources normal."
    try:
        import psutil

        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        sys_summary = f"CPU: {cpu}% | RAM: {ram}%"
    except Exception:
        pass

    briefing = (
        f"☀️ Daily Briefing for {_get_user_name()}\n"
        f"⏰ {now_str}\n\n"
        f"📋 Pending Tasks ({len(todos)} total):\n{todos_summary}\n\n"
        f"📅 Upcoming Agenda:\n{events_summary}\n\n"
        f"💻 PC Status: {sys_summary}"
    )

    return {"status": "success", "message": briefing}
