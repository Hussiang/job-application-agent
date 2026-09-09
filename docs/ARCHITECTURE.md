# Architecture

## Overview

The Job Application Agent is a modular Python application that separates job discovery, relevance filtering, ranking, lifecycle management, notifications, and application tracking.

The architecture is designed so that each responsibility is isolated into its own module. This makes the system easier to test, maintain, and extend.

## High-Level Architecture

```text
                         +----------------------+
                         |      Adzuna API      |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |  AdzunaJobSource     |
                         |  API Integration     |
                         +----------+-----------+
                                    |
                                    v
                    +-------------------------------+
                    |     JobDiscoveryService       |
                    |                               |
                    | - Query execution             |
                    | - New job detection           |
                    | - Duplicate detection         |
                    | - Changed job detection       |
                    | - Freshness tracking          |
                    +---------------+---------------+
                                    |
                                    v
                         +----------------------+
                         | JobRelevanceFilter   |
                         |                      |
                         | - Required keywords  |
                         | - Excluded keywords  |
                         | - Title filtering    |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |      Job Ranker       |
                         |                      |
                         | Profile-based score  |
                         | Recommendation       |
                         +----------+-----------+
                                    |
                  +-----------------+------------------+
                  |                                    |
                  v                                    v
        +----------------------+             +----------------------+
        |    Job Repository    |             | Notification Service |
        |                      |             |                      |
        |    jobs.json         |             | Telegram alerts      |
        +----------+-----------+             | Daily digest         |
                   |                         +----------+-----------+
                   |                                    |
                   v                                    v
        +----------------------+               +-------------------+
        | Application Tracker  |               | Telegram Bot API  |
        +----------+-----------+               +-------------------+
                   |
                   v
        +----------------------+
        | Application Dashboard|
        +----------------------+

                        GitHub Actions
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
       Python Tests                    Scheduled Discovery
       CI Workflow                    Job Discovery Workflow
```

## System Components

### 1. Source Layer

The source layer is responsible for obtaining job information.

Location:

```text
src/sources/
```

Main components:

```text
adzuna_job_source.py
json_job_source.py
job_source.py
job_search_source.py
```

### AdzunaJobSource

`AdzunaJobSource` integrates with the Adzuna REST API.

Responsibilities include:

- constructing API requests
- passing search parameters
- handling API responses
- retrying temporary request failures
- handling HTTP errors
- normalizing external API responses
- converting API records into internal `Job` objects

The rest of the application does not need to know the structure of the external API response because normalization happens inside the source layer.

### JsonJobSource

`JsonJobSource` loads persisted jobs from:

```text
data/jobs.json
```

It converts stored JSON records back into internal `Job` objects.

### Source Interfaces

The source interfaces provide abstractions that allow additional job sources to be added later without tightly coupling the rest of the system to Adzuna.

Potential future sources can implement the same interfaces.

## 2. Discovery Layer

Location:

```text
src/discovery/
```

Main components:

```text
search_query_builder.py
job_relevance_filter.py
job_discovery_service.py
```

### Search Query Builder

The search query builder generates job-search queries from the candidate profile.

The current configuration contains:

```text
Target roles
Locations
Discovery settings
```

The configured locations are:

```text
Hyderabad
Bengaluru
Remote
```

The query builder combines configured target roles with locations to create search queries.

### JobRelevanceFilter

The relevance filter removes jobs that are not appropriate for the candidate profile.

It evaluates job titles using:

```text
Required title keywords
Excluded title keywords
Excluded general keywords
```

This prevents unrelated or over-senior roles from entering the ranking pipeline.

Examples of exclusion criteria include:

```text
Senior
Sr
Lead
Principal
Architect
Manager
Director
Head
Staff
```

Additional title-level exclusions are maintained in:

```text
config/profile.yaml
```

### JobDiscoveryService

`JobDiscoveryService` coordinates the discovery process.

Its responsibilities include:

1. executing search queries
2. collecting jobs from the source
3. filtering irrelevant jobs
4. finding duplicate jobs
5. creating new job IDs
6. tracking first and last seen timestamps
7. detecting meaningful changes
8. updating existing records
9. reactivating previously inactive jobs
10. saving updated job data

The service separates results into:

```text
new_jobs
changed_jobs
```

This allows downstream components to treat new opportunities differently from existing listings.

## 3. Job Model

Location:

```text
src/jobs/job.py
```

The `Job` model is the core data structure used throughout the system.

Important fields include:

```text
job_id
title
company
location
description
skills
responsibilities
experience_required
certification_requirement
posted_date
source
job_url
is_active
discovered_at
first_seen
last_seen
active
telegram_notified
notification_hash
status
```

The model performs basic validation and normalization when records are created.

## 4. Job Repository

Location:

```text
src/jobs/job_repository.py
```

The repository provides persistence-related operations.

Responsibilities include:

- loading job data
- saving job data
- generating the next job ID
- updating job status
- duplicate detection
- normalized comparison

Duplicate detection uses:

```text
Normalized job URL
```

when available, or:

```text
Normalized title + company
```

when URL comparison is not available.

This is important because the discovery system performs multiple overlapping searches.

## 5. Job Ranking

Location:

```text
src/jobs/job_ranker.py
```

The ranking system evaluates discovered jobs against the candidate profile and scoring configuration.

Configuration is stored in:

```text
config/profile.yaml
config/scoring.yaml
```

The candidate profile includes skills in areas such as:

```text
AWS
Linux
Docker
Kubernetes
Terraform
Jenkins
CI/CD
Python
Monitoring
Prometheus
Grafana
```

The ranking process produces:

```text
score
recommendation
```

Typical recommendations are:

```text
STRONG APPLY
APPLY
CONSIDER
SKIP
```

The ranking result is then used by:

- shortlist display
- Telegram notifications
- daily digest
- application decision workflow

## 6. Job Lifecycle Management

Location:

```text
src/jobs/job_lifecycle_service.py
```

The system tracks discovery freshness using:

```text
first_seen
last_seen
active
```

### New Job

A new job receives:

```text
active = true
first_seen = current time
last_seen = current time
```

### Existing Job

When a previously known job is discovered again:

```text
last_seen = current time
```

### Stale Job

A job that has not been seen within the configured stale period can be marked:

```text
active = false
```

The record is retained instead of being deleted.

### Reactivation

If an inactive job is discovered again:

```text
active = true
last_seen = current time
```

This preserves historical information while allowing the job to become active again.

## 7. Meaningful Change Detection

The discovery system distinguishes between an actual job change and source-side noise.

Meaningful fields include:

```text
title
company
location
skills
responsibilities
experience_required
certification_requirement
```

Changes such as external redirect URL changes do not automatically count as a meaningful job change.

This reduces unnecessary notification activity.

## 8. Notification Layer

Location:

```text
src/notifications/
```

Main components:

```text
telegram_notifier.py
job_notification_service.py
daily_digest_service.py
```

### TelegramNotifier

`TelegramNotifier` communicates directly with the Telegram Bot API.

Responsibilities include:

- loading credentials
- constructing the Telegram API request
- sending messages
- handling failed notification requests

### JobNotificationService

This component applies notification policies.

It uses:

```text
minimum score
allowed recommendations
telegram_notified
notification_hash
```

A qualifying job can trigger a Telegram notification.

The notification fingerprint prevents the same job content from being sent repeatedly.

### Notification Hash

The system calculates a hash using meaningful job information and recommendation data.

The resulting value is stored as:

```text
notification_hash
```

This allows the system to distinguish:

```text
Same job
```

from:

```text
Meaningfully changed job
```

A redirect URL changing by itself should not create another notification.

### DailyDigestService

The daily digest produces a summary containing:

```text
Number of qualifying jobs
Recommendation counts
Top opportunities
Application status counts
```

This provides a broader daily overview without requiring an individual Telegram message for every opportunity.

## 9. Application Layer

Location:

```text
src/applications/
```

Main components:

```text
application_model.py
application_tracker.py
application_actions.py
application_dashboard.py
```

The application system is intentionally separated from the job discovery system.

### Why Separate Them?

A job and an application represent different states.

For example:

```text
Job:
active = true

Application:
status = INTERVIEW
```

The job can remain active in discovery while the candidate is already interviewing.

### Application Model

Application records contain fields such as:

```text
job_id
title
company
status
applied_date
interview_date
follow_up_date
notes
resume_version
application_url
last_updated
```

### Application Tracker

The application tracker manages:

- creating applications
- preventing duplicate applications
- updating application status
- updating interview information
- updating follow-up information
- updating notes
- loading and saving application records

Application persistence is stored in:

```text
data/applications.json
```

### Application Lifecycle

Typical flow:

```text
APPLIED
   |
   v
INTERVIEW
   |
   v
OFFER
```

Alternative outcomes include:

```text
REJECTED
WITHDRAWN
```

## 10. Application Dashboard

Location:

```text
src/applications/application_dashboard.py
```

The dashboard summarizes application activity.

Metrics include:

```text
Total Applications
Applied
Interviews
Offers
Rejected
Withdrawn
Response Rate
Interview Rate
Offer Rate
```

It also displays individual application details such as:

```text
Job ID
Company
Role
Status
Applied Date
Interview Date
Follow-up Date
Notes
```

## 11. Search and Filtering

Location:

```text
src/jobs/job_filters.py
src/jobs/job_search_menu.py
```

The CLI supports:

```text
Keyword search
Status filtering
Active-job filtering
Minimum-score filtering
Recommendation filtering
```

Keyword searches can match:

```text
Title
Company
Location
Description
Skills
```

Examples:

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

## 12. Persistence Layer

The current implementation uses JSON persistence.

Job database:

```text
data/jobs.json
```

Application database:

```text
data/applications.json
```

JSON was chosen because it provides:

- simple persistence
- human-readable records
- no database server requirement
- easy local development
- easy backup and inspection

The architecture allows a database such as PostgreSQL to be introduced later.

## 13. Configuration Layer

Location:

```text
config/
```

### profile.yaml

Contains candidate-specific configuration:

```text
candidate information
target roles
professional focus
skills
experience preferences
excluded keywords
required title keywords
job locations
notification configuration
```

### scoring.yaml

Contains job-scoring configuration.

Keeping configuration outside the Python code allows the matching strategy to be changed without modifying the application logic.

## 14. CLI Layer

The main interactive application is:

```text
main.py
```

The current menu provides:

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

A separate non-interactive runner is provided:

```text
run_discovery.py
```

This is used for automated execution.

## 15. CI/CD Architecture

Two GitHub Actions workflows are used.

### Python Test Workflow

Location:

```text
.github/workflows/test.yml
```

The workflow:

1. checks out the repository
2. installs Python
3. installs dependencies
4. runs pytest
5. builds the Docker image
6. validates Docker Compose configuration

It runs on:

```text
push to main
pull request to main
```

### Automated Job Discovery Workflow

Location:

```text
.github/workflows/job-discovery.yml
```

The workflow:

1. checks out the repository
2. installs Python
3. installs dependencies
4. injects GitHub repository secrets
5. runs `run_discovery.py`
6. updates the job database
7. commits database changes when required

The workflow supports:

```text
manual execution
scheduled execution
```

## 16. Secrets Management

External credentials are not stored in source code.

Required credentials include:

```text
ADZUNA_APP_ID
ADZUNA_APP_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

For local development they are stored in:

```text
.env
```

For GitHub Actions they are stored as:

```text
GitHub Repository Secrets
```

The `.env` file must never be committed.

## 17. Local and Remote Execution Model

The project supports two execution environments.

### Local Environment

Used for:

```text
Development
Testing
Syntax validation
Application testing
Git operations
```

### GitHub Actions Environment

Used for:

```text
Scheduled job discovery
External API access
Secret injection
Telegram delivery
Job database updates
```

This distinction is particularly useful when a corporate laptop or WSL environment has outbound network restrictions.

The application can therefore be developed and tested locally while real API-driven discovery runs in GitHub Actions.

## 18. Error Handling and Resilience

The Adzuna source implements retry behavior for temporary network and HTTP failures.

For temporary service errors such as HTTP 503:

```text
Attempt 1
   |
   v
Retry
   |
   v
Attempt 2
   |
   v
Retry
   |
   v
Attempt 3
   |
   v
Skip failed query
```

A temporary failure for one search query should not terminate the entire discovery workflow.

## 19. Testing Architecture

The project uses pytest.

Tests are located under:

```text
tests/
```

Current test coverage includes:

```text
Job filtering
Repository duplicate detection
Job status behavior
Ranking-based status changes
Telegram notification behavior
Notification deduplication
Notification threshold behavior
Meaningful change handling
Daily digest behavior
```

The full test suite can be executed using:

```bash
python3 -m pytest tests -v
```

## 20. Docker

The repository contains:

```text
Dockerfile
docker-compose.yml
.dockerignore
```

The Docker image uses:

```text
python:3.14-slim
```

Docker is validated through GitHub Actions.

Local Docker execution is optional.

## 21. Design Principles

The application follows several practical design principles.

### Separation of Concerns

Discovery, ranking, persistence, notification, and application tracking are implemented separately.

### Configuration Over Hardcoding

Candidate preferences, search locations, target roles, scoring, and notification thresholds are configurable.

### Testability

External API integrations are separated from business logic so notification and filtering behavior can be tested using mocked objects.

### Failure Isolation

A temporary failure from an external API should not terminate the entire job discovery process.

### State Persistence

Important state such as job freshness and notification state is persisted so the application can behave consistently across runs.

### Extensibility

Source interfaces allow additional job providers to be added later.

## 22. Future Architecture Improvements

Possible future enhancements include:

```text
Additional job sources
PostgreSQL persistence
Redis caching
Background workers
Semantic resume-to-job matching
AI-assisted job analysis
Web dashboard
Email notifications
Automated follow-up reminders
Job expiration detection
Advanced rate-limit management
Containerized deployment
Cloud deployment
```

## Summary

The Job Application Agent uses a modular architecture where:

```text
Sources
   ↓
Discovery
   ↓
Filtering
   ↓
Duplicate Detection
   ↓
Lifecycle Management
   ↓
Ranking
   ↓
Notifications
   ↓
Application Tracking
   ↓
Dashboard
```

GitHub Actions provides the automation layer for testing and scheduled execution.

This architecture keeps external integrations isolated from business logic and provides clear boundaries between job discovery state and application state.