def build_search_queries(profile):

    target_roles = profile.get(
        "target_roles",
        {},
    )

    discovery_config = profile.get(
        "job_discovery",
        {},
    )

    locations = discovery_config.get(
        "locations",
        [],
    )

    high_priority_roles = target_roles.get(
        "high_priority",
        [],
    )

    queries = []

    for role in high_priority_roles:
        for location in locations:

            query = (
                f"{role} {location}"
            )

            queries.append(query)

    return queries