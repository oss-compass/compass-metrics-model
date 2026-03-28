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



def get_score_by_criticality_score_with_mapping(metrics_data, metrics_weights_thresholds, name_mapping=None):
    total_weight = 0
    total_score = 0

    for config_key, weights_thresholds in metrics_weights_thresholds.items():
        weight = abs(weights_thresholds.get("weight", 0))
        total_weight += weight

        data_key = config_key.replace("_time_by_period", "").replace("_by_period", "")

        if config_key == 'repo_stars_by_period':
            param_data = metrics_data.get('stars_added')
        elif config_key == 'repo_forks_by_period':
            param_data = metrics_data.get('forks_added')
        else:
            param_data = metrics_data.get(data_key)

        # param_data = metrics_data.get(data_key)

        if isinstance(param_data, dict):
            valid_values = [v for v in param_data.values() if v is not None]
            param_data = sum(valid_values) / len(valid_values) if valid_values else 0

        # 获取是否为反向指标的标签和阈值
        is_reverse = weights_thresholds.get("is_reverse", False)
        threshold = weights_thresholds.get("threshold", 1)
        if threshold <= 0:  # 防止阈值配置错误导致除以 0
            threshold = 1

        if param_data is None:
            if is_reverse:
                # 反向指标的最差情况是达到或超过 threshold，此时应该拿 0 分
                param_data = threshold
            else:
                # 正向指标的最差情况是 0
                param_data = 0

        if is_reverse:
            # 针对越小越好的指标，使用“线性扣分”模型
            # 公式：权重 * max(0, 1 - (实际值 / 阈值))。超过阈值保底拿 0 分。
            actual_score = weight * max(0, 1 - (param_data / threshold))
        else:
            # 正向指标依然走原生的底层对数模型
            actual_score = get_param_score(param_data, threshold, weight)

        total_score += actual_score

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
