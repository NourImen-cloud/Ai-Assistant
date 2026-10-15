from typing import Any, Callable

from assistant.tools import (
    agenda,
    analytics,
    applications,
    automation,
    browser,
    documents,
    email_tools,
    files,
    memory_tools,
    research,
    system_tools,
    websites,
)
from assistant.workflows.engine import list_workflows, run_workflow

ToolHandler = Callable[..., dict[str, str]]

TOOL_HANDLERS: dict[str, ToolHandler] = {
    "open_application": applications.open_application,
    "close_application": applications.close_application,
    "open_website": websites.open_website,
    "open_website_in_chrome": websites.open_website_in_chrome,
    "create_folder": files.create_folder,
    "create_file": files.create_file,
    "open_folder": files.open_folder,
    "open_path": files.open_path,
    "open_in_vscode": files.open_in_vscode,
    "rename_path": files.rename_path,
    "list_directory": files.list_directory,
    "search_local_files": files.search_local_files,
    "delete_path": files.delete_path,
    "type_text": automation.type_text,
    "press_hotkey": automation.press_hotkey,
    "move_mouse": automation.move_mouse,
    "click": automation.click,
    "take_screenshot": automation.take_screenshot,
    "get_screen_size": automation.get_screen_size,
    "open_browser": browser.open_browser,
    "navigate": browser.navigate,
    "search_google": browser.search_google,
    "search_youtube": browser.search_youtube,
    "click_element": browser.click_element,
    "type_into_field": browser.type_into_field,
    "get_page_content": browser.get_page_content,
    "close_browser": browser.close_browser,
    "save_preference": memory_tools.save_preference,
    "get_preference": memory_tools.get_preference,
    "list_preferences": memory_tools.list_preferences,
    "save_project": memory_tools.save_project,
    "get_project": memory_tools.get_project,
    "list_projects": memory_tools.list_projects,
    "list_workflows": list_workflows,
    "run_workflow": run_workflow,
    # New Intelligence & Productivity Tools
    "read_document": documents.read_document,
    "summarize_document": documents.summarize_document,
    "search_documents_in_folder": documents.search_documents_in_folder,
    "deep_web_research": research.deep_web_research,
    "compare_products_or_options": research.compare_products_or_options,
    "academic_search": research.academic_search,
    "analyze_tabular_data": analytics.analyze_tabular_data,
    "generate_chart": analytics.generate_chart,
    "system_resource_inspector": system_tools.system_resource_inspector,
    "clean_temp_files": system_tools.clean_temp_files,
    "scaffold_code_project": system_tools.scaffold_code_project,
    "manage_todo": agenda.manage_todo,
    "manage_calendar": agenda.manage_calendar,
    "draft_email": agenda.draft_email,
    "get_daily_briefing": agenda.get_daily_briefing,
    # Gmail Integration
    "list_gmail_messages": email_tools.list_gmail_messages,
    "read_gmail_message": email_tools.read_gmail_message,
    "create_gmail_draft": email_tools.create_gmail_draft,
    "send_gmail_message": email_tools.send_gmail_message,
}

LOCATION_HINT = "Location: desktop, documents, downloads, or absolute path."

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": (
                "Launch a desktop application on the user's Windows computer. "
                f"Known apps: {', '.join(applications.list_applications())}. "
                "You can also pass other application names."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Application name, e.g. 'Chrome', 'VS Code', 'Calculator'.",
                    }
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "close_application",
            "description": (
                "Close a running known application. "
                "Cannot close File Explorer. "
                f"Known apps: {', '.join(applications.list_applications())}."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Application name to close.",
                    }
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "Open a website or URL in the default web browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Website URL or domain, e.g. 'google.com' or 'https://github.com'.",
                    }
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_website_in_chrome",
            "description": "Open a website or URL specifically in Google Chrome.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Website URL or domain to open in Chrome.",
                    }
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_folder",
            "description": f"Create a folder. {LOCATION_HINT}",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Folder name."},
                    "location": {
                        "type": "string",
                        "description": "Where to create it. Default: desktop.",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": f"Create a new text file. Fails if it already exists. {LOCATION_HINT}",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "File name including extension."},
                    "location": {
                        "type": "string",
                        "description": "Where to create it. Default: desktop.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Optional initial file contents.",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_folder",
            "description": f"Open a folder in File Explorer. {LOCATION_HINT}",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Base location. Default: desktop.",
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional subfolder name under location.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_path",
            "description": f"Open a file or folder with the default app. {LOCATION_HINT}",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute path, special location, or path under desktop.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_in_vscode",
            "description": f"Open a file or folder in VS Code. {LOCATION_HINT}",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to open in VS Code.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rename_path",
            "description": f"Rename a file or folder. {LOCATION_HINT}",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Current file or folder name."},
                    "new_name": {"type": "string", "description": "New name."},
                    "location": {
                        "type": "string",
                        "description": "Parent location. Default: desktop.",
                    },
                },
                "required": ["name", "new_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": f"List files and folders in a directory. {LOCATION_HINT}",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Base location. Default: desktop.",
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional subfolder name.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_local_files",
            "description": (
                "Search for files and folders on the user's PC by name, extension, or pattern. "
                "Use this whenever the user wants to find, locate, or search for files locally (e.g. 'find my report', 'search for csv files')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "File or folder name pattern to look for.",
                    },
                    "location": {
                        "type": "string",
                        "description": "'all' (Desktop, Documents, Downloads), 'desktop', 'documents', 'downloads', or a folder path.",
                    },
                    "file_type": {
                        "type": "string",
                        "description": "Optional extension filter, e.g. '.pdf', '.csv', '.xlsx', '.py', '.txt'.",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Max matching files to return. Default 15.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_path",
            "description": (
                "Delete a file or an empty folder. "
                "Always call first with confirm=false so the user can approve. "
                "Only call with confirm=true after the user explicitly confirms. "
                f"{LOCATION_HINT}"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "File or folder name."},
                    "location": {
                        "type": "string",
                        "description": "Parent location. Default: desktop.",
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Must be true only after user confirmation.",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text into the currently focused window using the keyboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type."},
                    "interval": {
                        "type": "number",
                        "description": "Delay between keystrokes in seconds. Default 0.02.",
                    },
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "press_hotkey",
            "description": (
                "Press a keyboard key or shortcut. "
                "Use '+' between keys, e.g. 'enter', 'ctrl+c', 'ctrl+s', 'win+e', 'alt+tab'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "string",
                        "description": "Key or hotkey combination.",
                    }
                },
                "required": ["keys"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "move_mouse",
            "description": "Move the mouse cursor to screen coordinates. Use get_screen_size first if unsure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "X coordinate in pixels."},
                    "y": {"type": "integer", "description": "Y coordinate in pixels."},
                    "duration": {
                        "type": "number",
                        "description": "Move duration in seconds. Default 0.3.",
                    },
                },
                "required": ["x", "y"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click",
            "description": "Click the mouse at optional coordinates, or at the current position.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "Optional X coordinate."},
                    "y": {"type": "integer", "description": "Optional Y coordinate."},
                    "button": {
                        "type": "string",
                        "enum": ["left", "right", "middle"],
                        "description": "Mouse button. Default left.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Capture the full screen and save a PNG screenshot.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Optional PNG filename.",
                    },
                    "location": {
                        "type": "string",
                        "description": "Optional save location. Default: project screenshots folder.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_screen_size",
            "description": "Get the primary screen resolution in pixels.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_browser",
            "description": "Launch a Playwright-controlled Chromium browser for automation.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "navigate",
            "description": "Navigate the automated browser to a URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL or domain to open."},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_google",
            "description": "Open Google and search for a query in the automated browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_youtube",
            "description": "Search YouTube for a query in the automated browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click_element",
            "description": "Click an element in the automated browser using a CSS selector.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector."},
                },
                "required": ["selector"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_into_field",
            "description": "Type text into an input field in the automated browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector."},
                    "text": {"type": "string", "description": "Text to type."},
                },
                "required": ["selector", "text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_page_content",
            "description": "Read the visible text content of the current browser page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_chars": {
                        "type": "integer",
                        "description": "Max characters to return. Default 3000.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "close_browser",
            "description": "Close the automated Playwright browser.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_preference",
            "description": "Save a user preference to memory, e.g. main_project = AI Scheduler.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_preference",
            "description": "Retrieve a saved user preference.",
            "parameters": {
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_preferences",
            "description": "List all saved user preferences.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_project",
            "description": "Save a project name and folder path to memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "path": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["name", "path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_project",
            "description": "Get a saved project's path by name.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_projects",
            "description": "List all saved projects.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_workflows",
            "description": "List predefined multi-step workflows the assistant can run.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_workflow",
            "description": (
                "Run a predefined workflow by name. "
                "Examples: dev_environment, research, open_main_project."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Workflow name."},
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_document",
            "description": "Read content from a local PDF, Word docx, text, code, or markdown file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path or name on desktop/documents."},
                    "max_chars": {"type": "integer", "description": "Maximum characters to return. Default 5000."},
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_document",
            "description": "Read a local document and prepare an executive summary with key takeaways.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to PDF, docx, or text document."},
                    "focus_topic": {"type": "string", "description": "Optional specific topic or questions to focus on."},
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_documents_in_folder",
            "description": "Search for text or keywords across local documents in a folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_path": {"type": "string", "description": "Folder location, default 'documents'."},
                    "query": {"type": "string", "description": "Text or keyword to search for."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "deep_web_research",
            "description": "Perform headless web research on any topic, extracting key facts and sources without browser windows.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Research question or query."},
                    "max_sources": {"type": "integer", "description": "Number of sources to synthesize, default 3."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_products_or_options",
            "description": "Compare products, tech stacks, or options using multi-source web research.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to compare (e.g. 'RTX 4070 vs RX 7800 XT')."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "academic_search",
            "description": (
                "Search for academic papers, research articles, and scholarly publications on a topic. "
                "Uses headless web search biased toward arxiv, Google Scholar, Semantic Scholar, PubMed, IEEE, and ACM. "
                "No browser window is opened. Use this for research papers, academic summaries, and state-of-the-art findings."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Research topic or paper search query."},
                    "max_sources": {"type": "integer", "description": "Number of papers to find, default 5."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_tabular_data",
            "description": "Analyze a CSV or Excel dataset, returning dimensions, columns, and statistical summaries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to CSV or Excel file."},
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_chart",
            "description": "Plot and save a chart (bar, line, scatter, hist, pie) from a CSV or Excel file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to CSV or Excel file."},
                    "chart_type": {"type": "string", "enum": ["bar", "line", "scatter", "hist", "pie"]},
                    "x_col": {"type": "string", "description": "Column name for X axis or categories."},
                    "y_col": {"type": "string", "description": "Column name for Y axis or values."},
                    "title": {"type": "string", "description": "Optional chart title."},
                },
                "required": ["file_path", "chart_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "system_resource_inspector",
            "description": "Inspect CPU, RAM, disk partitions, and top memory-consuming processes.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clean_temp_files",
            "description": "Scan and clean Windows %TEMP% files to free up disk space.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dry_run": {"type": "boolean", "description": "If true, only calculate reclaimable space. Set false to delete."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scaffold_code_project",
            "description": "Generate a boilerplate starter codebase (FastAPI, React Vite, or Python CLI).",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_type": {"type": "string", "description": "'fastapi', 'react', or 'cli'."},
                    "project_name": {"type": "string", "description": "Name for the project directory."},
                    "location": {"type": "string", "description": "Parent location. Default 'desktop'."},
                },
                "required": ["project_type", "project_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "manage_todo",
            "description": "Manage personal to-do tasks (add, list, complete, delete).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["add", "list", "complete", "delete"]},
                    "title": {"type": "string", "description": "Task description (for add)."},
                    "task_id": {"type": "integer", "description": "Task ID (for complete or delete)."},
                    "due_date": {"type": "string", "description": "Optional due date."},
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "manage_calendar",
            "description": "Manage upcoming meetings, deadlines, and events (add, list, delete).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["add", "list", "delete"]},
                    "title": {"type": "string", "description": "Event title."},
                    "date": {"type": "string", "description": "Date, e.g. '2026-09-25' or 'Tomorrow'."},
                    "time": {"type": "string", "description": "Optional time, e.g. '14:00' or '2 PM'."},
                    "notes": {"type": "string", "description": "Optional notes or location."},
                    "event_id": {"type": "integer", "description": "Event ID for delete."},
                },
                "required": ["action"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draft_email",
            "description": "Draft a formatted email with a specified tone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Recipient name or role."},
                    "subject": {"type": "string", "description": "Email subject."},
                    "key_points": {"type": "string", "description": "Key bullets or messages to include."},
                    "tone": {"type": "string", "enum": ["professional", "friendly", "concise", "assertive"]},
                },
                "required": ["recipient", "subject", "key_points"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_briefing",
            "description": "Get a morning briefing: pending tasks, agenda events, and PC health summary.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_gmail_messages",
            "description": "List recent emails from Gmail inbox (sender, subject, date, message ID).",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder": {"type": "string", "description": "Folder to check (default 'INBOX')."},
                    "unread_only": {"type": "boolean", "description": "Only return unread emails (default true)."},
                    "limit": {"type": "integer", "description": "Max number of emails to retrieve (default 5)."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_gmail_message",
            "description": "Read the full subject, sender, date, and body of a specific Gmail email by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "The email ID from list_gmail_messages."},
                },
                "required": ["message_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_gmail_draft",
            "description": "Create a draft email or draft reply directly in Gmail Drafts (Brouillons) folder, so the user can review and click Send.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Recipient email address."},
                    "subject": {"type": "string", "description": "Email subject line."},
                    "body": {"type": "string", "description": "Email body content/response text."},
                    "in_reply_to_msg_id": {"type": "string", "description": "Optional Message-ID header if this is a reply to an existing email."},
                },
                "required": ["recipient", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_gmail_message",
            "description": "Send an email immediately via Gmail SMTP (only when user explicitly requests immediate sending).",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string", "description": "Recipient email address."},
                    "subject": {"type": "string", "description": "Email subject line."},
                    "body": {"type": "string", "description": "Email body content."},
                },
                "required": ["recipient", "subject", "body"],
            },
        },
    },
]


def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, str]:
    """Run a registered tool by name with validation."""
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return {"status": "error", "message": f"Unknown tool: {name}"}

    # Filter out empty keys that some LLMs emit for zero-arg functions
    clean_args = {k: v for k, v in arguments.items() if k and str(k).strip()}

    try:
        return handler(**clean_args)
    except TypeError as exc:
        return {"status": "error", "message": f"Invalid arguments for {name}: {exc}"}


# ---------------------------------------------------------------------------
# Dynamic Tool Selection (reduces token footprint to fit within 8K TPM limits)
# ---------------------------------------------------------------------------

TOOL_MAP: dict[str, dict[str, Any]] = {
    t["function"]["name"]: t for t in TOOL_DEFINITIONS
}

TOOL_CATEGORIES: dict[str, list[str]] = {
    "research": [
        "deep_web_research",
        "academic_search",
        "compare_products_or_options",
        "read_document",
        "summarize_document",
    ],
    "documents": [
        "read_document",
        "summarize_document",
        "search_documents_in_folder",
        "create_file",
        "open_path",
        "list_directory",
    ],
    "data": [
        "analyze_tabular_data",
        "generate_chart",
        "read_document",
    ],
    "system": [
        "system_resource_inspector",
        "clean_temp_files",
        "scaffold_code_project",
    ],
    "agenda": [
        "manage_todo",
        "manage_calendar",
        "draft_email",
        "get_daily_briefing",
    ],
    "gmail": [
        "list_gmail_messages",
        "read_gmail_message",
        "create_gmail_draft",
        "send_gmail_message",
        "draft_email",
    ],
    "files": [
        "search_local_files",
        "create_folder",
        "create_file",
        "open_folder",
        "open_path",
        "open_in_vscode",
        "rename_path",
        "list_directory",
        "delete_path",
    ],
    "apps": [
        "open_application",
        "close_application",
        "open_website",
        "open_website_in_chrome",
    ],
    "browser": [
        "open_browser",
        "navigate",
        "search_google",
        "search_youtube",
        "click_element",
        "type_into_field",
        "get_page_content",
        "close_browser",
    ],
    "automation": [
        "take_screenshot",
        "type_text",
        "press_hotkey",
        "move_mouse",
        "click",
        "get_screen_size",
    ],
    "memory": [
        "save_preference",
        "get_preference",
        "list_preferences",
        "save_project",
        "get_project",
        "list_projects",
        "list_workflows",
        "run_workflow",
    ],
}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "research": [
        "research", "paper", "article", "arxiv", "scholar", "quantum",
        "web", "compare", "recherch", "synth", "internet", "en ligne"
    ],
    "documents": [
        "document", "pdf", "docx", "doc", "summar", "read", "folder", "résumé", "resume", "lire"
    ],
    "data": [
        "data", "csv", "excel", "chart", "graph", "plot", "statistic", "donnée", "donnee", "tableau"
    ],
    "system": [
        "system", "cpu", "ram", "disk", "memory", "temp", "clean", "scaffold", "process", "nettoy"
    ],
    "agenda": [
        "todo", "task", "calendar", "event", "meeting", "briefing", "tâche", "tache", "agenda", "rendez-vous"
    ],
    "gmail": [
        "gmail", "mail", "email", "inbox", "draft", "message", "courrier", "brouillon", "envoyer"
    ],
    "files": [
        "file", "folder", "directory", "path", "find", "search", "create", "delete", "rename", "vscode", "dossier", "fichier", "cherch", "trouv", "local"
    ],
    "apps": [
        "open", "close", "launch", "app", "chrome", "calc", "terminal", "ouvr", "ferm", "lanc", "youtube", "spotify", "netflix", "chatgpt"
    ],
    "browser": [
        "browser", "youtube", "navigate", "click", "type", "webpage", "navigateur"
    ],
    "automation": [
        "mouse", "click", "screenshot", "screeshot", "snapshot", "printscreen", "capture", "ecran", "écran", "photo", "hotkey", "keyboard", "screen", "souris", "clavier"
    ],
    "memory": [
        "preference", "project", "workflow", "save", "remember", "projet", "sauvegard"
    ],
}

CORE_TOOLS = [
    "open_application",
    "open_website",
    "search_local_files",
    "take_screenshot",
    "deep_web_research",
    "get_daily_briefing",
    "manage_todo",
    "open_path",
    "list_directory",
    "get_preference",
]


def get_tools_for_request(query: str = "", messages: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Select a focused subset of tools matching user intent and recent context.

    Keeps the total schema size small (< 1,500 tokens) so requests fit comfortably
    within strict provider rate limits (such as Groq's 8000 TPM limit).
    """
    text = (query or "").lower()
    if messages:
        for m in messages[-2:]:
            c = m.get("content")
            if isinstance(c, str):
                text += " " + c.lower()
            for tc in m.get("tool_calls", []):
                fn = tc.get("function", {}).get("name")
                if fn and fn in TOOL_MAP:
                    text += " " + fn

    selected: set[str] = set(CORE_TOOLS)

    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            for t_name in TOOL_CATEGORIES[cat]:
                selected.add(t_name)

    # Always ensure any tool that was actively called in messages is present
    if messages:
        for m in messages:
            for tc in m.get("tool_calls", []):
                fn = tc.get("function", {}).get("name")
                if fn:
                    selected.add(fn)

    return [TOOL_MAP[name] for name in selected if name in TOOL_MAP]

