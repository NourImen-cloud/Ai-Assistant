"""Memory tools backed by local SQLite."""

from assistant.memory.store import MemoryStore

_store = MemoryStore()


def save_preference(key: str, value: str) -> dict[str, str]:
    try:
        _store.set_preference(key, value)
        return {"status": "success", "message": f"Saved preference '{key}' = '{value}'."}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}


def get_preference(key: str) -> dict[str, str]:
    value = _store.get_preference(key)
    if value is None:
        return {"status": "error", "message": f"No preference saved for '{key}'."}
    return {"status": "success", "message": f"{key} = {value}"}


def list_preferences() -> dict[str, str]:
    prefs = _store.list_preferences()
    if not prefs:
        return {"status": "success", "message": "No preferences saved yet."}
    lines = [f"{k}: {v}" for k, v in prefs.items()]
    return {"status": "success", "message": "Preferences:\n" + "\n".join(lines)}


def save_project(name: str, path: str, description: str = "") -> dict[str, str]:
    try:
        _store.save_project(name, path, description)
        return {"status": "success", "message": f"Saved project '{name}' at {path}."}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": str(exc)}


def get_project(name: str) -> dict[str, str]:
    project = _store.get_project(name)
    if not project:
        return {"status": "error", "message": f"No project named '{name}'."}
    msg = f"{project['name']}: {project['path']}"
    if project["description"]:
        msg += f" — {project['description']}"
    return {"status": "success", "message": msg, "path": project["path"]}


def list_projects() -> dict[str, str]:
    projects = _store.list_projects()
    if not projects:
        return {"status": "success", "message": "No projects saved yet."}
    lines = [
        f"{p['name']}: {p['path']}"
        + (f" ({p['description']})" if p["description"] else "")
        for p in projects
    ]
    return {"status": "success", "message": "Projects:\n" + "\n".join(lines)}


def get_memory_store() -> MemoryStore:
    return _store
