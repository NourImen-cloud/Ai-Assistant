import ast
import json
import re
import time
from typing import Any

from assistant.llm import create_client, get_model, provider_info
from assistant.tools.memory_tools import get_memory_store
from assistant.tools.registry import TOOL_DEFINITIONS, execute_tool, get_tools_for_request


def parse_text_tool_calls(text: str) -> list[dict[str, Any]]:
    """Extract tool calls embedded as text (e.g. Qwen / XML or JSON style)."""
    calls: list[dict[str, Any]] = []
    if not text:
        return calls

    # 1. XML style: <function=name> ... <parameter=key>value</parameter> ... </function>
    fn_xml_matches = list(re.finditer(r'<function=([a-zA-Z0-9_-]+)>\s*(.*?)\s*</function>', text, re.DOTALL))
    for match in fn_xml_matches:
        fn_name = match.group(1).strip()
        body = match.group(2).strip()
        args: dict[str, Any] = {}
        param_matches = re.finditer(r'<parameter=([a-zA-Z0-9_-]+)>\s*(.*?)\s*</parameter>', body, re.DOTALL)
        found_param = False
        for pm in param_matches:
            found_param = True
            k = pm.group(1).strip()
            v = pm.group(2).strip()
            try:
                args[k] = json.loads(v)
            except Exception:
                args[k] = v
        if not found_param and body:
            try:
                parsed = json.loads(body)
                if isinstance(parsed, dict):
                    args = parsed
            except Exception:
                pass
        calls.append({"name": fn_name, "arguments": args})

    if calls:
        return calls

    # 2. Blocks inside <tool_call> ... </tool_call>
    tool_call_blocks = list(re.finditer(r'<tool_call>\s*(.*?)\s*</tool_call>', text, re.DOTALL))
    for block in tool_call_blocks:
        content = block.group(1).strip()
        # 2a: JSON inside <tool_call>
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                name = parsed.get("name") or parsed.get("function")
                args = parsed.get("arguments") or parsed.get("parameters") or {}
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        pass
                if name:
                    calls.append({"name": name, "arguments": args if isinstance(args, dict) else {}})
                    continue
        except Exception:
            pass

        # 2b: function_name(arg="val")
        call_match = re.match(r'([a-zA-Z0-9_]+)\((.*)\)$', content, re.DOTALL)
        if call_match:
            fn_name = call_match.group(1)
            raw_args = call_match.group(2).strip()
            args = {}
            if raw_args.startswith("{") and raw_args.endswith("}"):
                try:
                    args = json.loads(raw_args)
                except Exception:
                    try:
                        args = ast.literal_eval(raw_args)
                    except Exception:
                        pass
            elif raw_args:
                try:
                    args = eval(f"dict({raw_args})", {"__builtins__": {}})
                except Exception:
                    args = {"query": raw_args.strip("\"'")}
            calls.append({"name": fn_name, "arguments": args})

    return calls


def clean_model_output(text: str) -> str:
    """Strip out raw tool call tags, internal thinking tags, and XML markup."""
    if not text:
        return ""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'<think>.*', '', text, flags=re.DOTALL)
    text = re.sub(r'<tool_call>.*?</tool_call>', '', text, flags=re.DOTALL)
    text = re.sub(r'<tool_call>.*', '', text, flags=re.DOTALL)
    text = re.sub(r'<function=[^>]+>.*?</function>', '', text, flags=re.DOTALL)
    text = re.sub(r'<parameter=[^>]+>.*?</parameter>', '', text, flags=re.DOTALL)
    text = re.sub(r'</?(?:tool_call|function|parameter)[^>]*>', '', text)
    text = re.sub(r'⚡\s*Running\s+[^\n]+', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


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


def sanitize_message_history(messages: list[dict[str, Any]], max_history: int = 16) -> list[dict[str, Any]]:
    """Trim conversation history while strictly preserving system prompt and valid tool_call pairs."""
    if len(messages) <= max_history:
        return messages

    system_msg = messages[0] if messages and messages[0].get("role") == "system" else None
    rest = messages[1:] if system_msg else messages

    cutoff = max(0, len(rest) - max_history)
    while cutoff < len(rest) and rest[cutoff].get("role") in ("tool", "assistant"):
        cutoff += 1

    trimmed = rest[cutoff:] if cutoff < len(rest) else rest[-4:]
    return ([system_msg] if system_msg else []) + trimmed


def get_user_name() -> str:
    try:
        name = get_memory_store().get_preference("user_name")
        if name:
            return name
        import getpass
        return getpass.getuser().capitalize()
    except Exception:
        return "User"


BASE_SYSTEM_PROMPT_TEMPLATE = """You are Echo Mind, a fast, intelligent personal AI copilot for {user_name}'s Windows PC.
Understand what {user_name} needs and call tools to automate tasks, analyze data, research, and boost productivity. Do NOT execute shell commands directly.

Core Tool Rules:
- PC Files: ALWAYS use search_local_files to find documents/folders. Use list_directory, open_path, open_folder, create_folder, create_file.
- Apps & Web: open_application launches desktop apps (VS Code, Calc, etc.). To open any website, search on YouTube/Google, or play music/videos (e.g. 'search weekend playlist on youtube', 'open youtube in chrome'): ALWAYS use open_website_in_chrome or open_website directly with the URL (e.g. https://www.youtube.com/results?search_query=...). Do NOT call open_application first when opening web services. close_application closes apps.
- Screen & Input: take_screenshot captures PNG screenshots. type_text, press_hotkey, click, move_mouse for desktop GUI actions when no direct tool exists.
- Data & Docs: analyze_tabular_data and generate_chart for CSV/Excel datasets. read_document and summarize_document for PDF/Word/text files.
- Research: deep_web_research for online facts and comparisons. academic_search for papers.
- Agenda & Mail: manage_todo, manage_calendar, get_daily_briefing, list_gmail_messages, create_gmail_draft, send_gmail_message.
- Safety: delete_path requires confirm=false first.
- Multi-step tasks: You can execute multiple tools across rounds to complete multi-step goals. Do not narrate intermediate steps or output XML/tool tags in text. Execute tools silently, then provide a concise, polished response when done.
- Language: Bilingual English/French. Keep responses concise, direct, and formatted in markdown."""


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

        # Trim conversation history cleanly, keeping turns and tool pairs valid
        self.messages = sanitize_message_history(self.messages, max_history=8)

        self.memory.add_message("user", display_input or user_input)
        self.messages.append({"role": "user", "content": user_input})

        # Ensure all tool messages in history have a name (required by Harmony / vLLM / Groq)
        for msg in self.messages:
            if msg.get("role") == "tool" and not msg.get("name"):
                msg["name"] = "tool"

        # Select focused tools for this intent to stay well under provider rate limits
        active_tools = get_tools_for_request(user_input, self.messages)
        is_explicit_multistep = any(
            w in user_input.lower()
            for w in ["and then", "after that", "next", "also", "then", "puis", "ensuite"]
        )

        max_rounds = 4
        current_round = 0
        executed_tool_calls: set[str] = set()

        while current_round < max_rounds:
            current_round += 1
            tools_to_send = active_tools if active_tools else None
            if current_round > 1 and not is_explicit_multistep:
                if any("open_website" in sig for sig in executed_tool_calls) or len(executed_tool_calls) >= 2:
                    tools_to_send = None

            extra_kwargs: dict[str, Any] = {}
            if tools_to_send:
                extra_kwargs["tools"] = tools_to_send
                extra_kwargs["tool_choice"] = "auto"

            response = None
            for attempt in range(3):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=prune_old_tool_messages(self.messages),
                        max_tokens=250,
                        **extra_kwargs,
                    )
                    break
                except Exception as exc:
                    err_str = str(exc)
                    if "429" in err_str and attempt < 2:
                        time.sleep(1.5 * (attempt + 1))
                        continue
                    err_msg = f"LLM error: {exc}"
                    self.memory.add_message("assistant", err_msg)
                    while len(self.messages) > 1 and self.messages[-1].get("role") in ("tool", "assistant"):
                        self.messages.pop()
                    return err_msg

            if response is None:
                err_msg = "LLM error: Rate limit exceeded. Please wait a moment before trying again."
                self.memory.add_message("assistant", err_msg)
                return err_msg

            message = response.choices[0].message
            content = message.content or ""

            # Check for API tool calls OR text-based tool calls
            parsed_tools: list[dict[str, Any]] = []
            if message.tool_calls:
                for call in message.tool_calls:
                    parsed_tools.append({
                        "id": call.id,
                        "name": call.function.name,
                        "arguments_str": call.function.arguments or "{}",
                    })
            else:
                text_calls = parse_text_tool_calls(content)
                if text_calls:
                    for i, tc in enumerate(text_calls):
                        parsed_tools.append({
                            "id": f"text_call_{current_round}_{i}",
                            "name": tc["name"],
                            "arguments_str": json.dumps(tc.get("arguments", {})),
                        })

            # If no tools called, this is the final conversational response
            if not parsed_tools:
                reply = clean_model_output(content) or "Done."
                self.messages.append({"role": "assistant", "content": reply})
                self.memory.add_message("assistant", reply)
                return reply

            # Build assistant message with tool calls
            assistant_message: dict[str, Any] = {
                "role": "assistant",
                "content": clean_model_output(content) or None,
                "tool_calls": [
                    {
                        "id": t["id"],
                        "type": "function",
                        "function": {
                            "name": t["name"],
                            "arguments": t["arguments_str"],
                        },
                    }
                    for t in parsed_tools
                ],
            }
            self.messages.append(assistant_message)

            # Execute tools silently
            for t in parsed_tools:
                fn_name = t["name"]
                args_str = t["arguments_str"]
                call_sig = f"{fn_name}:{args_str}"

                if call_sig in executed_tool_calls:
                    result = {"status": "info", "message": f"{fn_name} was already executed."}
                else:
                    executed_tool_calls.add(call_sig)
                    try:
                        args = json.loads(args_str)
                    except json.JSONDecodeError as err:
                        result = {"status": "error", "message": f"Malformed tool arguments JSON: {err}"}
                    else:
                        result = execute_tool(fn_name, args)

                raw_tool_content = json.dumps(result)
                if len(raw_tool_content) > 2000:
                    raw_tool_content = raw_tool_content[:2000] + "... [truncated to fit token limit]"

                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": t["id"],
                        "name": fn_name,
                        "content": raw_tool_content,
                    }
                )

        fallback_reply = "Done."
        self.memory.add_message("assistant", fallback_reply)
        return fallback_reply

    def run_stream(self, user_input: str, display_input: str | None = None):
        """Process user input and stream response tokens in real-time."""
        if self.messages and self.messages[0].get("role") == "system":
            self.messages[0] = {"role": "system", "content": build_system_prompt()}
        else:
            self.messages.insert(0, {"role": "system", "content": build_system_prompt()})

        # Trim conversation history cleanly, keeping turns and tool pairs valid
        self.messages = sanitize_message_history(self.messages, max_history=8)

        self.memory.add_message("user", display_input or user_input)
        self.messages.append({"role": "user", "content": user_input})

        # Ensure all tool messages in history have a name (required by Harmony / vLLM / Groq)
        for msg in self.messages:
            if msg.get("role") == "tool" and not msg.get("name"):
                msg["name"] = "tool"

        # Select focused tools for this intent to stay well under provider rate limits
        active_tools = get_tools_for_request(user_input, self.messages)
        is_explicit_multistep = any(
            w in user_input.lower()
            for w in ["and then", "after that", "next", "also", "then", "puis", "ensuite"]
        )

        max_rounds = 4
        current_round = 0
        executed_tool_calls: set[str] = set()

        while current_round < max_rounds:
            current_round += 1
            tools_to_send = active_tools if active_tools else None
            if current_round > 1 and not is_explicit_multistep:
                if any("open_website" in sig for sig in executed_tool_calls) or len(executed_tool_calls) >= 2:
                    tools_to_send = None

            extra_kwargs: dict[str, Any] = {}
            if tools_to_send:
                extra_kwargs["tools"] = tools_to_send
                extra_kwargs["tool_choice"] = "auto"

            stream = None
            for attempt in range(3):
                try:
                    stream = self.client.chat.completions.create(
                        model=self.model,
                        messages=prune_old_tool_messages(self.messages),
                        stream=True,
                        max_tokens=250,
                        **extra_kwargs,
                    )
                    break
                except Exception as exc:
                    err_str = str(exc)
                    if "429" in err_str and attempt < 2:
                        time.sleep(1.5 * (attempt + 1))
                        continue
                    err_msg = f"LLM error: {exc}"
                    self.memory.add_message("assistant", err_msg)
                    while len(self.messages) > 1 and self.messages[-1].get("role") in ("tool", "assistant"):
                        self.messages.pop()
                    yield err_msg
                    return

            if stream is None:
                err_msg = "LLM error: Rate limit exceeded. Please wait a moment before trying again."
                self.memory.add_message("assistant", err_msg)
                yield err_msg
                return

            tool_calls_acc: dict[int, dict[str, str]] = {}
            content_chunks: list[str] = []

            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta.content:
                    content_chunks.append(delta.content)
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_acc:
                            tool_calls_acc[idx] = {"id": tc.id or "", "name": "", "arguments": ""}
                        if tc.id:
                            tool_calls_acc[idx]["id"] = tc.id
                        if tc.function:
                            if tc.function.name:
                                tool_calls_acc[idx]["name"] += tc.function.name
                            if tc.function.arguments:
                                tool_calls_acc[idx]["arguments"] += tc.function.arguments

            full_content = "".join(content_chunks)

            # Check for API tool calls OR text-based tool calls
            parsed_tools: list[dict[str, Any]] = []
            if tool_calls_acc:
                for i, tc_data in sorted(tool_calls_acc.items()):
                    parsed_tools.append({
                        "id": tc_data["id"] or f"call_{current_round}_{i}",
                        "name": tc_data["name"],
                        "arguments_str": tc_data["arguments"] or "{}",
                    })
            else:
                text_calls = parse_text_tool_calls(full_content)
                if text_calls:
                    for i, tc in enumerate(text_calls):
                        parsed_tools.append({
                            "id": f"text_call_{current_round}_{i}",
                            "name": tc["name"],
                            "arguments_str": json.dumps(tc.get("arguments", {})),
                        })

            # If tools were invoked: execute silently without yielding intermediate scratchpad
            if parsed_tools:
                assistant_message: dict[str, Any] = {
                    "role": "assistant",
                    "content": clean_model_output(full_content) or None,
                    "tool_calls": [
                        {
                            "id": t["id"],
                            "type": "function",
                            "function": {
                                "name": t["name"],
                                "arguments": t["arguments_str"],
                            },
                        }
                        for t in parsed_tools
                    ],
                }
                self.messages.append(assistant_message)

                for t in parsed_tools:
                    fn_name = t["name"]
                    args_str = t["arguments_str"]
                    call_sig = f"{fn_name}:{args_str}"

                    if call_sig in executed_tool_calls:
                        result = {"status": "info", "message": f"{fn_name} was already executed."}
                    else:
                        executed_tool_calls.add(call_sig)
                        try:
                            args = json.loads(args_str)
                        except json.JSONDecodeError as err:
                            result = {"status": "error", "message": f"Malformed tool arguments JSON: {err}"}
                        else:
                            result = execute_tool(fn_name, args)

                    raw_tool_content = json.dumps(result)
                    if len(raw_tool_content) > 1000:
                        raw_tool_content = raw_tool_content[:1000] + "... [truncated]"

                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": t["id"],
                            "name": fn_name,
                            "content": raw_tool_content,
                        }
                    )
                # Silently continue to next round
                continue

            # No tools invoked: this is the final conversational reply!
            final_reply = clean_model_output(full_content) or "Done."
            self.messages.append({"role": "assistant", "content": final_reply})
            self.memory.add_message("assistant", final_reply)
            yield final_reply
            return

        fallback_reply = "Done."
        self.memory.add_message("assistant", fallback_reply)
        yield fallback_reply

    def reset(self) -> None:
        """Clear conversation history, keeping the system prompt."""
        self.messages = [{"role": "system", "content": build_system_prompt()}]

    @staticmethod
    def provider_label() -> str:
        return provider_info()
