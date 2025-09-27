import sys
import pyfiglet
from core.agent import RecruiterAgent


def show_banner():
    banner = pyfiglet.figlet_format("AI Recruiter Agent")
    print(banner)


def repl():
    agent = RecruiterAgent()
    print("Type 'help' for commands, 'exit' to quit.\n")

    while True:
        try:
            command = input(">> ").strip()

            if not command:
                continue

            if command in ["exit", "quit"]:
                print("Goodbye!")
                break

            if command == "help":
                print("Available commands:")
                print("  resume <path>   Process a resume PDF")
                print("  exit / quit     Exit the program")
                continue

            if command.startswith("resume "):
                _, path = command.split(" ", 1)
                result = agent.handle_resume(path)
                if result["successful"]:
                    print(f"✅ Resume processed for {result['candidate']}")
                else:
                    print(f"❌ Error: {result['error']}")
                continue

            print("Unknown command. Type 'help' for options.")

        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    show_banner()
    repl()
