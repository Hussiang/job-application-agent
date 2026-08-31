# Job Application Agent

A Python-based CLI application that helps analyze job postings, rank job opportunities against a candidate profile, manage job decisions, prepare application information, and track applications.

The project reduces the manual effort involved in reviewing multiple job opportunities and deciding which roles should be prioritized.

---

# Features

## Job Intake

The application allows a user to add a new job posting by pasting a job description.

The system:

* Collects the job posting
* Extracts available metadata
* Identifies job title, company, and location
* Parses the job description
* Extracts known skills
* Extracts experience requirements
* Extracts certification requirements
* Detects duplicate jobs before saving

---

## Job Ranking

Each job is analyzed against the candidate profile using a weighted scoring system.

The ranking considers:

* Role alignment
* Required skill match
* Responsibility match
* Experience requirements
* Certification requirements
* Bonus keywords
* Penalties for major mismatches

Each ranked job includes:

* Overall score
* Recommendation
* Eligibility analysis
* Skill analysis
* Matched skills
* Missing skills
* Matched responsibilities
* Fit explanation
* Application priority
* Recommended action
* Resume tailoring suggestions

Jobs are sorted from highest to lowest score.

---

## Job Recommendations

Jobs receive a recommendation based on their ranking score and eligibility:

* `STRONG APPLY`
* `APPLY`
* `SKIP`

The application also displays the highest-ranked opportunities separately.

---

# Job Lifecycle Management

Job lifecycle statuses are separate from ranking recommendations.

Supported lifecycle statuses:

```text
NEW
ANALYZED
SHORTLISTED
APPLIED
REJECTED
ARCHIVED
```

The ranking recommendation does not replace the lifecycle status system.

### Automatic Ranking Status Updates

When a job is ranked:

```text
NEW + STRONG APPLY
        ↓
SHORTLISTED
```

```text
NEW + APPLY
        ↓
SHORTLISTED
```

```text
NEW + SKIP
        ↓
ANALYZED
```

The following statuses are protected from automatic ranking updates:

* `SHORTLISTED`
* `APPLIED`
* `REJECTED`
* `ARCHIVED`

This prevents future ranking runs from overwriting manually shortlisted or completed jobs.

---

# Duplicate Detection

Before saving a new job, the application checks for duplicates.

Duplicate detection currently compares:

* Job title
* Company
* Job URL, when available

This prevents the same job from being added multiple times.

---

# Application Management

Shortlisted jobs can be prepared for application.

The workflow is:

```text
SHORTLISTED Job
        ↓
Generate Application Package
        ↓
Review Application Information
        ↓
Confirm Application
        ↓
Create Application Record
        ↓
Update Job Status to APPLIED
```

Application records contain:

* Job ID
* Job title
* Company
* Application status
* Applied date

Supported application statuses:

* `APPLIED`
* `INTERVIEW`
* `OFFER`
* `REJECTED`

---

# Application Dashboard

The application dashboard provides a summary of tracked applications.

Example:

```text
APPLICATION SUMMARY

Total Applications: 6
Applied: 5
Interview: 1
Offer: 0
Rejected: 0
```

The dashboard also displays individual application details.

---

# Job Search and Filtering

The application includes an interactive search and filtering menu.

Users can:

1. Search jobs by keyword
2. Filter jobs by lifecycle status
3. Show all jobs
4. Exit

Jobs can be searched using:

* Job title
* Company name

Jobs can also be filtered using lifecycle statuses.

---

# CLI Menu

The application uses a menu-driven workflow.

```text
JOB APPLICATION AGENT

1. Add and analyze a new job
2. Rank all jobs
3. Manage applications
4. Update application status
5. View application dashboard
6. Search and filter jobs
7. Exit
```

This allows each feature to be used independently instead of forcing the user through the entire workflow every time the application starts.

---

# Project Structure

```text
job-application-agent/
│
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── config/
│   ├── profile.yaml
│   └── scoring.yaml
│
├── data/
│   ├── jobs.json
│   └── applications.json
│
├── src/
│   ├── applications/
│   │   ├── application_actions.py
│   │   ├── application_dashboard.py
│   │   ├── application_model.py
│   │   └── application_tracker.py
│   │
│   ├── application_package/
│   │   ├── package_display.py
│   │   └── package_generator.py
│   │
│   ├── core/
│   │   ├── config_loader.py
│   │   └── skill_normalizer.py
│   │
│   ├── intake/
│   │   ├── job_intake.py
│   │   └── job_metadata_extractor.py
│   │
│   ├── jobs/
│   │   ├── job.py
│   │   ├── job_actions.py
│   │   ├── job_display.py
│   │   ├── job_filters.py
│   │   ├── job_parser.py
│   │   ├── job_ranker.py
│   │   ├── job_repository.py
│   │   ├── job_search_menu.py
│   │   └── job_shortlist.py
│   │
│   ├── resume/
│   │   └── __init__.py
│   │
│   └── sources/
│       ├── job_source.py
│       └── json_job_source.py
│
└── tests/
    ├── test_job_filters.py
    └── test_job_repository.py
```

---

# Architecture

The application follows a modular architecture with separation between intake, parsing, ranking, persistence, workflow management, and presentation.

```text
                 ┌──────────────────┐
                 │    Job Intake     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Metadata       │
                 │   Extraction     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Job Parser     │
                 │ Skills / Exp /   │
                 │ Certification    │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Job Repository   │
                 │    jobs.json     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   Job Ranking    │
                 │ Candidate Match  │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Job Lifecycle    │
                 │   Management     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Application      │
                 │ Tracking         │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Dashboard /      │
                 │ Search / Filter  │
                 └──────────────────┘
```

---

# Data Model

## Job

A job contains information such as:

* `job_id`
* `title`
* `company`
* `location`
* `description`
* `skills`
* `experience_required`
* `posted_date`
* `source`
* `job_url`
* `status`

## Application

An application contains:

* `job_id`
* `title`
* `company`
* `status`
* `applied_date`

---

# Running the Project

Clone the repository:

```bash
git clone <repository-url>
cd job-application-agent
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python3 main.py
```

---

# Running Tests

The project includes automated tests for:

* Job searching
* Job filtering
* Duplicate job detection
* Non-duplicate job detection
* Protecting `SHORTLISTED` jobs from automatic ranking updates
* Protecting `APPLIED` jobs from automatic ranking updates
* Moving `NEW` jobs to `SHORTLISTED` for `STRONG APPLY`
* Moving `NEW` jobs to `SHORTLISTED` for `APPLY`
* Moving `NEW` jobs to `ANALYZED` for `SKIP`

Run all tests using:

```bash
python3 -m pytest tests -v
```

Current test suite:

```text
10 passed
```

---

# Example Workflow

```text
Start Application
        ↓
Display Main Menu
        ↓
Choose Action
        │
        ├── Add and Analyze Job
        │       ↓
        │   Extract Metadata
        │       ↓
        │   Parse Job Description
        │       ↓
        │   Duplicate Detection
        │       ↓
        │   Save Job
        │
        ├── Rank All Jobs
        │       ↓
        │   Compare Against Candidate Profile
        │       ↓
        │   Generate Score and Recommendation
        │       ↓
        │   Update Job Lifecycle Status
        │
        ├── Manage Applications
        │
        ├── Update Application Status
        │
        ├── View Application Dashboard
        │
        └── Search and Filter Jobs
                ↓
              Return to Menu
```

---

# Design Decisions

## Modular Architecture

The application separates responsibilities into different modules.

Examples:

* `job_parser.py` handles job description parsing
* `job_ranker.py` handles job scoring and recommendations
* `job_repository.py` handles job persistence and duplicate detection
* `job_filters.py` handles job searching and filtering
* `application_tracker.py` handles application persistence
* `application_actions.py` handles the application workflow
* `main.py` acts as the CLI orchestration layer

This separation makes the application easier to test, understand, and extend.

---

## JSON-Based Persistence

The current version uses JSON files for persistence:

* `data/jobs.json`
* `data/applications.json`

This keeps the project lightweight while allowing data to persist between application runs.

Possible future replacements include:

* SQLite
* PostgreSQL
* DynamoDB

The current architecture keeps higher-level business logic reasonably separate from storage operations.

---

## Repository Pattern

`JobRepository` centralizes job persistence operations including:

* Generating the next job ID
* Saving jobs
* Updating job status
* Detecting duplicates

This avoids spreading persistence logic across multiple modules.

---

## Separation of Recommendation and Status

A ranking recommendation and a job lifecycle status represent different concepts.

Recommendations answer:

```text
Should this job be prioritized?
```

Lifecycle statuses answer:

```text
Where is this job in the application process?
```

For example:

```text
Recommendation: STRONG APPLY
Status: SHORTLISTED
```

The project intentionally keeps these concepts separate to avoid ranking logic overwriting completed application states.

---

# Future Improvements

Potential improvements include:

* Integration with real job sources
* Job board ingestion
* Database persistence
* Web interface
* REST API
* Resume tailoring automation
* AI-assisted job description analysis
* Email notifications
* Application deadlines
* Follow-up reminders
* Advanced duplicate detection
* Historical ranking analytics
* Docker containerization
* CI/CD pipeline

---

# Key Learning Areas

This project demonstrates practical experience with:

* Python
* Object-Oriented Programming
* Dataclasses
* Modular Application Design
* JSON Persistence
* Repository Pattern
* Data Parsing
* Business Rule Implementation
* Weighted Scoring Logic
* Job Lifecycle Management
* Application Tracking
* Search and Filtering
* Unit Testing with Pytest
* Virtual Environments
* Git

---

# Interview Explanation

A concise way to explain this project:

> I built a Python-based Job Application Agent to automate the job evaluation and application tracking workflow. The system accepts job postings, extracts metadata and requirements such as skills, experience, and certifications, and compares them against a candidate profile using weighted scoring logic. Jobs receive recommendations such as STRONG APPLY, APPLY, or SKIP, while lifecycle statuses are managed separately to prevent ranking runs from overwriting completed application states. I implemented duplicate detection, JSON-based persistence, application tracking, a dashboard, job search and filtering, and automated tests for core business rules. The project follows a modular architecture with separate components for parsing, ranking, persistence, workflow management, and presentation.
