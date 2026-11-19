
def build_search_queries(profile):
    target_roles = profile.get("target_roles", {})
    discovery_config = profile.get("job_discovery", {})

    locations = discovery_config.get("locations", [])
    search_keywords = discovery_config.get("search_keywords", [])

    high_priority_roles = target_roles.get("high_priority", [])
    medium_priority_roles = target_roles.get("medium_priority", [])

    queries = []
    seen = set()

    def add_query(query):
        query = " ".join(query.split()).strip()
        if query and query.lower() not in seen:
            queries.append(query)
            seen.add(query.lower())

    # Role-focused searches: high priority first, then medium priority.
    roles = high_priority_roles + medium_priority_roles

    for role in roles:
        for location in locations:
            add_query(f"{role} {location}")

    # Technical searches: group keywords to limit API request volume.
    valid_keywords = [
        keyword.strip()
        for keyword in search_keywords
        if isinstance(keyword, str) and keyword.strip()
    ]

    keyword_groups = [
        valid_keywords[index:index + 3]
        for index in range(0, len(valid_keywords), 3)
    ]

    for location in locations:
        for keyword_group in keyword_groups:
            add_query(f"{' '.join(keyword_group)} {location}")

    return queries
