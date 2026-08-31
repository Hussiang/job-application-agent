def show_application_package(package):
    print("\nAPPLICATION PACKAGE\n")

    print(f"Job ID: {package['job_id']}")
    print(f"Role: {package['title']}")
    print(f"Company: {package['company']}")
    print(f"Recommendation: {package['recommendation']}")
    print(f"Priority: {package['priority']}")

    print("\nSKILLS TO EMPHASIZE")

    if package["skills_to_emphasize"]:
        print(
            ", ".join(
                package["skills_to_emphasize"]
            )
        )
    else:
        print("None")

    print("\nEXPERIENCE TO EMPHASIZE")

    if package["responsibilities_to_emphasize"]:
        print(
            ", ".join(
                package[
                    "responsibilities_to_emphasize"
                ]
            )
        )
    else:
        print("None")

    print("\nSKILLS NOT TO CLAIM")

    if package["missing_skills"]:
        print(
            ", ".join(
                package["missing_skills"]
            )
        )
    else:
        print("None")