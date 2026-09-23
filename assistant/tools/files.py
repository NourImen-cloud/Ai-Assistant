"""File and folder tools."""

import os
import subprocess

from assistant.tools.paths import ensure_within_home, resolve_path


def create_folder(name: str, location: str = "desktop") -> dict[str, str]:
    """Create a folder at the given location."""
    try:
        path = ensure_within_home(resolve_path(location, name))
        path.mkdir(parents=True, exist_ok=True)
        return {"status": "success", "message": f"Created folder: {path}"}
    except (OSError, PermissionError, ValueError) as exc:
        return {"status": "error", "message": str(exc)}


def create_file(
    name: str,
    location: str = "desktop",
    content: str = "",
) -> dict[str, str]:
    """Create a text file with optional content."""
    try:
        path = ensure_within_home(resolve_path(location, name))
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return {"status": "error", "message": f"File already exists: {path}"}
        path.write_text(content, encoding="utf-8")
        return {"status": "success", "message": f"Created file: {path}"}
    except (OSError, PermissionError, ValueError) as exc:
        return {"status": "error", "message": str(exc)}


def open_folder(location: str = "desktop", name: str | None = None) -> dict[str, str]:
    """Open a folder in File Explorer."""
    try:
        path = ensure_within_home(resolve_path(location, name))
        if not path.exists():
            return {"status": "error", "message": f"Folder not found: {path}"}
        if not path.is_dir():
            return {"status": "error", "message": f"Not a folder: {path}"}
        os.startfile(path)  # type: ignore[attr-defined]
        return {"status": "success", "message": f"Opened folder: {path}"}
    except (OSError, PermissionError, ValueError) as exc:
        return {"status": "error", "message": str(exc)}


def open_path(path: str) -> dict[str, str]:
    """Open a file or folder with the default Windows association."""
    try:
        resolved = ensure_within_home(resolve_path(path))
        if not resolved.exists():
            return {"status": "error", "message": f"Path not found: {resolved}"}
        os.startfile(resolved)  # type: ignore[attr-defined]
        kind = "folder" if resolved.is_dir() else "file"
        return {"status": "success", "message": f"Opened {kind}: {resolved}"}
    except (OSError, PermissionError, ValueError) as exc:
        return {"status": "error", "message": str(exc)}


def rename_path(
    name: str,
    new_name: str,
    location: str = "desktop",
) -> dict[str, str]:
    """Rename a file or folder."""
    try:
        source = ensure_within_home(resolve_path(location, name))
        destination = ensure_within_home(source.parent / new_name)
        if not source.exists():
            return {"status": "error", "message": f"Path not found: {source}"}
        if destination.exists():
            return {"status": "error", "message": f"Destination already exists: {destination}"}
        source.rename(destination)
        return {"status": "success", "message": f"Renamed {source.name} -> {destination.name}"}
    except (OSError, PermissionError, ValueError) as exc:
        return {"status": "error", "message": str(exc)}


def list_directory(location: str = "desktop", name: str | None = None) -> dict[str, str]:
    """List files and folders in a directory."""
    try:
        path = ensure_within_home(resolve_path(location, name))
        if not path.exists():
            return {"status": "error", "message": f"Folder not found: {path}"}
        if not path.is_dir():
            return {"status": "error", "message": f"Not a folder: {path}"}

        entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        if not entries:
            return {"status": "success", "message": f"{path} is empty."}

        lines = []
        for entry in entries[:100]:
            prefix = "[dir] " if entry.is_dir() else "[file]"
            lines.append(f"{prefix} {entry.name}")

        extra = ""
        if len(entries) > 100:
            extra = f"\n... and {len(entries) - 100} more"

        return {
            "status": "success",
            "message": f"Contents of {path}:\n" + "\n".join(lines) + extra,
        }
    except (OSError, PermissionError, ValueError) as exc:
        return {"status": "error", "message": str(exc)}


def delete_path(
    name: str,
    location: str = "desktop",
    confirm: bool = False,
) -> dict[str, str]:
    """Delete a file or empty folder. Requires confirm=True."""
    if not confirm:
        try:
            path = ensure_within_home(resolve_path(location, name))
            return {
                "status": "needs_confirmation",
                "message": (
                    f"This will permanently delete '{path}'. "
                    "Ask the user to confirm, then call again with confirm=true."
                ),
            }
        except (PermissionError, ValueError) as exc:
            return {"status": "error", "message": str(exc)}

    try:
        path = ensure_within_home(resolve_path(location, name))
        if not path.exists():
            return {"status": "error", "message": f"Path not found: {path}"}

        if path.is_dir():
            path.rmdir()  # empty folders only — safer default
            return {"status": "success", "message": f"Deleted empty folder: {path}"}

        path.unlink()
        return {"status": "success", "message": f"Deleted file: {path}"}
    except OSError as exc:
        return {
            "status": "error",
            "message": f"Could not delete {name}: {exc}. Non-empty folders are not deleted.",
        }
    except (PermissionError, ValueError) as exc:
        return {"status": "error", "message": str(exc)}


def open_in_vscode(path: str) -> dict[str, str]:
    """Open a file or folder in VS Code."""
    try:
        resolved = ensure_within_home(resolve_path(path))
        if not resolved.exists():
            return {"status": "error", "message": f"Path not found: {resolved}"}
        subprocess.Popen(["code", str(resolved)], shell=True)
        return {"status": "success", "message": f"Opened in VS Code: {resolved}"}
    except (OSError, PermissionError, ValueError) as exc:
        return {"status": "error", "message": str(exc)}
