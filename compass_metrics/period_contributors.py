"""Classify contributor activity across all records in a selected period."""

_CODE_TYPES = ["pr_creation", "pr_comments", "code_author", "code_committer", "pr_merged"]


def get_non_code_contributor_counts(client, index, query):
    """Count active non-code people and their role subsets over the same scope.

    Enrichment stores a contributor separately for each repository/week. Code
    on any selected record excludes that contributor; a non-code record on a
    different date must not admit them again. Pure observers have no positive
    contribution_without_observe. Role membership must also have actual
    activity, rather than only a star/fork under that role.

    Composite pagination avoids truncating the contributor set or retaining
    all contributor identities in memory. Searches use the caller's original
    date, repository and bot filters. Counts are exact for the returned pages;
    an index changing between pages is not a point-in-time snapshot.
    """
    actual = {"range": {"contribution_without_observe": {"gt": 0}}}
    composite = {
        "size": 1000,
        "sources": [{"contributor": {"terms": {"field": "contributor.keyword"}}}]
    }
    body = query.copy()
    body["aggs"] = {
        "contributors": {
            "composite": composite,
            "aggs": {
                "code": {"filter": {"terms": {
                    "contribution_type_list.contribution_type.keyword": _CODE_TYPES
                }}},
                "actual": {"filter": actual},
                "org_actual": {"filter": {"bool": {"must": [
                    actual, {"match_phrase": {"ecological_type": "organization"}}
                ]}}},
                "individual_actual": {"filter": {"bool": {"must": [
                    actual, {"match_phrase": {"ecological_type": "individual participant"}}
                ]}}}
            }
        }
    }
    counts = {"total": 0, "org": 0, "individual": 0}
    while True:
        page = client.search(index=index, body=body)["aggregations"]["contributors"]
        buckets = page["buckets"]
        for bucket in buckets:
            if bucket["actual"]["doc_count"] and not bucket["code"]["doc_count"]:
                counts["total"] += 1
                counts["org"] += int(bool(bucket["org_actual"]["doc_count"]))
                counts["individual"] += int(bool(bucket["individual_actual"]["doc_count"]))
        after = page.get("after_key")
        if not buckets or not after:
            break
        composite["after"] = after
    return counts
