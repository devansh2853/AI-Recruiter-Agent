# AI Recruiter Agent

AI Recruiter Agent is a terminal-based tool that processes a candidate's resume, generates relevant technical or behavioral interview questions, creates a structured Google Docs report, and emails it to a specified recipient.

---

## Features

- Extracts key information from resumes (skills, experience, education, certifications, languages).
- Generates technical or behavioral interview questions tailored to the candidate.
- Creates a professional Google Docs report with proper headings.
- Sends the report via email to the specified recipient.

---

## Project Structure

```
AI-Recruiter-Agent/
├── core/
│   ├── agent.py          # Main agent logic & orchestration
│   ├── constants.py      # Initialize and expose OpenAI + Composio clients
│   ├── connections.py    # Create and manage external connections
│   ├── auth_config.py    # Create, manage, and validate auth configuration
│   └── tools.py          # Return tools to plug into the agent
├── main.py               # Terminal CLI entry point
├── README.md
├── .env.example          # Example environment variables
├── pyproject.toml
├── uv.lock               # Locked package versions for uv
├── Makefile
└── uploads/              # Place resumes here for processing
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository_url>
cd AI-Recruiter-Agent
```

### 2. Create a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
```

### 3. Install `uv` (if not already installed)

Follow [uv installation instructions](https://uvproject.org/) or via `curl`.

### 4. Install dependencies using uv

```bash
uv add -r requirements.txt
uv sync
```

### 5. Configure authentication

Run the `auth_config.py` script to create Composio auth configurations:

```bash
python core/auth_config.py
```

- Copy the printed **Auth Config IDs** into your `.env` file (refer to `.env.example`).

### 6. Connect external accounts

Start the CLI:

```bash
python main.py
```

- Use the command `connect` to link Gmail and Google Docs accounts.
- Follow the OAuth prompts and grant the required permissions.

### 7. Add resumes

Place any resumes to be processed in the `uploads/` folder.

### 8. Process a resume

Run the command:

```text
resume <filename>.pdf
```

- Generates a Google Docs report.
- Prompts for the recipient email.
- Sends the report via email.

---

## Commands

| Command         | Description                              |
| --------------- | ---------------------------------------- |
| `connect`       | Connect Gmail and Google Docs accounts   |
| `resume <file>` | Process a resume PDF and generate report |
| `help`          | Show available commands                  |
| `exit` / `quit` | Exit the CLI                             |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```text
OPENAI_API_KEY=<your_openai_api_key>
COMPOSIO_API_KEY=<your_composio_api_key>
AUTHCFG_GMAIL=<gmail_auth_config_id>
AUTHCFG_GDOCS=<google_docs_auth_config_id>
```

---

## Notes

- `.python-version` ensures the correct Python version is used.
- `uploads/` must exist, even if empty.
- CLI shows the ASCII banner on startup.

---

## License

[MIT License](LICENSE)
