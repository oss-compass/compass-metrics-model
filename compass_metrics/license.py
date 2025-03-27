from compass_metrics.db_dsl import get_license_query
from compass_common.opensearch_utils import get_all_index_data
from compass_metrics.constants.license_constants import (
    LICENSE_COMPATIBILITY, COMMERCIAL_ALLOWED_LICENSES, WEAK_LICENSES, CLAIM_REQUIRED_LICENSES)

def get_license_msg(client, contributors_index, date, repo_list, page_size=1):
    """获取仓库开源许可证信息。
        只取一条，如果有多条则取grimoire_creation_date最新的
        """
    query = get_license_query(repo_list, page_size, date)
    license_msg = get_all_index_data(client, index=contributors_index, body=query)

    # 初始化存储所有许可证的集合
    all_licenses = set()
    osi_licenses = set()
    non_osi_licenses = set()

    # 遍历每个结果
    for item in license_msg:
        if '_source' in item and 'license' in item['_source']:
            license_info = item['_source']['license']

            # 获取各类许可证信息
            if 'license_list' in license_info:
                all_licenses.update(license_info['license_list'])
            if 'osi_license_list' in license_info:
                osi_licenses.update(license_info['osi_license_list'])
            if 'non_osi_licenses' in license_info:
                non_osi_licenses.update(license_info['non_osi_licenses'])

    # 转换为列表（如果需要）
    result = {
        'license_list': list(all_licenses),
        'osi_license_list': list(osi_licenses),
        'non_osi_licenses': list(non_osi_licenses)
    }

    return result


def license_conflicts_exist(client, contributors_index, date, repo_list, page_size=1):
    """检查仓库是否存在许可证冲突（同时存在 OSI 和非 OSI 许可证）。

    Args:
        client: Elasticsearch 客户端
        contributors_index: 索引名称
        repo_list: 仓库列表
        page_size: 返回结果数量

    """
    flag = 0
    license_msg = get_license_msg(client, contributors_index, date, repo_list, page_size)

    # 检查是否同时存在 OSI 和非 OSI 许可证
    has_osi = len(license_msg['osi_license_list']) > 0
    has_non_osi = len(license_msg['non_osi_licenses']) > 0

    if has_osi and has_non_osi:
        flag = 0
    else:
        flag = 1
    result = {
        'license_conflicts_exist': flag
    }
    return result


def license_dep_conflicts_exist(client, contributors_index, date, repo_list, page_size=1):
    """检查仓库的许可证兼容性。

    Args:
        client: Elasticsearch 客户端
        contributors_index: 索引名称
        repo_list: 仓库列表
        page_size: 返回结果数量

    Returns:
        dict: 包含许可证兼容性检查结果
    """
    # 获取许可证信息
    license_msg = get_license_msg(client, contributors_index, date, repo_list, page_size)

    # 获取所有许可证
    licenses = _get_normalized_licenses(license_msg)

    # 检查许可证兼容性
    compatibility_result = check_license_compatibility(licenses)

    result = {
        'status': compatibility_result['status'],
        'details': compatibility_result['details'],
        'license_list': licenses,
        'osi_license_list': [license.lower() for license in license_msg.get('osi_license_list', [])],
        'non_osi_licenses': [license.lower() for license in license_msg.get('non_osi_licenses', [])],
        'license_dep_conflicts_exist': 0 if compatibility_result['status'] == 'incompatible' else 1
    }

    return result


def license_is_weak(client, contributors_index, date, repo_list, page_size=1):
    """
    检查仓库的许可证是否为宽松型或弱著作权许可证。
    宽松型许可证包括：MIT、Apache、BSD等
    弱著作权许可证包括：LGPL、MPL等

    Args:
        client: Elasticsearch 客户端
        contributors_index: 索引名称
        repo_list: 仓库列表
        page_size: 返回结果数量

    Returns:
        dict: 包含许可证类型检查结果
    """
    # 获取许可证信息
    license_msg = get_license_msg(client, contributors_index, date, repo_list, page_size)
    licenses = _get_normalized_licenses(license_msg)

    # 检查是否所有许可证都是宽松型的
    all_weak = all(license in WEAK_LICENSES for license in licenses)

    result = {
        'license_is_weak': 1 if all_weak else 0,
        'license_list': licenses,
        'details': 'All licenses are permissive or weak copyright licenses' if all_weak else 'A non-permissive license exists'
    }

    return result


def license_change_claims_required(client, contributors_index, date, repo_list, page_size=1):
    """
    检查仓库的许可证是否要求对软件变更进行声明。
    某些许可证（如 GPL、LGPL、MPL）要求对软件的修改进行声明，
    而另一些（如 MIT、Apache）则相对宽松。

    Args:
        client: Elasticsearch 客户端
        contributors_index: 索引名称
        repo_list: 仓库列表
        page_size: 返回结果数量

    Returns:
        dict: 包含许可证变更声明要求的检查结果
    """
    # 获取许可证信息
    license_msg = get_license_msg(client, contributors_index, date, repo_list, page_size)
    licenses = _get_normalized_licenses(license_msg)

    # 检查是否有任何许可证要求声明变更
    claims_required = any(license in CLAIM_REQUIRED_LICENSES for license in licenses)

    # 找出需要声明的许可证
    required_licenses = [license for license in licenses if license in CLAIM_REQUIRED_LICENSES]

    result = {
        'license_change_claims_required': 1 if claims_required else 0,
        'license_list': licenses,
        'licenses_requiring_claims': required_licenses,
        'details': 'Requires declaration of software changes' if claims_required else 'No declaration of software changes is required'
    }

    return result


def license_commercial_allowed(client, contributors_index, date, repo_list, page_size=1):
    """
    检查仓库的许可证是否允许修改后闭源（商业化使用）。
    包括宽松许可证（如MIT、Apache）和弱著作权许可证（如LGPL、MPL）。

    Args:
        client: Elasticsearch 客户端
        contributors_index: 索引名称
        repo_list: 仓库列表
        page_size: 返回结果数量

    Returns:
        dict: 包含许可证商业化许可检查结果
    """
    # 获取许可证信息
    license_msg = get_license_msg(client, contributors_index, date, repo_list, page_size)
    licenses = _get_normalized_licenses(license_msg)

    # 检查是否所有许可证都允许闭源
    all_commercial_allowed = all(license in COMMERCIAL_ALLOWED_LICENSES for license in licenses)

    # 找出不允许闭源的许可证
    non_commercial_licenses = [license for license in licenses if license not in COMMERCIAL_ALLOWED_LICENSES]

    result = {
        'license_commercial_allowed': 1 if all_commercial_allowed else 0,
        'license_list': licenses,
        'non_commercial_licenses': non_commercial_licenses,
        'details': 'All licenses allow closed source modification' if all_commercial_allowed else 'There are licenses that do not allow closed source'
    }

    return result


def _get_normalized_licenses(msg):
    return [lic.lower() for lic in msg.get('license_list', [])]

def check_license_compatibility(licenses):
    """检查许可证之间的兼容性

    Args:
        licenses: 许可证列表

    Returns:
        dict: 兼容性问题的详细信息
    """
    if not licenses:
        return {
            'status': 'compatible',
            'details': '没有发现许可证'
        }

    # 将许可证名称统一为小写
    licenses = [lic.lower() for lic in licenses]

    # 检查是否有未知的许可证
    unknown_licenses = [lic for lic in licenses if lic not in LICENSE_COMPATIBILITY]
    if unknown_licenses:
        return {
            'status': 'unknown',
            'details': f'Discover unknown licenses: {unknown_licenses}'
        }

    # 检查许可证兼容性
    incompatible_pairs = []
    for i, lic1 in enumerate(licenses):
        for lic2 in licenses[i + 1:]:
            if lic2 not in LICENSE_COMPATIBILITY[lic1]:
                incompatible_pairs.append((lic1, lic2))

    if incompatible_pairs:
        return {
            'status': 'incompatible',
            'details': f'Incompatible license combination found: {incompatible_pairs}'
        }

    return {
        'status': 'compatible',
        'details': 'All licenses are compatible'
    }