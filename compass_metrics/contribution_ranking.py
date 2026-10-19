"""Find a contribution maximum without dropping low-frequency entities."""


def highest_contribution_key(client, index, query, field):
    """Scan complete entity buckets, retaining only the current winner.

    A top-terms bucket is selected by document frequency and can omit the
    entity with the largest contribution sum, or omit some of its documents
    on a shard. Composite pages include every matching key and its full sum.
    Equal sums retain the previous document-count, then ascending-key tie
    preference. The caller's repository, date, role and bot filters are kept.

    Each page contains at most 1,000 entities. Pagination costs additional
    searches and does not provide an atomic snapshot of a changing index.
    """
    composite = {
        "size": 1000,
        "sources": [{"entity": {"terms": {"field": field}}}],
    }
    body = query.copy()
    body["aggs"] = {
        "entities": {
            "composite": composite,
            "aggs": {"contribution": {"sum": {"field": "contribution"}}},
        }
    }
    winner = None
    maximum = None
    maximum_documents = 0
    while True:
        page = client.search(index=index, body=body)["aggregations"]["entities"]
        buckets = page["buckets"]
        for bucket in buckets:
            value = bucket["contribution"]["value"]
            documents = bucket["doc_count"]
            if (maximum is None or value > maximum or
                    (value == maximum and documents > maximum_documents)):
                winner = bucket["key"]["entity"]
                maximum = value
                maximum_documents = documents
        after = page.get("after_key")
        if not buckets or not after:
            break
        composite["after"] = after
    return winner
