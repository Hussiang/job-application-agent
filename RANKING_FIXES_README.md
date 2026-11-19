# Ranking engine update

## Files to replace in your existing project
- config/scoring.yaml
- src/jobs/job_ranker.py
- tests/test_job_ranker.py

## Backups
The following original backups from the uploaded project are included unchanged for safekeeping:
- backups/profile.yaml.before-update
- backups/resume.md.before-update
- backups/scoring.yaml.before-update

## Changes
1. Related technical job titles receive configured related-role points (10 by default). Exact high- and medium-priority target roles retain their existing scores. Unrelated titles default to 0.
2. Skill summary `percentage` now represents profile skill coverage. `evidence_strength_percentage` separately represents the evidence-adjusted skill score.
3. The recommendation's Strong Apply gate uses evidence strength, not simple skill coverage. Existing APPLY / CONSIDER score thresholds remain unchanged.
4. Seniority and experience eligibility rules remain unchanged.

## Validation
- 46 tests passed.
- compileall passed.
- YAML parsing passed.
- git diff --check passed.

## Apply
Extract this ZIP into the root of your existing job-application-agent project and allow the three updated files to replace their counterparts. The backups are included only as reference; do not overwrite or delete your local backups.
