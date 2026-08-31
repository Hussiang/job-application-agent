def extract_job_metadata(
    job_posting: str
) -> dict:
    lines = [
        line.strip()
        for line in job_posting.splitlines()
        if line.strip()
    ]

    title = None
    company = None
    location = None

    for line in lines:
        lower_line = line.lower()

        if (
            lower_line.startswith("job title:")
            or lower_line.startswith("title:")
        ):
            title = line.split(
                ":",
                1
            )[1].strip()

        elif lower_line.startswith("company:"):
            company = line.split(
                ":",
                1
            )[1].strip()

        elif lower_line.startswith("location:"):
            location = line.split(
                ":",
                1
            )[1].strip()

    return {
        "title": title,
        "company": company,
        "location": location,
        "description": job_posting,
        "raw_lines": lines
    }