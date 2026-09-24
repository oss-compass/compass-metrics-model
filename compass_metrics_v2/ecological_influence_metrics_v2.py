"""Ecological influence metrics (v2).

The models under compass_model_v2/community_health/ecological_influence declare
partner-diversity, partner-influence and technology-adoption metrics. Those
metrics historically had no implementation, no default threshold and no entry in
the metrics_switch of BaseMetricsModel, so instantiating one of the models raised
KeyError before a single value was computed.

The functions below implement the metrics that the data ingested by this
repository can actually feed. The data source is the enriched contributor index
(contributors_enriched_index): for every contributor and time range it stores the
organization the contributor belongs to, the CHAOSS ecological role
(ecological_type: organization/individual manager or participant), the mileage
role assigned by the contributor mileage algorithm (core/regular/casual) and the
contribution counters (contribution, which includes star/fork actions, and
contribution_without_observe, which does not).

Data sources that do not exist yet
----------------------------------
Two metrics the technology-adoption model used to declare are intentionally not
implemented here: package_downloads and paper_citations. This repository ingests
no package registry download data and no publication citation data, so any value
for them would be invented. They can be added together with their data source
once it is available.

Organization classification
---------------------------
The enriched index stores the organization name only, there is no
organization-type field yet. Research institutions are therefore recognised by
well-known name markers (university, institute, academy, ...) and every other
organization is treated as a business organization. The rule is isolated in
classify_organization so it can be unit tested and later replaced by an explicit
classification coming from the enrichment pipeline without touching the metric
functions.

Calling convention
------------------
Every public metric function follows the metrics_switch convention of
compass_model/base_metrics_model_v2.py:
    function(client, contributors_enriched_index, date, repo_list)
and returns a {metric_name: value} dict.
"""

BUSINESS_ORGANIZATION = "business_organization"
RESEARCH_INSTITUTION = "research_institution"

# Markers are matched case-insensitively against the organization name stored in
# the enriched index. The list is explicit on purpose: a reviewable heuristic is
# preferable to a hidden one, and every marker can be adjusted independently.
RESEARCH_INSTITUTION_MARKERS = (
    "university",
    "universidad",
    "universit\u00e9",
    "universit\u00e4t",
    "college",
    "institute",
    "institution",
    "academy",
    "academia",
    "school",
    "research",
    "laboratory",
    "polytechnic",
    "hospital",
    "national lab",
)


def classify_organization(organization):
    """Classify an organization name coming from the enriched contributor index.

    Returns RESEARCH_INSTITUTION when the name carries a well-known research
    marker, BUSINESS_ORGANIZATION for every other organization and None for
    contributors without an organization (individual contributors).

    The helper is pure and public on purpose: the metric functions stay trivial
    and the classification can be tested as well as replaced by an explicit
    organization type later on.
    """
    if organization is None:
        return None
    normalized = str(organization).strip().casefold()
    if not normalized:
        return None
    for marker in RESEARCH_INSTITUTION_MARKERS:
        if marker in normalized:
            return RESEARCH_INSTITUTION
    return BUSINESS_ORGANIZATION


def _share(part, total):
    """Share of part in total rounded to 4 decimals, None when total is empty."""
    if not total:
        return None
    return round(part / total, 4)


def summarize_ecological_influence(contributor_detail_list):
    """Aggregate enriched contributor records into the ecological metrics.

    contributor_detail_list is the list returned by
    contributor_metrics_v2.contributor_detail_list: one dict per contributor
    holding the aggregated contribution/contribution_without_observe counters,
    the ecological_type role, the organization and the mileage_type calculated by
    the mileage algorithm.

    The aggregation is a pure function so the metric semantics can be verified
    with plain unit tests, without an Elasticsearch cluster.
    """
    business_organizations = set()
    research_organizations = set()
    business_contributors = 0
    research_contributors = 0
    individual_core_contributors = 0
    business_contribution = 0
    research_contribution = 0
    individual_contribution = 0
    observe_contribution = 0
    total_contribution = 0

    for contributor in contributor_detail_list:
        contribution = contributor.get("contribution") or 0
        without_observe = contributor.get("contribution_without_observe") or 0
        total_contribution += contribution
        # Star and fork are the only "observe" actions tracked by the enriched
        # index; a fork in particular is a concrete reuse of the project, which
        # makes the observe counter the adoption signal available here.
        observe_contribution += max(0, contribution - without_observe)

        organization = contributor.get("organization")
        organization_type = classify_organization(organization)
        if organization_type == RESEARCH_INSTITUTION:
            research_organizations.add(organization)
            research_contributors += 1
            research_contribution += contribution
        elif organization_type == BUSINESS_ORGANIZATION:
            business_organizations.add(organization)
            business_contributors += 1
            business_contribution += contribution
        else:
            individual_contribution += contribution

        ecological_type = str(contributor.get("ecological_type") or "")
        if ecological_type.startswith("individual") and contributor.get("mileage_type") == "core":
            individual_core_contributors += 1

    return {
        # Partner diversity: how many partners of each kind take part.
        "business_org_count": len(business_organizations),
        "business_org_contributors": business_contributors,
        "research_institution_count": len(research_organizations),
        "research_institution_developers": research_contributors,
        "individual_core_contributors": individual_core_contributors,
        # Partner influence: share of the contribution volume of each kind.
        "business_org_influence": _share(business_contribution, total_contribution),
        "research_institution_influence": _share(research_contribution, total_contribution),
        "individual_contributor_influence": _share(individual_contribution, total_contribution),
        # Technology adoption signals available in the enriched index.
        "open_source_adoption": observe_contribution,
        "commercial_adoption": len(business_organizations),
    }


def _ecological_influence_summary(client, contributors_enriched_index, date, repo_list):
    """Load the enriched contributor data and aggregate it for one period.

    The contributor_metrics_v2 import is done lazily so this module and its pure
    helpers can be imported and unit tested without the Elasticsearch stack.
    """
    from compass_metrics_v2.contributor_metrics_v2 import contributor_detail_list

    detail = contributor_detail_list(client, contributors_enriched_index, date, repo_list)
    return summarize_ecological_influence(detail["contributor_detail_list"])


def _metric(client, contributors_enriched_index, date, repo_list, metric_name):
    """Return the single metric metric_name for the model to consume."""
    summary = _ecological_influence_summary(client, contributors_enriched_index, date, repo_list)
    return {metric_name: summary[metric_name]}


def business_org_count(client, contributors_enriched_index, date, repo_list):
    """Number of distinct business organizations active in the period."""
    return _metric(client, contributors_enriched_index, date, repo_list, "business_org_count")


def business_org_contributors(client, contributors_enriched_index, date, repo_list):
    """Number of contributors affiliated with a business organization."""
    return _metric(client, contributors_enriched_index, date, repo_list, "business_org_contributors")


def research_institution_count(client, contributors_enriched_index, date, repo_list):
    """Number of distinct research institutions active in the period."""
    return _metric(client, contributors_enriched_index, date, repo_list, "research_institution_count")


def research_institution_developers(client, contributors_enriched_index, date, repo_list):
    """Number of contributors affiliated with a research institution."""
    return _metric(client, contributors_enriched_index, date, repo_list, "research_institution_developers")


def individual_core_contributors(client, contributors_enriched_index, date, repo_list):
    """Number of individual (unaffiliated) core contributors in the period."""
    return _metric(client, contributors_enriched_index, date, repo_list, "individual_core_contributors")


def business_org_influence(client, contributors_enriched_index, date, repo_list):
    """Share of the contribution volume coming from business organizations."""
    return _metric(client, contributors_enriched_index, date, repo_list, "business_org_influence")


def research_institution_influence(client, contributors_enriched_index, date, repo_list):
    """Share of the contribution volume coming from research institutions."""
    return _metric(client, contributors_enriched_index, date, repo_list, "research_institution_influence")


def individual_contributor_influence(client, contributors_enriched_index, date, repo_list):
    """Share of the contribution volume coming from individual contributors."""
    return _metric(client, contributors_enriched_index, date, repo_list, "individual_contributor_influence")


def open_source_adoption(client, contributors_enriched_index, date, repo_list):
    """Open-source adoption: star/fork (observe) actions in the period."""
    return _metric(client, contributors_enriched_index, date, repo_list, "open_source_adoption")


def commercial_adoption(client, contributors_enriched_index, date, repo_list):
    """Commercial adoption: business organizations contributing in the period."""
    return _metric(client, contributors_enriched_index, date, repo_list, "commercial_adoption")
