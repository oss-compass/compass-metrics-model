from compass_metrics.db_dsl import get_pr_message_count


def test_omitted_field_keeps_only_date_filter():
    filters = get_pr_message_count(["repo"], "uuid")["query"]["bool"]["filter"]
    assert len(filters) == 1
    assert None not in filters[0]["range"]


def test_explicit_field_adds_minimum_count_filter():
    filters = get_pr_message_count(["repo"], "uuid", filter_field="comments")["query"]["bool"]["filter"]
    assert filters[0] == {"range": {"comments": {"gte": 1}}}
    assert len(filters) == 2
