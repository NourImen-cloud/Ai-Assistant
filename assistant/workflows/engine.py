"""Predefined multi-step workflows."""

from typing import Any, Callable

WorkflowStep = dict[str, Any]
Workflow = list[WorkflowStep]

WORKFLOWS: dict[str, dict[str, Any]] = {
    "dev_environment": {
        "description": "Open VS Code, Terminal, and Chrome for development.",
        "steps": [
            {"tool": "open_application", "args": {"name": "VS Code"}},
            {"tool": "open_application", "args": {"name": "Terminal"}},
            {"tool": "open_application", "args": {"name": "Chrome"}},
        ],
    },
    "research": {
        "description": "Open browser and go to Google.",
        "steps": [
            {"tool": "open_browser", "args": {}},
            {"tool": "navigate", "args": {"url": "https://www.google.com"}},
        ],
    },
    "open_main_project": {
        "description": "Open the user's main project in VS Code (uses saved preference).",
        "steps": [],  # handled dynamically
        "dynamic": True,
    },
}


def _resolve_main_project_steps() -> Workflow:
    from assistant.tools.memory_tools import get_memory_store

    store = get_memory_store()
    main = store.get_preference("main_project")
    if not main:
        raise ValueError(
            "No main project set. Save one first, e.g. "
            "save_preference('main_project', 'AI Scheduler') and save_project(...)."
        )

    project = store.get_project(main)
    if not project:
        raise ValueError(f"Main project '{main}' not found in saved projects.")

    return [
        {"tool": "open_in_vscode", "args": {"path": project["path"]}},
        {"tool": "open_application", "args": {"name": "Chrome"}},
    ]


def list_workflows() -> dict[str, str]:
    lines = []
    for name, wf in WORKFLOWS.items():
        lines.append(f"{name}: {wf['description']}")
    return {"status": "success", "message": "Workflows:\n" + "\n".join(lines)}


def run_workflow(name: str) -> dict[str, str]:
    from assistant.tools.registry import execute_tool

    key = name.strip().lower().replace(" ", "_")
    wf = WORKFLOWS.get(key)
    if not wf:
        available = ", ".join(WORKFLOWS.keys())
        return {"status": "error", "message": f"Unknown workflow '{name}'. Available: {available}"}

    try:
        if wf.get("dynamic"):
            steps = _resolve_main_project_steps()
        else:
            steps = wf["steps"]

        results: list[str] = []
        for step in steps:
            result = execute_tool(step["tool"], step.get("args", {}))
            results.append(f"{step['tool']}: {result.get('message', result)}")
            if result.get("status") == "error":
                return {
                    "status": "error",
                    "message": f"Workflow '{key}' failed at {step['tool']}: {result.get('message')}",
                }

        return {
            "status": "success",
            "message": f"Workflow '{key}' completed:\n" + "\n".join(results),
        }
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "message": f"Workflow failed: {exc}"}
