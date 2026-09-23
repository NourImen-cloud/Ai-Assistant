"""Personal AI Assistant — CLI entry point."""

import argparse
import sys

from assistant.agent import AssistantAgent
from assistant.voice.stt import listen
from assistant.voice.tts import speak


def run_cli(voice_mode: bool = False) -> None:
    try:
        agent = AssistantAgent()
    except ValueError as exc:
        print(f"Setup error: {exc}")
        sys.exit(1)

    print("=" * 50)
    print("  Personal AI Assistant")
    print(f"  LLM: {agent.provider_label()}")
    print("=" * 50)
    print()
    print("Examples:")
    print("  Open Chrome")
    print("  Search Google for Python decorators")
    print("  Create a folder called AI Projects on my desktop")
    print("  Save my main project as AI Scheduler at C:\\Users\\...\\AI-Scheduler")
    print("  Run the dev_environment workflow")
    print()
    print("Commands: quit, reset" + (", say 'listen' for voice input" if not voice_mode else ""))
    print("-" * 50)
    print()

    while True:
        try:
            if voice_mode:
                print("Listening... (speak now)")
                heard = listen()
                if heard.get("status") != "success":
                    print(f"Voice error: {heard.get('message')}\n")
                    continue
                user_input = heard.get("text", heard["message"])
                print(f"You (voice): {user_input}")
            else:
                user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        lower = user_input.lower()
        if lower in {"quit", "exit", "q"}:
            print("Goodbye!")
            break

        if lower == "reset":
            agent.reset()
            print("Conversation cleared.\n")
            continue

        if lower == "listen" and not voice_mode:
            heard = listen()
            if heard.get("status") != "success":
                print(f"Voice error: {heard.get('message')}\n")
                continue
            user_input = heard.get("text", heard["message"])
            print(f"You (voice): {user_input}")

        try:
            response = agent.run(user_input)
            print(f"\nAssistant: {response}\n")
            if voice_mode:
                speak(response)
        except Exception as exc:
            print(f"\nError: {exc}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Personal AI Assistant")
    parser.add_argument("--voice", action="store_true", help="Continuous voice input mode")
    args = parser.parse_args()
    run_cli(voice_mode=args.voice)


if __name__ == "__main__":
    main()
