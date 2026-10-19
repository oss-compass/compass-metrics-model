"""Aggregate activity counts without losing object-array type associations."""


def contribution_sum_aggregation(contribution_types, exclude=False):
    """Sum only the requested entries within each contributor document."""
    return {
        "sum": {
            "script": {
                "source": """
                    double total = 0;
                    for (def item : params._source.contribution_type_list) {
                        if (params.types.contains(item.contribution_type) != params.exclude) {
                            total += item.contribution;
                        }
                    }
                    return total;
                """,
                "params": {"types": contribution_types, "exclude": exclude}
            }
        }
    }


def get_contribution_types(client, index, query):
    """Discover type buckets, then aggregate their matching counts in one batch.

    Object arrays are flattened in the index. A sum over their numeric field
    includes unrelated entries even inside a contribution-type terms bucket.
    Keep the existing bucket selection/order; compute counts and contributor
    cardinalities together in a second search using the same outer filters.
    """
    response = client.search(index=index, body=query)
    buckets = response['aggregations']['contribution_types']['buckets']
    detail = []
    if buckets:
        totals_query = query.copy()
        totals_query['aggs'] = {
            'type_' + str(position): {
                'filter': {'term': {
                    'contribution_type_list.contribution_type.keyword': bucket['key']
                }},
                'aggs': {
                    'contributions': contribution_sum_aggregation([bucket['key']]),
                    'contributors': {'cardinality': {'field': 'contributor.keyword'}}
                }
            }
            for position, bucket in enumerate(buckets)
        }
        totals = client.search(index=index, body=totals_query)['aggregations']
        for position, bucket in enumerate(buckets):
            values = totals['type_' + str(position)]
            detail.append({
                'contribution_type': bucket['key'],
                'contributor': values['contributors']['value'],
                'contribution': values['contributions']['value']
            })
    return {
        'types_of_contributions': len(detail),
        'types_of_contributions_detail': detail
    }
