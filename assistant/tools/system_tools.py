"""System diagnostic, performance monitoring, and project scaffolding tools."""

import os
import shutil
from pathlib import Path
from typing import Any

from assistant.tools.paths import ensure_within_home, resolve_path


def system_resource_inspector() -> dict[str, Any]:
    """Inspect real-time CPU, RAM, disk usage, and identify top memory-consuming processes."""
    try:
        import psutil

        cpu_percent = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory()
        mem_used_gb = round((mem.total - mem.available) / (1024**3), 2)
        mem_total_gb = round(mem.total / (1024**3), 2)

        # Disks
        disk_stats = []
        for partition in psutil.disk_partitions(all=False):
            if "cdrom" in partition.opts or not partition.fstype:
                continue
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                free_gb = round(usage.free / (1024**3), 1)
                total_gb = round(usage.total / (1024**3), 1)
                disk_stats.append(f"{partition.device} ({partition.mountpoint}): {usage.percent}% used ({free_gb} GB free of {total_gb} GB)")
            except (PermissionError, OSError):
                continue

        # Top 5 memory-hungry processes
        processes = []
        for p in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                mem_mb = round(p.info["memory_info"].rss / (1024**2), 1)
                processes.append((p.info["name"], mem_mb, p.info["pid"]))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda x: x[1], reverse=True)
        top_procs = processes[:5]
        proc_lines = [f"- {name} (PID {pid}): {mb} MB" for name, mb, pid in top_procs]

        report = (
            f"System Hardware Diagnostic:\n"
            f"- CPU Usage: {cpu_percent}%\n"
            f"- RAM Usage: {mem.percent}% ({mem_used_gb} GB used / {mem_total_gb} GB total)\n"
            f"- Storage:\n  " + "\n  ".join(disk_stats) + "\n\n"
            f"Top 5 Memory-Intensive Processes:\n" + "\n".join(proc_lines)
        )

        return {
            "status": "success",
            "message": report,
            "cpu_percent": cpu_percent,
            "ram_percent": mem.percent,
            "ram_used_gb": mem_used_gb,
            "ram_total_gb": mem_total_gb,
        }
    except Exception as exc:
        return {"status": "error", "message": f"Failed to inspect system resources: {exc}"}


def clean_temp_files(dry_run: bool = True) -> dict[str, Any]:
    """Scan and safely clean Windows %TEMP% files to reclaim disk space."""
    temp_dir_str = os.environ.get("TEMP") or os.environ.get("TMP")
    if not temp_dir_str or not os.path.exists(temp_dir_str):
        return {"status": "error", "message": "Could not locate Windows TEMP directory."}

    temp_path = Path(temp_dir_str)
    total_bytes = 0
    file_count = 0
    cleaned_bytes = 0
    cleaned_count = 0

    try:
        for item in temp_path.iterdir():
            try:
                if item.is_file():
                    size = item.stat().st_size
                    total_bytes += size
                    file_count += 1
                    if not dry_run:
                        item.unlink(missing_ok=True)
                        cleaned_bytes += size
                        cleaned_count += 1
                elif item.is_dir():
                    # Check directory size
                    dir_size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                    total_bytes += dir_size
                    file_count += 1
                    if not dry_run:
                        shutil.rmtree(item, ignore_errors=True)
                        cleaned_bytes += dir_size
                        cleaned_count += 1
            except (PermissionError, OSError):
                # Active locked files in use by Windows are skipped
                continue

        reclaimable_mb = round(total_bytes / (1024**2), 2)
        if dry_run:
            return {
                "status": "success",
                "message": (
                    f"Temp Scan Complete: Found {file_count} items ({reclaimable_mb} MB) in {temp_path}.\n"
                    f"To clean these files, call clean_temp_files with dry_run=false."
                ),
                "reclaimable_mb": reclaimable_mb,
            }

        freed_mb = round(cleaned_bytes / (1024**2), 2)
        return {
            "status": "success",
            "message": f"Cleaned {cleaned_count} items, successfully freed {freed_mb} MB of disk space.",
            "freed_mb": freed_mb,
        }
    except Exception as exc:
        return {"status": "error", "message": f"Failed to clean temp files: {exc}"}


def scaffold_code_project(
    project_type: str = "fastapi", project_name: str = "my_project", location: str = "desktop"
) -> dict[str, Any]:
    """Scaffold a production-ready boilerplate codebase (FastAPI, React Vite, or Python CLI)."""
    try:
        base_dir = ensure_within_home(resolve_path(location, project_name))
        base_dir.mkdir(parents=True, exist_ok=True)

        p_type = project_type.lower().strip()
        created_files = []

        if "fastapi" in p_type or "api" in p_type:
            main_code = '''from fastapi import FastAPI\n\napp = FastAPI(title="Generated API")\n\n@app.get("/")\ndef root():\n    return {"message": "Hello from FastAPI!"}\n\nif __name__ == "__main__":\n    import uvicorn\n    uvicorn.run(app, host="127.0.0.1", port=8000)\n'''
            reqs = "fastapi>=0.110.0\nuvicorn>=0.27.0\npydantic>=2.0.0\n"
            docker = "FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD [\"python\", \"main.py\"]\n"

            (base_dir / "main.py").write_text(main_code, encoding="utf-8")
            (base_dir / "requirements.txt").write_text(reqs, encoding="utf-8")
            (base_dir / "Dockerfile").write_text(docker, encoding="utf-8")
            (base_dir / ".env").write_text("PORT=8000\nDEBUG=True\n", encoding="utf-8")
            (base_dir / "README.md").write_text(f"# {project_name}\n\nFastAPI service created by Echo Mind.\n", encoding="utf-8")
            created_files = ["main.py", "requirements.txt", "Dockerfile", ".env", "README.md"]

        elif "react" in p_type or "frontend" in p_type:
            pkg = f'{{\n  "name": "{project_name}",\n  "private": true,\n  "version": "1.0.0",\n  "type": "module",\n  "scripts": {{\n    "dev": "vite",\n    "build": "vite build"\n  }},\n  "dependencies": {{\n    "react": "^18.3.1",\n    "react-dom": "^18.3.1"\n  }},\n  "devDependencies": {{\n    "@vitejs/plugin-react": "^4.3.1",\n    "vite": "^5.4.0"\n  }}\n}}\n'
            src_dir = base_dir / "src"
            src_dir.mkdir(exist_ok=True)
            app_jsx = 'export default function App() {\n  return (\n    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>\n      <h1>Welcome to your new React App!</h1>\n    </div>\n  );\n}\n'
            main_jsx = 'import React from "react";\nimport ReactDOM from "react-dom/client";\nimport App from "./App";\n\nReactDOM.createRoot(document.getElementById("root")).render(<App />);\n'
            index_html = '<!DOCTYPE html>\n<html>\n<head><title>React App</title></head>\n<body><div id="root"></div><script type="module" src="/src/main.jsx"></script></body>\n</html>\n'

            (base_dir / "package.json").write_text(pkg, encoding="utf-8")
            (base_dir / "index.html").write_text(index_html, encoding="utf-8")
            (src_dir / "App.jsx").write_text(app_jsx, encoding="utf-8")
            (src_dir / "main.jsx").write_text(main_jsx, encoding="utf-8")
            created_files = ["package.json", "index.html", "src/App.jsx", "src/main.jsx"]

        else:
            cli_code = '''import sys\n\ndef main():\n    print("Welcome to your Python CLI!")\n\nif __name__ == "__main__":\n    main()\n'''
            (base_dir / "cli.py").write_text(cli_code, encoding="utf-8")
            (base_dir / "requirements.txt").write_text("# Dependencies\n", encoding="utf-8")
            (base_dir / "README.md").write_text(f"# {project_name}\n\nPython CLI created by Echo Mind.\n", encoding="utf-8")
            created_files = ["cli.py", "requirements.txt", "README.md"]

        return {
            "status": "success",
            "message": f"Successfully scaffolded '{project_type}' project at: {base_dir}\nCreated: {', '.join(created_files)}",
            "path": str(base_dir),
            "files": created_files,
        }
    except Exception as exc:
        return {"status": "error", "message": f"Failed to scaffold project: {exc}"}
