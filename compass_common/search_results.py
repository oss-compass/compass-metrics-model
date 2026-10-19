"""Read total hit counts from supported search response formats."""


def total_hits(response):
    """Accept both Elasticsearch 6 integers and modern value/relation objects.

    Missing keys and unsupported total types raise instead of being silently
    interpreted as a successful empty search. This does not change the query's
    hit-count precision or interpret a lower-bound count as an exact count.
    """
    total = response["hits"]["total"]
    if isinstance(total, dict):
        return total["value"]
    if isinstance(total, int) and not isinstance(total, bool):
        return total
    raise TypeError("hits.total must be an integer or a value/relation object")
