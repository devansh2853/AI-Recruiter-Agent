import sys
import os
import pyfiglet
from core.agent import RecruiterAgent
from core.connections import authenticate_gmail, authenticate_docs, saveuser, getuser


os.makedirs("uploads", exist_ok=True)
RESUME_FOLDER = "uploads"

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

            elif command in ["exit", "quit"]:
                print("Goodbye!")
                break

            elif command == "help":
                print("Available commands:")
                print("  connect         Create Gmail and notion/google doc connections")
                print("  resume <path>   Process a resume PDF")
                print("  exit / quit     Exit the program")
                continue

            elif command == 'connect':
                user = getuser()
                if not user:
                    userId = input("Enter username (no spaces)").strip()
                    while not userId:
                        userId = input("Please enter valid username").strip()
                    print("Connecting to Gmail..... \n")
                    authenticate_gmail(userId)
                    saveuser(userId, True, False)
                    print("Connecting to Google Documents..... \n")
                    authenticate_docs(userId)
                    saveuser(userId, True, True)
                else:
                    if user['gmail'] and user['docs']:
                        rewrite = input("Connections found. Would you like to overwrite them? (y/n)").strip()
                        if (rewrite.lower() == 'y'):
                            userId = user['userId']
                            print("Connecting to Gmail..... \n")
                            authenticate_gmail(userId)
                            saveuser(userId, True, False)
                            print("Connecting to Google Documents..... \n")
                            authenticate_docs(userId)
                            saveuser(userId, True, True)

                    elif not user['gmail']:
                        print("Connecting to Gmail..... \n")
                        authenticate_gmail(userId)
                        print("Docs already connected")
                        saveuser(user['userId'], True, True)
                    elif not user['docs']:
                        print("Gmail already connected")
                        print("Connecting to Google Documents..... \n")
                        authenticate_docs(userId)
                        saveuser(user['userId'], True, True)


            elif command.startswith("resume "):
                user = getuser()
                if not user:
                    print("Connections to Gmail and Docs are pending")
                elif not user['gmail']:
                    print("Gmail Connection is pending")
                elif not user['docs']:
                    print("Google Docs connection is pending")
                else:
                    userId = user['userId']
                    _, filename = command.split(" ", 1)
                    path = os.path.join(RESUME_FOLDER, filename)
                    if not os.path.exists(path):
                        print(f"❌ Resume file not found: {path}")
                        return
                    result = agent.handleResume(path, userId)
                    if result["successful"]:
                        print(f"✅ Resume processed for {result['candidate']}")
                    else:
                        print(f"❌ Error: {result['error']}")
                    continue

            else:   
                print("Unknown command.")
            
            print("Type 'help' for options.")
            

        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    show_banner()
    repl()
