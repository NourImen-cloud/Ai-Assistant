import json
from typing import Any

from assistant.llm import create_client, get_model, provider_info
from assistant.tools.memory_tools import get_memory_store
from assistant.tools.registry import TOOL_DEFINITIONS, execute_tool, get_tools_for_request


def prune_old_tool_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Prune large tool outputs from conversation to strictly stay under token limits."""
    last_user_idx = -1
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("role") == "user":
            last_user_idx = i
            break

    pruned = []
    for i, msg in enumerate(messages):
        if msg.get("role") == "tool":
            content = str(msg.get("content", ""))
            limit = 250 if i < last_user_idx else 2000
            if len(content) > limit:
                copy_msg = dict(msg)
                copy_msg["content"] = content[:limit] + "... [truncated for token limit]"
                pruned.append(copy_msg)
                continue
        pruned.append(msg)
    return pruned


def get_user_name() -> str:
    try:
        name = get_memory_store().get_preference("user_name")
        if name:
            return name
        import getpass
        return getpass.getuser().capitalize()
    except Exception:
        return "User"


BASE_SYSTEM_PROMPT_TEMPLATE = """You are Echo Mind, an advanced personal AI copilot for {user_name}'s Windows computer.
Your job is to understand what {user_name} wants and call the appropriate tool(s) to automate tasks, analyze data, research, and boost productivity. You do NOT execute shell commands directly — only use the provided tools.

Guidelines:
- Local Files & System Search:
  • search_local_files — search for files/folders across Desktop, Documents, Downloads, or custom paths by name, extension, or pattern. ALWAYS use search_local_files when the user wants to find or search for files, documents, or data on their PC!
  • list_directory, open_folder, open_path, open_in_vscode, create_folder, create_file, rename_path.
- Apps & Web Services:
  • open_application — launch desktop apps (Chrome, VS Code, Calculator, Terminal, Notepad) OR popular web services (YouTube, Spotify, Netflix, ChatGPT, GitHub, Gmail, Maps). For example, "open Chrome and YouTube" or "lance YouTube" should call open_application(name="youtube").
  • open_website, open_website_in_chrome, close_application.
- Screenshots & Automation:
  • take_screenshot — capture the screen and save to the screenshots folder. Use this whenever the user asks for a screenshot ("take a screenshot", "capture d'écran", "screen").
  • type_text, press_hotkey, click, move_mouse, get_screen_size.
- Data & Analytics:
  • analyze_tabular_data — inspect CSV or Excel datasets (dimensions, columns, statistics, data preview). Works with files in uploads/ or on Desktop/Documents.
  • generate_chart — plot and save charts (bar, line, scatter, hist, pie) from CSV/Excel files.
- Documents: read_document (PDF, docx, txt, md, csv), summarize_document, search_documents_in_folder.
- Online Web Research (ONLY for general internet knowledge, web facts, and online articles):
  • deep_web_research — fast multi-source web search & facts. Use ONLY for internet questions, not for finding local files.
  • academic_search — find scientific papers (arxiv, Google Scholar, PubMed).
  • compare_products_or_options — side-by-side product reviews.
- System Diagnostics: system_resource_inspector (CPU, RAM, disk, processes); clean_temp_files (free space); scaffold_code_project.
- Agenda & Email: manage_todo (add, list, complete, delete); manage_calendar (add, list, delete); draft_email; get_daily_briefing; list_gmail_messages; read_gmail_message; create_gmail_draft; send_gmail_message.
- Destructive deletes: call delete_path with confirm=false first, then confirm=true only after user approval.
- Languages: You are completely bilingual in French and English. You understand commands in French (e.g. 'Ouvre Chrome', 'Lance YouTube', 'Prends une capture d'écran', 'Cherche mes fichiers', 'Analyse ce tableau') and always reply in the same language the user speaks to you.
- Keep responses concise, organized with markdown bullets and tables when appropriate."""


def build_system_prompt() -> str:
    user_name = get_user_name()
    base_prompt = BASE_SYSTEM_PROMPT_TEMPLATE.format(user_name=user_name)
    memory = get_memory_store().context_summary()
    if memory:
        return f"{base_prompt}\n\n--- Saved memory ---\n{memory}"
    return base_prompt


class AssistantAgent:
    def __init__(self) -> None:
        self.client = create_client()
        self.model = get_model()
        self.memory = get_memory_store()
        self.messages: list[dict[str, Any]] = [
            {"role": "system", "content": build_system_prompt()}
        ]

    def run(self, user_input: str, display_input: str | None = None) -> str:
        """Process user input and return the assistant's response."""
        # Always synchronize system prompt with latest saved memory
        if self.messages and self.messages[0].get("role") == "system":
            self.messages[0] = {"role": "system", "content": build_system_prompt()}
        else:
            self.messages.insert(0, {"role": "system", "content": build_system_prompt()})

        # Trim conversation history if it gets too long (keep system prompt + last 20 messages)
        if len(self.messages) > 25:
            self.messages = [self.messages[0]] + self.messages[-20:]

        self.memory.add_message("user", display_input or user_input)
        self.messages.append({"role": "user", "content": user_input})

        # Ensure all tool messages in history have a name (required by Harmony / vLLM / Groq)
        for msg in self.messages:
            if msg.get("role") == "tool" and not msg.get("name"):
                msg["name"] = "tool"

        # Select focused tools for this intent to stay well under provider rate limits
        active_tools = get_tools_for_request(user_input, self.messages)

        max_rounds = 8
        current_round = 0

        while current_round < max_rounds:
            current_round += 1
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=prune_old_tool_messages(self.messages),
                    tools=active_tools,
                    tool_choice="auto",
                    max_tokens=2048,
                )
            except Exception as exc:
                err_msg = f"LLM error: {exc}"
                self.memory.add_message("assistant", err_msg)
                while len(self.messages) > 1 and self.messages[-1].get("role") in ("tool", "assistant"):
                    self.messages.pop()
                return err_msg

            message = response.choices[0].message
            assistant_message: dict[str, Any] = {
                "role": "assistant",
                "content": message.content,
            }

            if message.tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in message.tool_calls
                ]

            self.messages.append(assistant_message)

            if not message.tool_calls:
                reply = message.content or "Done."
                self.memory.add_message("assistant", reply)
                return reply

            for call in message.tool_calls:
                try:
                    args = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError as err:
                    result = {"status": "error", "message": f"Malformed tool arguments JSON: {err}"}
                else:
                    result = execute_tool(call.function.name, args)

                raw_tool_content = json.dumps(result)
                if len(raw_tool_content) > 2000:
                    raw_tool_content = raw_tool_content[:2000] + "... [truncated to fit token limit]"

                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "name": call.function.name,
                        "content": raw_tool_content,
                    }
                )

        fallback_reply = "Reached maximum tool execution steps. Please narrow down your request."
        self.memory.add_message("assistant", fallback_reply)
        return fallback_reply

    def run_stream(self, user_input: str, display_input: str | None = None):
        """Process user input and stream response tokens in real-time."""
        if self.messages and self.messages[0].get("role") == "system":
            self.messages[0] = {"role": "system", "content": build_system_prompt()}
        else:
            self.messages.insert(0, {"role": "system", "content": build_system_prompt()})

        if len(self.messages) > 25:
            self.messages = [self.messages[0]] + self.messages[-20:]

        self.memory.add_message("user", display_input or user_input)
        self.messages.append({"role": "user", "content": user_input})

        # Ensure all tool messages in history have a name (required by Harmony / vLLM / Groq)
        for msg in self.messages:
            if msg.get("role") == "tool" and not msg.get("name"):
                msg["name"] = "tool"

        # Select focused tools for this intent to stay well under provider rate limits
        active_tools = get_tools_for_request(user_input, self.messages)

        max_rounds = 8
        current_round = 0

        while current_round < max_rounds:
            current_round += 1
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=prune_old_tool_messages(self.messages),
                    tools=active_tools,
                    tool_choice="auto",
                    max_tokens=2048,
                )
            except Exception as exc:
                err_msg = f"LLM error: {exc}"
                self.memory.add_message("assistant", err_msg)
                while len(self.messages) > 1 and self.messages[-1].get("role") in ("tool", "assistant"):
                    self.messages.pop()
                yield err_msg
                return

            message = response.choices[0].message
            assistant_message: dict[str, Any] = {
                "role": "assistant",
                "content": message.content,
            }

            if message.tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in message.tool_calls
                ]
                self.messages.append(assistant_message)

                for call in message.tool_calls:
                    yield f"⚡ Running {call.function.name.replace('_', ' ')}...\n"
                    try:
                        args = json.loads(call.function.arguments or "{}")
                    except json.JSONDecodeError as err:
                        result = {"status": "error", "message": f"Malformed tool arguments JSON: {err}"}
                    else:
                        result = execute_tool(call.function.name, args)

                    raw_tool_content = json.dumps(result)
                    if len(raw_tool_content) > 2000:
                        raw_tool_content = raw_tool_content[:2000] + "... [truncated to fit token limit]"

                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "name": call.function.name,
                            "content": raw_tool_content,
                        }
                    )
                continue

            full_reply = message.content or "Done."
            self.messages.append(assistant_message)
            self.memory.add_message("assistant", full_reply)
            yield full_reply
            return

        fallback_reply = "Reached maximum tool execution steps. Please narrow down your request."
        self.memory.add_message("assistant", fallback_reply)
        yield fallback_reply

    def reset(self) -> None:
        """Clear conversation history, keeping the system prompt."""
        self.messages = [{"role": "system", "content": build_system_prompt()}]

    @staticmethod
    def provider_label() -> str:
        return provider_info()
