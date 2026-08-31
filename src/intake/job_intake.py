def collect_job_posting() -> str:
    print("\nPASTE JOB POSTING\n")
    print(
        "Paste the complete job posting below."
    )
    print(
        "Type DONE on a new line when finished:\n"
    )

    lines = []

    while True:
        line = input()

        if line.strip().upper() == "DONE":
            break

        lines.append(line)

    return "\n".join(lines)