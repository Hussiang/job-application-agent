# Operations Guide

## Normal Automated Flow

The intended production-like flow is:

```text
GitHub Actions
      ↓
Automated Discovery
      ↓
Adzuna API
      ↓
Relevance Filtering
      ↓
Duplicate Detection
      ↓
Lifecycle Update
      ↓
Job Ranking
      ↓
Telegram Notifications
      ↓
Daily Digest
      ↓
jobs.json Update
```

## Local Development

Use the local environment for:

```text
Code development
Unit testing
Syntax validation
Application testing
Git operations
```

Start the interactive application with:

```bash
python3 main.py
```

## Automated Discovery

The non-interactive runner is:

```bash
python3 run_discovery.py
```

This runner is intended for environments with outbound internet access.

## Test Health

Run:

```bash
python3 -m pytest tests -v
```

The entire test suite should pass before changes are pushed.

## Syntax Validation

Run:

```bash
python3 -m py_compile main.py
python3 -m py_compile run_discovery.py
```

A successful compile produces no output.

## Git Health

Check the repository:

```bash
git status
```

A clean working tree should report:

```text
nothing to commit, working tree clean
```

## Job Database

Persistent job state is stored in:

```text
data/jobs.json
```

Application state is stored in:

```text
data/applications.json
```

These files should normally be managed by the application rather than manually edited.

## Adzuna Connectivity

Test network connectivity using:

```bash
curl -I --max-time 10 https://api.adzuna.com
```

A successful response indicates that outbound access to the Adzuna endpoint is available.

## Telegram Connectivity

Test:

```bash
curl -I --max-time 10 https://api.telegram.org
```

If local network restrictions prevent access, use the GitHub Actions environment for actual notification execution.

## Adzuna Failures

The Adzuna integration includes retry handling for temporary failures.

Temporary HTTP errors such as:

```text
503 Service Temporarily Unavailable
```

are retried.

When retries are exhausted, the affected search query is skipped instead of terminating the entire discovery process.

## Telegram Failures

If Telegram notifications fail, verify:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Also check external network connectivity.

Never expose the bot token in source control or shared logs.

## GitHub Actions

The repository contains:

```text
Python Tests
Automated Job Discovery
```

Monitor both from:

```text
GitHub
→ Actions
```

A green workflow indicates successful execution.

## Manual Discovery Run

To manually execute the automated discovery workflow:

```text
GitHub
→ Actions
→ Automated Job Discovery
→ Run workflow
```

This is useful for operational testing.

## Scheduled Execution

The job discovery workflow contains a cron schedule.

The scheduled process executes:

```text
run_discovery.py
```

without requiring the interactive CLI.

## GitHub Secrets

Required secrets:

```text
ADZUNA_APP_ID
ADZUNA_APP_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Secrets should be configured through GitHub repository settings rather than stored in the repository.

## Data Integrity

Before intentionally changing the JSON data model:

```text
data/jobs.json
data/applications.json
```

create a backup when appropriate.

Avoid committing timestamp-only changes caused by local test or development runs unless those changes are intentional.

## Local Network Restrictions

The development WSL environment may not have outbound access to external APIs because of corporate network restrictions.

When this occurs:

```text
Local WSL
→ development/testing

GitHub Actions
→ real external API execution
```

This is the expected operational model.

## Security

Never commit:

```text
.env
Adzuna API keys
Telegram bot tokens
private credentials
```

Use `.env` locally.

Use GitHub repository secrets for automated execution.

## Recovery

If an automated workflow creates an unexpected data change:

1. inspect the workflow output
2. inspect the Git diff
3. determine whether the database change is legitimate
4. restore or correct the data when necessary
5. run the complete test suite
6. rerun the workflow

Git history provides a recovery trail for committed database versions.

## Recommended Operational Model

### Development

```text
WSL
Python virtual environment
pytest
Git
VS Code
```

### Automated Execution

```text
GitHub Actions
Adzuna
Telegram
jobs.json
```

This model keeps development independent from the environment used for real scheduled job discovery.