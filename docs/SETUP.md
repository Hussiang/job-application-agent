# Setup Guide

## Prerequisites

The project requires:

- Python 3.14
- Git
- WSL/Linux or another compatible Python environment
- Adzuna API credentials
- Telegram bot credentials

Docker and Docker Compose are optional.

## Clone the Repository

```bash
git clone https://github.com/Hussiang/job-application-agent.git
cd job-application-agent
```

## Create the Virtual Environment

```bash
python3 -m venv .venv
```

## Activate the Virtual Environment

```bash
source .venv/bin/activate
```

Verify:

```bash
which python3
python3 --version
```

The Python executable should point to the project's `.venv`.

## Install Dependencies

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
pip install pytest
```

## Environment Variables

Create a `.env` file in the project root.

Example:

```text
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Never commit `.env`.

## Adzuna Setup

The application uses the Adzuna API for live job discovery.

Required credentials:

```text
ADZUNA_APP_ID
ADZUNA_APP_KEY
```

Store these values in `.env` for local development.

For GitHub Actions, store them as GitHub repository secrets.

## Telegram Setup

Create a Telegram bot using BotFather.

Required values:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

General setup flow:

1. Create a Telegram bot using BotFather.
2. Copy the bot token.
3. Send a message to the bot.
4. Retrieve the chat ID using the Telegram Bot API.
5. Store both values in `.env`.

## Candidate Configuration

Candidate and job-search configuration is stored in:

```text
config/profile.yaml
```

This file controls:

- candidate information
- target roles
- locations
- skills
- experience preferences
- required title keywords
- excluded keywords
- job discovery settings
- Telegram notification settings

## Scoring Configuration

Job scoring rules are stored in:

```text
config/scoring.yaml
```

This allows scoring behavior to be modified without changing the core Python logic.

## Run the Interactive Application

Activate the virtual environment first:

```bash
source .venv/bin/activate
```

Then run:

```bash
python3 main.py
```

The main menu provides:

```text
1. Add and analyze a new job
2. Rank all jobs
3. Manage applications
4. Update application status
5. View application dashboard
6. Search and filter jobs
7. Discover live jobs
8. Exit
```

## Run Automated Discovery

The non-interactive discovery runner is:

```bash
python3 run_discovery.py
```

This is the entry point intended for automated execution through GitHub Actions.

## Run Tests

Run the complete test suite:

```bash
python3 -m pytest tests -v
```

The test suite covers job filtering, duplicate detection, job lifecycle behavior, Telegram notification behavior, notification deduplication, notification thresholds, meaningful changes, and daily digest behavior.

## GitHub Actions

The repository contains two workflows:

```text
.github/workflows/test.yml
.github/workflows/job-discovery.yml
```

### Python Test Workflow

The test workflow:

1. checks out the repository
2. installs Python
3. installs project dependencies
4. runs pytest
5. builds the Docker image
6. validates Docker Compose configuration

It runs on pushes and pull requests targeting `main`.

### Automated Job Discovery Workflow

The discovery workflow:

1. checks out the repository
2. installs Python
3. installs dependencies
4. injects repository secrets
5. runs `run_discovery.py`
6. updates job data
7. commits database changes when necessary

## GitHub Repository Secrets

Configure the following secrets:

```text
ADZUNA_APP_ID
ADZUNA_APP_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Navigate to:

```text
Repository
→ Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

Add each secret individually.

## Manual Workflow Execution

To manually run automated discovery:

```text
GitHub
→ Actions
→ Automated Job Discovery
→ Run workflow
```

This is also useful for testing the workflow without waiting for the scheduled execution.

## Local Network Restrictions

The application can be developed and tested locally even when external API access is unavailable.

Local environment:

```text
Python development
Unit testing
Syntax validation
Git operations
```

GitHub Actions environment:

```text
External API access
Scheduled execution
Telegram delivery
Secret injection
Database updates
```

This separation is useful when corporate network restrictions prevent outbound API connections from the development environment.

## Docker

The repository contains:

```text
Dockerfile
docker-compose.yml
.dockerignore
```

The Docker image uses Python 3.14 slim.

Docker is validated through GitHub Actions.

Local Docker execution is optional.