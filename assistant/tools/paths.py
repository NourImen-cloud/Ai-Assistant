"""Safe path resolution for file tools."""

from pathlib import Path

USER_HOME = Path.home()

SPECIAL_LOCATIONS: dict[str, Path] = {
    "desktop": USER_HOME / "Desktop",
    "documents": USER_HOME / "Documents",
    "downloads": USER_HOME / "Downloads",
    "pictures": USER_HOME / "Pictures",
    "music": USER_HOME / "Music",
    "videos": USER_HOME / "Videos",
    "home": USER_HOME,
}


def resolve_location(location: str | None) -> Path:
    """Resolve a special location name or absolute/relative path."""
    if not location or not location.strip():
        return SPECIAL_LOCATIONS["desktop"]

    key = location.strip().lower()
    if key in SPECIAL_LOCATIONS:
        return SPECIAL_LOCATIONS[key]

    raw_path = Path(location).expanduser()
    # If relative path exists in current working directory, resolve it directly
    if not raw_path.is_absolute() and raw_path.exists():
        return raw_path.resolve()

    if not raw_path.is_absolute():
        desktop_target = (SPECIAL_LOCATIONS["desktop"] / raw_path).resolve()
        if desktop_target.exists():
            return desktop_target
        cwd_target = raw_path.resolve()
        if cwd_target.exists():
            return cwd_target
        return desktop_target

    return raw_path.resolve()


def resolve_path(location: str | None, name: str | None = None) -> Path:
    """Build a full path from a location and optional name."""
    base = resolve_location(location)
    if name:
        return (base / name).resolve()
    return base


def ensure_within_home(path: Path) -> Path:
    """Reject paths outside the user's home directory."""
    resolved = path.resolve()
    try:
        resolved.relative_to(USER_HOME.resolve())
    except ValueError as exc:
        raise PermissionError(
            f"Path must be inside your user folder ({USER_HOME}): {resolved}"
        ) from exc
    return resolved
