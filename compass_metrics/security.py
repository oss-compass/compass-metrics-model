import requests
import configparser

from compass_metrics.db_dsl import get_security_query
from compass_common.opensearch_utils import get_all_index_data
from compass_metrics.constants.security_constants import SECURITY_CONFIG

# 从 INI 文件中加载配置
config = configparser.ConfigParser()
config.read(SECURITY_CONFIG)

TPC_SERVICE_API_USERNAME = config['OPEN_CHECKService']['username']
TPC_SERVICE_API_PASSWORD = config['OPEN_CHECKService']['password']
TPC_SERVICE_API_ENDPOINT = config['OPEN_CHECKService']['endpoint']
TPC_SERVICE_SERVICE_CALLBACK_URL = config['OPEN_CHECKService']['service_callback_url']
TPC_SERVICE_SERVICE_CALLBACK_URL_TEST = config['OPEN_CHECKService']['service_callback_url_test']


def get_security_msg(client, contributors_index, repo_list, page_size, flag=True):
    """获取仓库的安全漏洞信息。

    Args:
        client: OpenSearch客户端
        contributors_index: 索引名称
        repo_list: 仓库列表
        page_size: 返回结果数量
        flag: 控制返回数据量的标志
             - True: 只返回最新的一条记录
             - False: 返回最新和最早的记录（如果只有一条则只返回该条）

    Returns:
        list: 包含一个或两个字典的列表，每个字典包含以下信息：
            - has_vulnerabilities: 是否存在漏洞（0或1）
            - vulnerability_count: 漏洞总数（基于CVE号去重）
            - packages: 所有包的漏洞信息列表
            - high_severity_count: 高危漏洞数量（基于CVE号去重）
            - scan_date: 扫描时间
    """
    # 修改查询以按时间排序
    query = get_security_query(repo_list, page_size)
    security_msg = get_all_index_data(client, index=contributors_index, body=query)

    if not security_msg:
        get_license(repo_list)
        return []

    results = []
    if security_msg:
        # 处理最新的记录
        latest_record = security_msg[0]['_source']
        results.append(process_record(latest_record))

        # 如果flag为False且有多条记录，添加最早的记录
        if not flag and len(security_msg) > 1:
            # 重新查询以获取最早的记录
            query['sort'][0]['grimoire_creation_date']['order'] = 'asc'
            earliest_msg = get_all_index_data(client, index=contributors_index, body=query)
            if earliest_msg:
                earliest_record = earliest_msg[0]['_source']
                # 确保不是同一条记录
                if earliest_record.get('grimoire_creation_date') != latest_record.get('grimoire_creation_date'):
                    results.append(process_record(earliest_record))

    return results

def security_vul_stat(client, contributors_index, repo_list, page_size):
    # 获取开源软件的安全漏洞数
    security_results = get_security_msg(client, contributors_index, repo_list, page_size)
    if not security_results:
        return {'security_vul_stat': 0, 'info': 'There is no data on security breaches'}
    result = {
        'security_vul_stat': security_results[0]['vulnerability_count'],
    }
    return result

def security_vul_fixed(client, contributors_index, repo_list, page_size):
    # 评估开源软件已暴露安全漏洞的修复情况。
    # 获取最早和最新的扫描结果
    security_results = get_security_msg(client, contributors_index, repo_list, page_size, False)

    # 初始化结果
    class VulnerabilityFixStatus:
        def __init__(self):
            self.fixed = 0
            self.unfixed = 0

    vulStatus = VulnerabilityFixStatus()

    result = {
        'security_vul_fixed': vulStatus,
        'info': None
    }

    # 如果没有扫描结果，直接返回
    if not security_results:
        result['info'] = "There are no scan results"
        return result

    # 如果只有一条扫描记录，则所有漏洞都算作未修复
    if len(security_results) == 1:
        vulStatus.unfixed = security_results[0]['vulnerability_count']
        result['info'] = "Only one scan record"
        return result

    # 获取最早和最新的CVE数量
    earliest = security_results[1]['vulnerability_count']
    latest = security_results[0]['vulnerability_count']

    # 计算修复和未修复的漏洞数量
    # 已修复 = 最早扫描中有但最新扫描中没有的CVE数量
    vulStatus.fixed = abs(latest - earliest)
    # 未修复 = 最新扫描中的CVE数量
    vulStatus.unfixed = len(latest)

    return result

def security_scanned(client, contributors_index, repo_list, page_size):
    # 返回是否有扫描，并且返回扫描工具
    # 获取数据
    security_results = get_security_msg(client, contributors_index, repo_list, page_size)

    # 初始化结果
    result = {
        'security_scanned': 0,
        'scanner': "osv scanner"
    }
    if security_results:
        result['security_scanned'] = 1
    else:
        result['info'] = "There are no scan results"
    return result

def process_record(record):
    result = {
        'has_vulnerabilities': 0,
        'vulnerability_count': 0,
        'packages': [],
        'high_severity_count': 0,
        'scan_date': record.get('grimoire_creation_date')
    }

    # 用于记录已统计的CVE
    counted_cves = set()
    high_severity_cves = set()

    # 处理安全信息
    security_info = record.get('security', [])

    # 检查是否存在真实的漏洞信息
    has_real_vulnerabilities = False
    for package in security_info:
        if package.get('vulnerabilities'):
            has_real_vulnerabilities = True
            break

    result['has_vulnerabilities'] = 1 if has_real_vulnerabilities else 0

    # 处理每个包的漏洞信息
    for package in security_info:
        package_info = {
            'name': package.get('package_name'),
            'version': package.get('package_version'),
            'vulnerabilities': []
        }

        for vuln in package.get('vulnerabilities', []):
            vulnerability = {
                'severity': vuln.get('severity'),
                'cve': vuln.get('aliases', []),
                'published': vuln.get('published'),
                'fixed_version': vuln.get('fixed_version', [])
            }
            package_info['vulnerabilities'].append(vulnerability)

            for cve in vuln.get('aliases', []):
                counted_cves.add(cve)
                if vuln.get('severity') in ['HIGH', 'CRITICAL']:
                    high_severity_cves.add(cve)

        result['packages'].append(package_info)

    result['vulnerability_count'] = len(counted_cves)
    result['high_severity_count'] = len(high_severity_cves)
    return result

# 如果没有数据，则请求opencheck
def get_license(repo):
    payload = {
        "username": TPC_SERVICE_API_USERNAME,
        "password": TPC_SERVICE_API_PASSWORD
    }

    # 获取token
    result = base_post_request("auth", payload)
    if not result["status"]:
        return {'status': False, 'message': 'no auth'}
    token = result["body"]["access_token"]

    commands = ["scancode", "osv-scanner"]
    payload = {
        "commands": commands,
        "project_url": f"{repo}.git",
        "callback_url": TPC_SERVICE_SERVICE_CALLBACK_URL,
        "task_metadata": {
            "report_type": -1
        }
    }

    # 向openchenck发送扫描项目请求
    result = base_post_request("opencheck", payload, token=token)
    if result["status"]:
        return {'status': True, 'message': result['body']}
    else:
        return {'status': False, 'message': 'no callback'}


def base_post_request(request_path, payload, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"JWT {token}"
    try:
        response = requests.post(
            f"{TPC_SERVICE_API_ENDPOINT}/{request_path}",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        resp_data = response.json()
        if "error" in resp_data:
            return {"status": False, "message": f"Error: {resp_data.get('description', 'Unknown error')}"}
        return {"status": True, "body": resp_data}
    except requests.RequestException as ex:
        return {"status": False, "message": str(ex)}
