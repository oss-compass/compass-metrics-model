from compass_metrics.db_dsl import get_license_query
from compass_common.opensearch_utils import get_all_index_data

# 定义许可证兼容性矩阵
LICENSE_COMPATIBILITY = {
    'mit': ['mit', 'apache-2.0', 'gpl-2.0', 'gpl-3.0', 'lgpl-2.1', 'lgpl-3.0'],
    'amazon-sl': ['amazon-sl'],
    'lgpl-2.1': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'eupl-1.2', 'rpsl-1.0', 'sleepycat', 'apache-2.0', 'ecl-2.0'],
    'lgpl-2.1-plus': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'eupl-1.2', 'rpsl-1.0', 'sleepycat', 'apache-2.0', 'ecl-2.0'],
    'lgpl-3.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'eupl-1.2', 'rpsl-1.0', 'sleepycat', 'apache-2.0', 'ecl-2.0'],
    'gpl-2.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'gpl-2.0', 'gpl-2.0-plus', 'artistic-2.0', 'cecill-2.1', 'eupl-1.1', 'eupl-1.2', 'vim', 'rpsl-1.0', 'sleepycat'],
    'gpl-2.0-plus': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'cecill-2.1', 'epl-2.0', 'eupl-1.2', 'vim', 'rpsl-1.0', 'sleepycat', 'apache-2.0', 'ecl-2.0'],
    'gpl-3.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'cecill-2.1', 'epl-2.0', 'eupl-1.2', 'vim', 'rpsl-1.0', 'sleepycat', 'apache-2.0', 'ecl-2.0'],
    'agpl-3.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'cecill-2.1', 'eupl-1.2', 'vim', 'rpsl-1.0', 'sleepycat', 'apache-2.0', 'ecl-2.0'],
    'artistic-2.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'cecill-2.1', 'epl-1.0', 'epl-2.0', 'eupl-1.1', 'eupl-1.2', 'mpl-2.0', 'ms-rl', 'osl-3.0', 'vim', 'cddl-1.0', 'cpal-1.0', 'cpl-1.0', 'ibmpl-1.0', 'lucent-pl-1.02', 'nokos-1.0a', 'rpsl-1.0', 'sun-sissl-1.1', 'sleepycat', 'spl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'cecill-2.1': ['gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'cecill-2.1', 'eupl-1.1', 'eupl-1.2', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'epl-1.0': ['artistic-2.0', 'epl-1.0', 'epl-2.0', 'eupl-1.1', 'eupl-1.2', 'lucent-pl-1.02', 'sun-sissl-1.1', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'epl-2.0': ['gpl-2.0-plus', 'gpl-3.0', 'artistic-2.0', 'epl-1.0', 'epl-2.0', 'lucent-pl-1.02', 'sun-sissl-1.1', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'eupl-1.1': ['gpl-2.0', 'artistic-2.0', 'cecill-2.1', 'epl-1.0', 'eupl-1.1', 'eupl-1.2', 'osl-3.0', 'cpl-1.0', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'eupl-1.2': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'cecill-2.1', 'epl-1.0', 'eupl-1.1', 'eupl-1.2', 'mpl-2.0', 'osl-3.0', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'mpl-2.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'eupl-1.2', 'mpl-2.0', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'ms-rl': ['artistic-2.0', 'ms-rl', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'osl-3.0': ['artistic-2.0', 'eupl-1.1', 'eupl-1.2', 'osl-3.0', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'vim': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'vim', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'cddl-1.0': ['artistic-2.0', 'cddl-1.0', 'lucent-pl-1.02', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'cpal-1.0': ['artistic-2.0', 'cpal-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'cpl-1.0': ['artistic-2.0', 'eupl-1.1', 'cpl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'ibmpl-1.0': ['artistic-2.0', 'ibmpl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'lucent-pl-1.02': ['artistic-2.0', 'cecill-2.1', 'epl-1.0', 'epl-2.0', 'eupl-1.1', 'eupl-1.2', 'mpl-2.0', 'ms-rl', 'osl-3.0', 'vim', 'cddl-1.0', 'cpal-1.0', 'cpl-1.0', 'ibmpl-1.0', 'lucent-pl-1.02', 'nokos-1.0a', 'rpsl-1.0', 'sun-sissl-1.1', 'sleepycat', 'spl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'nokos-1.0a': ['artistic-2.0', 'nokos-1.0a', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'rpsl-1.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'mpl-2.0', 'cpl-1.0', 'ibmpl-1.0', 'rpsl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'sun-sissl-1.1': ['artistic-2.0', 'lucent-pl-1.02', 'sun-sissl-1.1', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'sleepycat': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'lucent-pl-1.02', 'sleepycat', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'spl-1.0': ['artistic-2.0', 'lucent-pl-1.02', 'spl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'apache-2.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'cecill-2.1', 'epl-1.0', 'epl-2.0', 'eupl-1.1', 'eupl-1.2', 'mpl-2.0', 'ms-rl', 'osl-3.0', 'vim', 'cddl-1.0', 'cpal-1.0', 'cpl-1.0', 'ibmpl-1.0', 'lucent-pl-1.02', 'nokos-1.0a', 'rpsl-1.0', 'sun-sissl-1.1', 'sleepycat', 'spl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'ecl-2.0': ['lgpl-2.1', 'lgpl-2.1-plus', 'lgpl-3.0', 'gpl-2.0-plus', 'gpl-3.0', 'agpl-3.0', 'artistic-2.0', 'cecill-2.1', 'epl-1.0', 'epl-2.0', 'eupl-1.1', 'eupl-1.2', 'mpl-2.0', 'ms-rl', 'osl-3.0', 'vim', 'cddl-1.0', 'cpal-1.0', 'cpl-1.0', 'ibmpl-1.0', 'lucent-pl-1.02', 'nokos-1.0a', 'rpsl-1.0', 'sun-sissl-1.1', 'sleepycat', 'spl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
    'php-3.01': ['artistic-2.0', 'cecill-2.1', 'epl-1.0', 'epl-2.0', 'eupl-1.1', 'eupl-1.2', 'mpl-2.0', 'ms-rl', 'osl-3.0', 'vim', 'cddl-1.0', 'cpal-1.0', 'cpl-1.0', 'ibmpl-1.0', 'lucent-pl-1.02', 'nokos-1.0a', 'rpsl-1.0', 'sun-sissl-1.1', 'sleepycat', 'spl-1.0', 'php-3.01', 'apache-2.0', 'ecl-2.0'],
}

# 定义允许修改后闭源的许可证列表
COMMERCIAL_ALLOWED_LICENSES = [
    # 宽松许可证
    'mit',
    'bsd-2-clause',
    'bsd-3-clause',
    'bsd-4-clause',
    'apache-2.0',
    'isc',
    'ms-pl',
    'x11',
    'zlib',
    # 弱著作权许可证
    'lgpl-2.1',
    'lgpl-2.1-plus',
    'lgpl-3.0',
    'mpl-2.0',
    'cddl-1.0',
    'epl-1.0',
    'epl-2.0',
    'cpl-1.0',
    # 其他允许闭源的许可证
    'php-3.01',
    'python-2.0',
    'ruby',
    'artistic-2.0',
    'ecl-2.0',
    'osl-3.0',
    'intel'
]

# 定义宽松型和弱著作权许可证列表
WEAK_LICENSES = {
    # 宽松型许可证
    'mit',           # MIT许可证
    'apache-2.0',    # Apache 2.0
    'bsd-2-clause',  # BSD 2-Clause
    'bsd-3-clause',  # BSD 3-Clause
    'bsd-0-clause',  # BSD Zero Clause
    'isc',           # ISC许可证
    'artistic-2.0',  # Artistic License 2.0
    'python-2.0',    # Python License 2.0
    'zlib',          # zlib/libpng许可证
    'x11',           # X11许可证
    'unlicense',     # The Unlicense
    'wtfpl',         # Do What The F*ck You Want To Public License
    'cc0-1.0',       # Creative Commons Zero v1.0 Universal
    
    # 弱著作权许可证
    'lgpl-2.0',      # LGPL 2.0
    'lgpl-2.1',      # LGPL 2.1
    'lgpl-3.0',      # LGPL 3.0
    'mpl-1.1',       # Mozilla Public License 1.1
    'mpl-2.0',       # Mozilla Public License 2.0
    'cddl-1.0',      # Common Development and Distribution License 1.0
    'epl-1.0',       # Eclipse Public License 1.0
    'epl-2.0',       # Eclipse Public License 2.0
    'ms-pl',         # Microsoft Public License
    'osl-3.0',       # Open Software License 3.0
}

# 定义需要声明变更的许可证列表
CLAIM_REQUIRED_LICENSES = {
    # GNU系列
    'gpl-1.0',      # GPL 1.0要求声明修改
    'gpl-2.0',      # GPL 2.0要求声明修改
    'gpl-3.0',      # GPL 3.0要求声明修改
    'lgpl-2.0',     # LGPL 2.0要求声明修改
    'lgpl-2.1',     # LGPL 2.1要求声明修改
    'lgpl-3.0',     # LGPL 3.0要求声明修改
    'agpl-1.0',     # AGPL 1.0要求声明修改
    'agpl-3.0',     # AGPL 3.0要求声明修改
    
    # Mozilla系列
    'mpl-1.0',      # Mozilla Public License 1.0要求声明修改
    'mpl-1.1',      # Mozilla Public License 1.1要求声明修改
    'mpl-2.0',      # Mozilla Public License 2.0要求声明修改
    
    # 欧盟和其他国家的许可证
    'eupl-1.1',     # European Union Public License 1.1要求声明修改
    'eupl-1.2',     # European Union Public License 1.2要求声明修改
    'cecill-2.1',   # CeCILL Free Software License Agreement要求声明修改
    
    # 其他要求声明的许可证
    'apache-2.0',   # Apache 2.0要求声明修改
    'ms-rl',        # Microsoft Reciprocal License要求声明修改
    'osl-3.0',      # Open Software License 3.0要求声明修改
    'artistic-2.0', # Artistic License 2.0要求声明修改
    'epl-1.0',      # Eclipse Public License 1.0要求声明修改
    'epl-2.0',      # Eclipse Public License 2.0要求声明修改
    'cddl-1.0',     # Common Development and Distribution License 1.0要求声明修改
    'amazon-sl',    # Amazon Service License 要求声明修改
}

def get_license_msg(client, contributors_index, repo_list, page_size=1):
    """获取仓库开源许可证信息。
        只取一条，如果有多条则取grimoire_creation_date最新的
        """
    query = get_license_query(repo_list, page_size)
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

def license_conflicts_exist(client, contributors_index, repo_list, page_size=1):
    """检查仓库是否存在许可证冲突（同时存在 OSI 和非 OSI 许可证）。

    Args:
        client: Elasticsearch 客户端
        contributors_index: 索引名称
        repo_list: 仓库列表
        page_size: 返回结果数量

    """
    flag = 0
    license_msg = get_license_msg(client, contributors_index, repo_list, page_size)
    
    # 检查是否同时存在 OSI 和非 OSI 许可证
    has_osi = len(license_msg['osi_license_list']) > 0
    has_non_osi = len(license_msg['non_osi_licenses']) > 0

    if has_osi and has_non_osi :
        flag = 0
    else :
        flag = 1
    result = {
        'license_conflicts_exist' : flag
    }
    return result

def license_dep_conflicts_exist(client, contributors_index, repo_list, page_size=1):
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
    license_msg = get_license_msg(client, contributors_index, repo_list, page_size)
    
    # 获取所有许可证
    licenses = license_msg.get('license_list', [])
    licenses = [license.lower() for license in licenses]
    
    # 检查许可证兼容性
    compatibility_result = check_license_compatibility(licenses)
    
    result = {
        'status': compatibility_result['status'],
        'details': compatibility_result['details'],
        'license_list': licenses,
        'osi_license_list': [license.lower() for license in license_msg.get('osi_license_list', [])],
        'non_osi_licenses': [license.lower() for license in license_msg.get('non_osi_licenses', [])],
        'license_conflicts_exist': 0 if compatibility_result['status'] == 'incompatible' else 1
    }
    
    return result

def license_is_weak(client, contributors_index, repo_list, page_size=1):
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
    license_msg = get_license_msg(client, contributors_index, repo_list, page_size)
    licenses = [license.lower() for license in license_msg.get('license_list', [])]
    
    # 检查是否所有许可证都是宽松型的
    all_weak = all(license in WEAK_LICENSES for license in licenses)
    
    result = {
        'license_is_weak': 1 if all_weak else 0,
        'license_list': licenses,
        'details': '所有许可证都是宽松型或弱著作权许可证' if all_weak else '存在非宽松型许可证'
    }
    
    return result

def license_change_claims_required(client, contributors_index, repo_list, page_size=1):
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
    license_msg = get_license_msg(client, contributors_index, repo_list, page_size)
    licenses = [license.lower() for license in license_msg.get('license_list', [])]
    
    # 检查是否有任何许可证要求声明变更
    claims_required = any(license in CLAIM_REQUIRED_LICENSES for license in licenses)
    
    # 找出需要声明的许可证
    required_licenses = [license for license in licenses if license in CLAIM_REQUIRED_LICENSES]
    
    result = {
        'license_change_claims_required': 1 if claims_required else 0,
        'license_list': licenses,
        'licenses_requiring_claims': required_licenses,
        'details': '需要对软件变更进行声明' if claims_required else '不需要对软件变更进行声明'
    }
    
    return result

def license_commercial_allowed(client, contributors_index, repo_list, page_size=1):
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
    license_msg = get_license_msg(client, contributors_index, repo_list, page_size)
    licenses = [license.lower() for license in license_msg.get('license_list', [])]
    
    # 检查是否所有许可证都允许闭源
    all_commercial_allowed = all(license in COMMERCIAL_ALLOWED_LICENSES for license in licenses)
    
    # 找出不允许闭源的许可证
    non_commercial_licenses = [license for license in licenses if license not in COMMERCIAL_ALLOWED_LICENSES]
    
    result = {
        'license_commercial_allowed': 1 if all_commercial_allowed else 0,
        'license_list': licenses,
        'non_commercial_licenses': non_commercial_licenses,
        'details': '所有许可证都允许修改后闭源' if all_commercial_allowed else '存在不允许闭源的许可证'
    }
    
    return result


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
            'details': f'发现未知的许可证: {unknown_licenses}'
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
            'details': f'发现不兼容的许可证组合: {incompatible_pairs}'
        }

    return {
        'status': 'compatible',
        'details': '所有许可证都是兼容的'
    }
