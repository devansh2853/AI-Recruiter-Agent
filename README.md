# AI Recruiter Agent

An AI-powered recruiter assistant that processes candidate resumes, generates technical or behavioral interview questions, creates a structured report in Google Docs, and emails the report to the desired recipient.

## Project Structure

```
AI-Recruiter-Agent/
  core/
    agent.py         # Main agent logic & orchestration
    constants.py     # Initialize and expose OpenAI + Composio clients
    connection.py    # Create and manage external connections
    auth_config.py   # Create, manage, and validate auth configurations
    tools.py         # Return the list of tools to plug into the agent
  uploads/           # Add resumes to be processed here
  main.py            # Entry point: interactive terminal CLI
  README.md
  .env.example
  pyproject.toml     # Dependency management for uv
  uv.lock            # Dependency lock file
  Makefile
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repo_url>
cd AI-Recruiter-Agent
```

### 2. Install UV (if not installed)

Follow the instructions from [UV installation guide](https://uv.dev) or using curl.

### 3. Install dependencies and create virtual environment

UV will handle creating a virtual environment and installing all dependencies from `pyproject.toml`.

```bash
uv sync
```

### 4. Configure Auth

Run the auth configuration script to generate Composio auth config IDs:

```bash
python core/auth_config.py
```

Copy the printed `GMAIL_AUTH_CONFIG_ID` and `DOCS_AUTH_CONFIG_ID` values into your `.env` file.

### 5. Connect Gmail and Google Docs

Run the interactive CLI:

```bash
uv run python main.py
```

- Use the command `connect` to authenticate your Gmail and Google Docs accounts.
- Follow the OAuth prompts in your browser.

### 6. Add resumes

Place the resumes you want to process in the `uploads/` folder.

### 7. Process a resume

In the CLI, run:

```bash
resume <filename>.pdf
```

- Example: `resume resume1.pdf`
- The agent will process the resume, generate questions, create a Google Doc report, and prompt for the recipient email.

### 8. Email the report

Provide the recipient's email in the CLI prompt. The report will be sent automatically from the connected Gmail account.

## Notes

- Ensure the `.env` file is properly configured with the auth IDs and API keys.
- The `uploads/` folder must contain the resumes to process.
- UV manages the virtual environment and dependencies automatically, so there is no need to manually create a venv or install packages.

## License

MIT License
