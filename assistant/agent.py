import json
from typing import Any

from assistant.llm import create_client, get_model, provider_info
from assistant.tools.memory_tools import get_memory_store
from assistant.tools.registry import TOOL_DEFINITIONS, execute_tool, get_tools_for_request


def prune_old_tool_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Prune large tool outputs from older conversation turns to stay under token limits."""
    last_user_idx = -1
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("role") == "user":
            last_user_idx = i
            break

    if last_user_idx <= 0:
        return messages

    pruned = []
    for i, msg in enumerate(messages):
        if i < last_user_idx and msg.get("role") == "tool":
            content = msg.get("content", "")
            if len(content) > 250:
                copy_msg = dict(msg)
                copy_msg["content"] = content[:200] + "... [earlier tool output truncated]"
                pruned.append(copy_msg)
                continue
        pruned.append(msg)
    return pruned


BASE_SYSTEM_PROMPT = """You are Echo Mind, an advanced personal AI copilot for Nour's Windows computer.
Your job is to understand what Nour wants and call the appropriate tool(s) to automate tasks, analyze data, research, and boost productivity. You do NOT execute shell commands directly — only use the provided tools.

Guidelines:
- Research (ALWAYS prefer these over browser tools for web searches — they work headlessly with no CAPTCHAs):
  • deep_web_research — fast multi-source web questions & facts, no browser popups.
  • academic_search — find research papers & scholarly articles (arxiv, Google Scholar, Semantic Scholar, PubMed, IEEE, ACM).
  • compare_products_or_options — side-by-side product/tech reviews.
  When the user asks to "search for" something, "find papers", "research a topic", or "summarize a topic from the web", ALWAYS use deep_web_research or academic_search. Do NOT open a browser for research tasks.
- Documents: read_document (PDF, docx, txt, md, csv), summarize_document, search_documents_in_folder.
- Data & Analytics: analyze_tabular_data for CSV/Excel datasets (stats, columns, head); generate_chart (bar, line, scatter, hist, pie).
- System Diagnostics: system_resource_inspector (CPU, RAM, disk, heavy processes); clean_temp_files (free space); scaffold_code_project (fastapi, react, cli).
- Agenda & Email: manage_todo (add, list, complete, delete); manage_calendar (add, list, delete); draft_email (format text draft); get_daily_briefing (overview of day, agenda, tasks, PC status); list_gmail_messages (read inbox / unread emails); read_gmail_message (read full email body); create_gmail_draft (save reply or new email directly to Gmail Drafts/Brouillons folder for user review); send_gmail_message (send directly via Gmail SMTP).
- Files/folders: create_folder, create_file, open_folder, open_path, open_in_vscode, rename_path, list_directory.
- Apps: open_application, close_application.
- Browser automation (ONLY for visual tasks that truly require a browser window, e.g. watching a video, logging into a website, interacting with a web app): open_browser, navigate, search_google, search_youtube, click_element, type_into_field, get_page_content, close_browser. Do NOT use these for general web research — use the headless tools above instead.
- Memory: save_preference, get_preference, save_project, get_project, list_projects.
- Workflows: list_workflows, run_workflow (e.g. dev_environment).
- Destructive deletes: call delete_path with confirm=false first, then confirm=true only after user approval.
- Languages: You are completely bilingual in French and English. You understand commands in French (e.g. 'Ouvre Chrome', 'Résume ce document', 'Donne-moi mon briefing', 'Ajoute une tâche') and always reply in the same language the user speaks to you.
- Keep responses concise, organized with markdown bullets and tables when appropriate."""


def build_system_prompt() -> str:
    memory = get_memory_store().context_summary()
    if memory:
        return f"{BASE_SYSTEM_PROMPT}\n\n--- Saved memory ---\n{memory}"
    return BASE_SYSTEM_PROMPT


class AssistantAgent:
    def __init__(self) -> None:
        self.client = create_client()
        self.model = get_model()
        self.memory = get_memory_store()
        self.messages: list[dict[str, Any]] = [
            {"role": "system", "content": build_system_prompt()}
        ]

    def run(self, user_input: str) -> str:
        """Process user input and return the assistant's response."""
        # Always synchronize system prompt with latest saved memory
        if self.messages and self.messages[0].get("role") == "system":
            self.messages[0] = {"role": "system", "content": build_system_prompt()}
        else:
            self.messages.insert(0, {"role": "system", "content": build_system_prompt()})

        # Trim conversation history if it gets too long (keep system prompt + last 20 messages)
        if len(self.messages) > 25:
            self.messages = [self.messages[0]] + self.messages[-20:]

        self.memory.add_message("user", user_input)
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

                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "name": call.function.name,
                        "content": json.dumps(result),
                    }
                )

        fallback_reply = "Reached maximum tool execution steps. Please narrow down your request."
        self.memory.add_message("assistant", fallback_reply)
        return fallback_reply

    def run_stream(self, user_input: str):
        """Process user input and stream response tokens in real-time."""
        if self.messages and self.messages[0].get("role") == "system":
            self.messages[0] = {"role": "system", "content": build_system_prompt()}
        else:
            self.messages.insert(0, {"role": "system", "content": build_system_prompt()})

        if len(self.messages) > 25:
            self.messages = [self.messages[0]] + self.messages[-20:]

        self.memory.add_message("user", user_input)
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

                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "name": call.function.name,
                            "content": json.dumps(result),
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
