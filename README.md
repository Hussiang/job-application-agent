# Job Application Agent

An automated Python-based job discovery and application tracking system that finds relevant DevOps, Cloud, Linux, Platform, and Application Support opportunities, evaluates them against a candidate profile, tracks job freshness, sends Telegram notifications, generates daily digests, and manages application progress.

## Project Overview

The Job Application Agent automates repetitive parts of a technical job search.

The system is designed to:

- discover jobs from the Adzuna API
- search across multiple target roles and locations
- filter irrelevant roles using configurable profile rules
- detect duplicate job listings
- track when jobs were first and last seen
- mark stale jobs inactive
- reactivate jobs that appear again
- score and rank jobs against a candidate profile
- send qualifying job alerts through Telegram
- generate a daily Telegram job digest
- track applications and interview progress
- search and filter stored jobs
- run automated tests with pytest
- run scheduled discovery using GitHub Actions

## Main Architecture

```text
                         +------------------+
                         |    Adzuna API    |
                         +--------+---------+
                                  |
                                  v
                     +------------------------+
                     |    Job Discovery       |
                     |       Service          |
                     +-----------+------------+
                                 |
                                 v
                     +------------------------+
                     |    Relevance Filter    |
                     +-----------+------------+
                                 |
                                 v
                     +------------------------+
                     | Duplicate Detection    |
                     | + Lifecycle Management |
                     +-----------+------------+
                                 |
                                 v
                     +------------------------+
                     |      Job Ranker        |
                     +-----------+------------+
                                 |
                    +------------+------------+
                    |                         |
                    v                         v
          +------------------+      +--------------------+
          |   jobs.json      |      | Telegram Alerts    |
          +--------+---------+      +--------------------+
                   |
                   v
          +----------------------+
          | Application Tracker  |
          +----------+-----------+
                     |
                     v
          +----------------------+
          | Application Dashboard|
          +----------------------+

                  GitHub Actions
                        |
                        v
               Scheduled Discovery
```

## Key Features

### 1. Live Job Discovery

The system uses the Adzuna API to discover jobs using combinations of target roles and locations.

Current configured locations:

- Hyderabad
- Bengaluru
- Remote

Current high-priority roles:

- Junior DevOps Engineer
- Associate DevOps Engineer
- DevOps Engineer
- Cloud Engineer
- Cloud Operations Engineer
- Cloud Support Engineer
- Application Support Engineer
- Platform Engineer
- Linux Engineer

Current medium-priority roles:

- Site Reliability Engineer
- Systems Engineer
- Infrastructure Engineer
- Cloud Infrastructure Engineer

The query builder generates role/location search combinations from `config/profile.yaml`.

### 2. Relevance Filtering

Jobs are filtered before ranking.

The filter evaluates job titles against required and excluded keywords.

Typical excluded signals include:

- Senior
- Sr
- Lead
- Principal
- Architect
- Manager
- Director
- AVP
- Vice President
- VP
- Head
- Staff

Additional title exclusions include examples such as:

- Data Platform
- AI Platform
- Java Platform
- RPA
- UiPath
- Banking
- Salesforce
- QA
- Testing
- Golang

These rules are configurable in `config/profile.yaml`.

### 3. Job Ranking

Jobs are scored against the candidate profile and scoring configuration.

The profile includes skills and experience relevant to:

- AWS
- EC2
- EKS
- ECR
- IAM
- VPC
- S3
- RDS
- ALB
- Route 53
- CloudWatch
- SNS
- Secrets Manager
- Docker
- Kubernetes
- Helm
- Terraform
- AWS CloudFormation
- Jenkins
- Git
- Prometheus
- Grafana
- Linux
- Ubuntu
- Amazon Linux 2023
- Python
- Bash
- PostgreSQL

The candidate profile also includes production-oriented experience keywords such as:

- Production Operations
- Production Support
- Incident Management
- Incident Troubleshooting
- Root Cause Analysis
- Deployment Support
- Release Management
- Change Management
- CI/CD
- Infrastructure as Code
- Cloud Automation
- Monitoring
- Observability
- Kubernetes Operations

### 4. Recommendations

Jobs are classified into recommendation categories such as:

- STRONG APPLY
- APPLY
- CONSIDER
- SKIP

The scoring configuration is maintained separately in `config/scoring.yaml`.

### 5. Duplicate Detection

The system prevents repeated storage of the same job across overlapping searches.

Duplicate detection uses:

1. normalized job URL when available
2. normalized job title + company combination

This is especially important because multiple role/location queries can return the same listing.

### 6. Job Freshness and Lifecycle

Each job tracks:

- `first_seen`
- `last_seen`
- `active`

When a job is discovered for the first time:

```text
active = true
first_seen = current time
last_seen = current time
```

When an existing job is found again:

```text
last_seen = current time
```

Jobs that have not been seen within the configured stale period can be marked inactive.

If an inactive job appears again during discovery, it is reactivated.

This allows the system to retain historical job information instead of deleting old records.

### 7. Meaningful Change Detection

Not every source-side change is treated as a meaningful change.

Meaningful fields include:

- title
- company
- location
- skills
- responsibilities
- experience requirement
- certification requirement

Source changes such as redirect URL changes should not automatically trigger another notification.

The discovery service therefore separates:

```text
new jobs
changed jobs
unchanged duplicates
```

### 8. Telegram Notifications

The system integrates with the Telegram Bot API.

Notification configuration is stored in `config/profile.yaml`.

Example:

```yaml
notifications:
  telegram:
    enabled: true
    minimum_score: 45
    recommendations:
      - STRONG APPLY
      - APPLY
      - CONSIDER
```

The notification layer uses:

- `TelegramNotifier`
- `JobNotificationService`
- `notification_hash`
- `telegram_notified`

These mechanisms reduce repeated alerts.

### 9. Notification Fingerprinting

A notification fingerprint is generated from meaningful job information and recommendation/score data.

The fingerprint is stored as:

```text
notification_hash
```

Together with:

```text
telegram_notified
```

this prevents the same opportunity from being repeatedly sent to Telegram.

### 10. Daily Job Digest

The system generates a daily Telegram digest containing:

- number of qualifying jobs
- recommendation counts
- top opportunities
- application status counts

The digest is implemented in:

```text
src/notifications/daily_digest_service.py
```

### 11. Application Tracking

Application data is stored separately from discovered job data.

Application information includes:

- job ID
- title
- company
- application status
- applied date
- interview date
- follow-up date
- notes
- resume version
- application URL
- last updated timestamp

Application statuses include:

- APPLIED
- INTERVIEW
- OFFER
- REJECTED
- WITHDRAWN

### 12. Application Dashboard

The dashboard reports:

- total applications
- applied count
- interview count
- offer count
- rejected count
- withdrawn count
- response rate
- interview rate
- offer rate

It also displays application details, interview dates, follow-up dates, and notes.

### 13. Search and Filtering

The CLI supports:

- keyword search
- status filtering
- active-job filtering
- minimum-score filtering
- recommendation filtering

Keyword search can cover:

- job title
- company
- location
- description
- skills

Example searches include:

```text
DevOps
Cloud
Linux
AWS
Kubernetes
Hyderabad
Docker
Terraform
```

## Application Lifecycle

The application lifecycle is intentionally separated from job discovery lifecycle.

Typical application progression:

```text
APPLIED
   |
   v
INTERVIEW
   |
   v
OFFER
```

Alternate outcomes include:

```text
REJECTED
WITHDRAWN
```

Job discovery state and application state are independent.

For example:

```text
Job:
active = true

Application:
status = INTERVIEW
```

A job can therefore remain active in discovery while an application for it is already in interview stage.

## Repository Structure

```text
job-application-agent/
|
+-- .github/
|   +-- workflows/
|       +-- test.yml
|       +-- job-discovery.yml
|
+-- config/
|   +-- profile.yaml
|   +-- scoring.yaml
|
+-- data/
|   +-- applications.json
|   +-- jobs.json
|
+-- docs/
|   +-- ARCHITECTURE.md
|   +-- SETUP.md
|   +-- JOB-LIFECYCLE.md
|   +-- OPERATIONS.md
|
+-- src/
|   +-- application_package/
|   +-- applications/
|   +-- core/
|   +-- discovery/
|   +-- intake/
|   +-- jobs/
|   +-- notifications/
|   +-- sources/
|
+-- tests/
|   +-- test_daily_digest.py
|   +-- test_job_filters.py
|   +-- test_job_notifications.py
|   +-- test_job_repository.py
|
+-- Dockerfile
+-- docker-compose.yml
+-- main.py
+-- run_discovery.py
+-- requirements.txt
+-- README.md
```

## Technology Stack

### Programming

- Python 3.14

### Libraries

- requests
- python-dotenv
- PyYAML
- pytest

### APIs and Services

- Adzuna API
- Telegram Bot API
- GitHub Actions

### DevOps Technologies

- Git
- GitHub
- Docker
- Docker Compose
- Linux / WSL

## Configuration

### Candidate Profile

```text
config/profile.yaml
```

Controls:

- candidate details
- target roles
- skills
- experience preferences
- exclusion rules
- job locations
- discovery configuration
- Telegram notification configuration

### Scoring

```text
config/scoring.yaml
```

Controls job scoring behavior.

## Local Setup

### Prerequisites

Recommended:

- Python 3.14
- Git
- VS Code
- WSL/Linux environment

Optional:

- Docker
- Docker Compose

### Clone the Repository

```bash
git clone https://github.com/Hussiang/job-application-agent.git
cd job-application-agent
```

### Create Virtual Environment

```bash
python3 -m venv .venv
```

### Activate Virtual Environment

```bash
source .venv/bin/activate
```

### Verify Python

```bash
which python3
python3 --version
```

### Install Dependencies

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
pip install pytest
```

## Environment Variables

Create a local `.env` file in the project root.

Example:

```text
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Never commit `.env`.

## Telegram Setup

1. Open Telegram.
2. Open BotFather.
3. Create a bot.
4. Copy the generated bot token.
5. Put the token into `.env`.
6. Send a message to the bot.
7. Retrieve the chat ID.
8. Put the chat ID into `.env`.

Example:

```text
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

## Adzuna Setup

Create an Adzuna developer account and obtain:

```text
ADZUNA_APP_ID
ADZUNA_APP_KEY
```

Place both values in `.env`.

## Run the Interactive Application

```bash
python3 main.py
```

Main menu:

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

The non-interactive runner is:

```bash
python3 run_discovery.py
```

It is intended for automated execution.

## Run Tests

Run the complete test suite:

```bash
python3 -m pytest tests -v
```

The test suite covers:

- job filtering
- repository duplicate detection
- status protection
- ranking-based status changes
- Telegram notification behavior
- duplicate notification prevention
- notification thresholds
- meaningful change handling
- daily digest behavior

## Continuous Integration

The repository contains a Python test workflow:

```text
.github/workflows/test.yml
```

It:

1. checks out the repository
2. installs Python
3. installs dependencies
4. runs pytest
5. builds the Docker image
6. validates Docker Compose configuration

The workflow runs on:

- pushes to `main`
- pull requests targeting `main`

## Automated Job Discovery

The repository also contains:

```text
.github/workflows/job-discovery.yml
```

This workflow:

1. checks out the repository
2. configures Python
3. installs dependencies
4. loads API credentials from GitHub repository secrets
5. runs `run_discovery.py`
6. updates `data/jobs.json`
7. commits database changes when required

The workflow can be:

- triggered manually
- triggered on a scheduled basis

## Required GitHub Secrets

Create these repository secrets:

```text
ADZUNA_APP_ID
ADZUNA_APP_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

GitHub path:

```text
Repository
    -> Settings
    -> Secrets and variables
    -> Actions
    -> New repository secret
```

## Local Development vs GitHub Actions

Local WSL is used for:

- coding
- unit tests
- syntax checks
- Git operations
- local application testing

GitHub Actions is used for:

- scheduled discovery
- external API access
- secret injection
- Telegram delivery
- updating the persistent job database

This separation is useful when corporate network restrictions prevent direct outbound connections from the development machine.

## Docker

The repository includes:

```text
Dockerfile
docker-compose.yml
.dockerignore
```

The Docker image is based on:

```text
python:3.14-slim
```

Docker is validated in GitHub Actions.

Local Docker execution is optional for development.

## Error Handling

The Adzuna source includes retry behavior for temporary API failures.

For example, temporary HTTP 503 errors are retried before the affected query is skipped.

A failure for one search should not terminate the entire discovery process.

## Troubleshooting

### Adzuna 503

Example:

```text
503 Service Temporarily Unavailable
```

This is treated as a temporary upstream error.

The discovery service retries the request and then skips the affected query if necessary.

### Local Network Timeout

Test connectivity:

```bash
curl -I --max-time 10 https://api.adzuna.com
```

Test Telegram:

```bash
curl -I --max-time 10 https://api.telegram.org
```

If these requests fail from WSL because of corporate network restrictions, use the GitHub Actions workflow for real external API execution.

### Telegram 404

Verify:

```text
TELEGRAM_BOT_TOKEN
```

A malformed Telegram bot token can result in a `404 Not Found` response.

### Telegram Updates Empty

If Telegram `getUpdates` returns:

```json
{"ok": true, "result": []}
```

send a message to the bot first and then call `getUpdates` again.

## Data Files

Job database:

```text
data/jobs.json
```

Application database:

```text
data/applications.json
```

The project currently uses JSON persistence to keep the application simple and portable.

## Engineering Decisions

### Why JSON?

JSON provides:

- simple persistence
- human-readable data
- no database server dependency
- easy local development

A relational database can be introduced later without redesigning the higher-level discovery and ranking modules.

### Why Separate Job and Application State?

A discovered job and an application are different concepts.

A job can be:

```text
active = true
```

while its associated application is:

```text
INTERVIEW
```

Keeping these states separate prevents lifecycle conflicts.

### Why Track first_seen and last_seen?

This allows the agent to distinguish:

- newly discovered jobs
- recurring jobs
- stale jobs
- reactivated jobs

### Why Use a Notification Hash?

External job sources can change redirect URLs or other non-critical fields.

A meaningful-content fingerprint reduces duplicate Telegram notifications.

### Why GitHub Actions?

The scheduled agent requires:

- external network access
- API credentials
- Telegram credentials

GitHub Actions provides a controlled execution environment with repository secrets and scheduled workflows.

## Security Considerations

Never commit:

```text
.env
API keys
Telegram bot tokens
private credentials
```

Credentials should be provided through:

- local `.env` for development
- GitHub repository secrets for automated execution

## Future Improvements

Potential future enhancements include:

- more job sources
- LinkedIn integration where permitted
- additional job boards
- relational database persistence
- semantic resume-to-job matching
- AI-assisted job description analysis
- automated follow-up reminders
- email notifications
- web dashboard
- richer application analytics
- job expiration detection
- improved rate-limit management
- containerized deployment

## Project Status

Current implementation includes:

- live Adzuna discovery
- configurable role/location searches
- relevance filtering
- duplicate detection
- freshness tracking
- stale-job lifecycle
- job reactivation
- job ranking
- configurable Telegram notifications
- Telegram deduplication
- daily Telegram digest
- application tracking
- application dashboard
- search/filter functionality
- automated tests
- GitHub Actions CI
- scheduled job discovery
- Docker configuration

## License

This project is intended as a personal automation and learning project.