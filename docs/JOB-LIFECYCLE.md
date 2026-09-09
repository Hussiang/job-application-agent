# Job Lifecycle

The Job Application Agent maintains two separate lifecycles:

1. Job discovery lifecycle
2. Application lifecycle

These states are intentionally separated because discovering a job and applying to a job are different processes.

## Discovery State

Each job maintains:

```text
first_seen
last_seen
active
```

Notification state is also stored:

```text
telegram_notified
notification_hash
```

## New Job

When a job is discovered for the first time:

```text
active = true
first_seen = current time
last_seen = current time
```

The job receives the next available job ID.

## Existing Job

When the same job is found during a later search:

```text
last_seen = current time
```

The system updates the existing record instead of creating another job.

## Duplicate Detection

Duplicate detection uses normalized values.

The repository first checks the job URL when available.

If URL comparison is not possible, it compares normalized:

```text
title
company
```

This is important because multiple search queries can return the same listing.

## Meaningful Job Changes

The system distinguishes meaningful changes from source-side noise.

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

Changes to non-meaningful fields such as an external redirect URL do not automatically trigger a notification.

## Stale Jobs

A job that has not been seen for the configured stale period can be marked:

```text
active = false
```

The job record is retained instead of being deleted.

This allows historical discovery information to remain available.

## Reactivation

When an inactive job is discovered again:

```text
active = true
last_seen = current time
```

The job becomes active again without losing its previous history.

## Notification Lifecycle

A qualifying job may trigger a Telegram notification.

After successful notification, the system stores:

```text
telegram_notified = true
notification_hash = calculated fingerprint
```

This prevents the same job information from being repeatedly sent.

## Notification Hash

The notification fingerprint is based on meaningful job information and ranking information.

It allows the system to distinguish:

```text
Same job
```

from:

```text
Meaningfully changed job
```

A redirect URL changing by itself should not create another notification.

## Application Lifecycle

Application state is separate from discovery state.

Typical progression:

```text
APPLIED
   ↓
INTERVIEW
   ↓
OFFER
```

Alternate outcomes include:

```text
REJECTED
WITHDRAWN
```

## Example

A job can have:

```text
active = true
last_seen = recent timestamp
```

while its application has:

```text
status = INTERVIEW
```

This is intentional.

The discovery lifecycle describes whether the job opportunity is active.

The application lifecycle describes what happened to the candidate's application.

## Why the Lifecycles Are Separate

Consider the following scenario:

```text
Job:
Cloud Engineer
active = true

Application:
status = INTERVIEW
```

The job may still be available in the discovery system while the candidate has already reached the interview stage.

Keeping these states independent prevents application progress from changing the discovery state incorrectly.