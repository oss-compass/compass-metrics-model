import math


def get_score_by_criticality_score(metrics_data, metrics_weights_thresholds):
    """ Calculation of model scores by criticality_score algorithm,
     Reference Links https://github.com/ossf/criticality_score """
    total_weight = 0
    total_score = 0
    for metrics, weights_thresholds in metrics_weights_thresholds.items():
        total_weight += weights_thresholds["weight"]
        param_data = metrics_data[metrics]
        if param_data is None:
            if weights_thresholds["weight"] >= 0:
                param_data = 0
            else:
                param_data = weights_thresholds["threshold"]
        total_score += get_param_score(param_data, weights_thresholds["threshold"], weights_thresholds["weight"])
    try:
        return round(total_score / total_weight, 5)
    except ZeroDivisionError:
        return 0.0


def get_score_by_aggregate_score(metrics_data, metrics_weights_thresholds):
    """ GetAggregateScore returns the aggregate score. 
    total_score = Σ(score × weight) / Σ(weight) 
    """
    total_weight = 0
    total_score = 0
    for metrics, weights_thresholds in metrics_weights_thresholds.items():
        score = metrics_data[metrics]
        if score is not None:
            weight = weights_thresholds["weight"]
            total_score += (score * weight)
            total_weight += weight
    try:
        return round(total_score / total_weight, 2)
    except ZeroDivisionError:
        return 0.0
    


def get_param_score(param, max_value, weight=1):
    """Return paramater score given its current value, max value and parameter weight."""
    return (math.log(1 + param) / math.log(1 + max(param, max_value))) * weight


def normalize(score, min_score, max_score):
    """ score normalize """
    return (score - min_score) / (max_score - min_score)


def get_medium(L):
    L.sort()
    n = len(L)
    m = int(n/2)
    if n == 0:
        return None
    elif n % 2 == 0:
        return (L[m]+L[m-1])/2.0
    else:
        return L[m]
