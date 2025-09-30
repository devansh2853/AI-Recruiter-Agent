# AI Recruiter Agent

AI Recruiter Agent gathers information from a candidate’s resume, generates technical or behavioral interview questions based on the candidate’s profile, creates a report in Google Docs, and emails the report to the recipient.

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd AI-Recruiter-Agent
```

### 2. Environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Fill in your Composio and Gemini API Keys. Leave the Auth Config IDs for now.

### 3. Install UV (if not installed)

Follow the instructions from [UV installation guide](https://docs.astral.sh/uv/getting-started/installation/) or using curl.

### 4. Set up Python environment with `uv`

```bash
uv sync  # Install dependencies
```

### 5. Create Auth Configs

Run the auth config script to create Gmail and Google Docs auth configs:

```bash
uv run python core/auth_config.py
```

Copy the printed auth config IDs into your `.env` file.

### 6. Connect your accounts

Run the main CLI:

```bash
uv run python main.py
```

Then type:

```text
connect
```

Follow the prompts to connect your Gmail and Google Docs accounts. Make sure to allow all required permissions on the OAuth pages.

### 7. Prepare resume

Add the resume(s) you want to process into the `uploads/` folder.

### 8. Process resume and send report

In the CLI, run:

```text
resume <filename>.pdf
```

- The Google Docs report will be created automatically.
- You will be prompted to enter the email ID where the report should be sent.
- The report will then be emailed.
