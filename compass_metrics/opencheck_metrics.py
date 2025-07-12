""" Set of git related metrics """

from compass_metrics.db_dsl import (get_updated_since_query,
                                    get_uuid_count_query,
                                    get_message_list_query,
                                    get_pr_query_by_commit_hash)
from compass_metrics.contributor_metrics import get_contributor_list
from compass_metrics.repo_metrics import get_activity_repo_list
from compass_common.datetime import (get_time_diff_months,
                                     check_times_has_overlap,
                                     get_oldest_date,
                                     get_latest_date,
                                     get_date_list)
from compass_common.list_utils import split_list                                     
from datetime import timedelta
from compass_common.opensearch_utils import get_all_index_data
from compass_common.dict_utils import deep_get
import numpy as np
import math
import datetime
from dateutil.relativedelta import relativedelta
import pkg_resources
import json
from typing import Dict, List, Tuple, Any, Optional


global_spdx_license = None  #全局缓存变量


def get_spdx_license():
    """ Get spdx license data"""
    global global_spdx_license
    
    if global_spdx_license is None:
        spdx_license_dict = {}
        spdx_license_file_data = pkg_resources.resource_string('compass_metrics', 'resources/spdx_licenses.json')
        spdx_license_data = json.loads(spdx_license_file_data.decode('utf-8'))
        for license in spdx_license_data.get("licenses", []):
            spdx_license_dict[license["licenseId"]] = {
                "isOsiApproved": license.get("isOsiApproved", False),
                "isFsfLibre": license.get("isFsfLibre", False),
            }
        global_spdx_license = spdx_license_dict

    return global_spdx_license


def binary_artifacts(client, openchecker_index, repo_list):
    """ Is the project free of checked-in binaries? """
    binary_file_suffix = [".crx", ".deb", ".dex", ".dey", ".elf", ".o", ".a", ".so", ".macho", ".iso", ".class", ".jar",
                          ".bundle", ".dylib", ".lib", ".msi", ".dll", ".drv", ".efi", ".exe", ".ocx", ".pyc", ".pyo", ".par", ".rpm", ".wasm", ".whl"]
    binary_artifact_list = []
    for repo_url in repo_list:
        openchecker_data = get_openchecker_data(client, openchecker_index, repo_url, "binary-checker")
        if openchecker_data is not None:
            binary_file_list = deep_get(openchecker_data, ["_source", "command_result", "binary_file_list"], [])
            matched_files = [f for f in binary_file_list if '.' in f and f[f.rfind('.'):].lower() in binary_file_suffix]
            binary_artifact_list.extend(matched_files)
    binary_artifact_list = list(set(binary_artifact_list))
    result = {
        "binary_artifacts": max(10 - len(binary_artifact_list), 0),
        "binary_artifacts_detail": binary_artifact_list
    }
    return result


def license(client, openchecker_index, repo_list):
    """ Does the project declare a license?
    """
    
    spdx_license_dict = get_spdx_license()
    license_filename_list = list(map(str.lower, ["LICENSE", "COPYRIGHT", "COPYING"]))
    
    
    license_data = None
    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "scancode")
    if openchecker_data is not None:
        files = deep_get(openchecker_data, ["_source", "command_result", "files"], [])
        files = [file for file in files if file.get("detected_license_expression") is not None and any(keyword in file["path"].lower() for keyword in license_filename_list) ]
        if len(files) > 0:
            license_data = files[0]
            for file in files:
                path_split = (file["path"].lower()).split("/")
                if file["type"] == "file" and len(path_split) >= 2 and "license" in path_split[1]:
                    license_data = file
                    break 
    
    score = 0
    license_detail = {
        "license_path": None,
        "license_name": None,
        "fsf_or_osi": None
    }
    if license_data is not None:
        score = 9
        license_detail["license_path"] = license_data.get("path")
        license_detail["license_name"] = license_data.get("detected_license_expression_spdx") or license_data.get("detected_license_expression")
        if license_detail["license_name"] in spdx_license_dict and \
            (spdx_license_dict[license_detail["license_name"]]["isOsiApproved"] or spdx_license_dict[license_detail["license_name"]]["isFsfLibre"]):
            score += 1
            license_detail["fsf_or_osi"] = True
             
            
    result = {
        "license": score,
        "license_detail": license_detail
    }
    return result


def signed_releases(client, openchecker_index, repo_list):
    """ Does the project cryptographically sign releases? """
    file_suffix = [".minisig", ".asc (pgp)", "*.sig", ".sign", ".sigstore", ".intoto.jsonl"]
    
    release_list = []
    signed_release_list = []
    
    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "release-checker")
    if openchecker_data is not None:
        command_result_list = deep_get(openchecker_data, ["_source", "command_result", "signed-release-checker", "signed_files"], [])
        for item in command_result_list[:5]:
            release_list.append(item["release_name"]) 
            matched_files = [
                sig_file
                for sig_file in item["signature_files"]
                if any(suffix in sig_file for suffix in file_suffix)
            ]
            if len(matched_files) > 0:
                signed_release_list.appned(item["release_name"])
    score = None
    if len(release_list) > 0:
        score = int(len(signed_release_list) * 10 / len(release_list))
    result = {
        "signed_releases": score,
        "signed_releases_detail": {
            "release_list": release_list,
            "signed_release_list": signed_release_list
        }
    }
    return result


def sbom(client, openchecker_index, repo_list):
    """ his check tries to determine if the project maintains a Software Bill of Materials (SBOM) either as a file in the source or a release artifact """
    release_list = []
    sbom_release_list = []
    
    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "release-checker")
    if openchecker_data is not None:
        command_result_list = deep_get(openchecker_data, ["_source", "command_result", "sbom", "release_contents"], [])
        for item in command_result_list[:5]:
            release_list.append(item["release_name"]) 
            if len(item["content_files"]) > 0:
                sbom_release_list.appned(item["release_name"])
    result = {
        "sbom": 10 if len(sbom_release_list) > 0 else 0,
        "sbom_detail": {
            "release_list": release_list,
            "sbom_release_list": sbom_release_list
        }
    }
    return result



def vulnerabilities(client, openchecker_index, repo_list):
    """ Does the project have unfixed vulnerabilities? Uses the OSV service. """
    
    vulnerabilities_detail = []
    vulnerabilities_set = set()
    
    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "osv-scanner")
    if openchecker_data is not None:
        command_result_list = deep_get(openchecker_data, ["_source", "command_result", "results"], [])
        for item in command_result_list:
            for package in item["packages"]:
                vulnerabilities = [vulnerability["id"] for vulnerability in package["vulnerabilities"]]
                if len(vulnerabilities) > 0:
                    vulnerabilities_detail.appned({
                        "package_name": package["name"],
                        "vulnerabilities": vulnerabilities
                    })
                    vulnerabilities_set.update(vulnerabilities)
                
    result = {
        "vulnerabilities": max(10 - len(vulnerabilities_set), 0),
        "vulnerabilities_detail": vulnerabilities_detail
    }
    return result


def cii_best_practices(client, openchecker_index, repo_list):
    """ This check determines whether the project has earned an 
    OpenSSF (formerly CII) Best Practices Badge at the passing, silver, or gold level 
    """
    
    badge_level = 'Unknown'
    
    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "bestpractices-checker")
    if openchecker_data is not None:
        command_result = deep_get(openchecker_data, ["_source", "command_result"], {})
        badge_level = command_result.get('badge_level', 'Unknown')

    score_mapping = {
        'gold': 10,
        'silver': 7,
        'passing': 5,
        'in_progress': 2
    }
    result = {
        "cii_best_practices": score_mapping.get(badge_level.lower(), 0),
        "cii_best_practices_detail": {
            "badge_level": badge_level
        }
    }
    return result


def dangerous_workflow(client, openchecker_index, repo_list):
    """ This check determines whether the project's Action workflows has dangerous code patterns. 
    Some examples of these patterns are untrusted code checkouts, logging context and secrets, 
    or use of potentially untrusted inputs in scripts. 
    """ 
    workflow_file_list = []
    dangerous_patterns = []

    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "dangerous-workflow-checker")
    if openchecker_data is not None:
        command_result = deep_get(openchecker_data, ["_source", "command_result"], [])
        workflow_file_list = [item["workflow_file"] for item in command_result]
        dangerous_patterns = [
            {
                "type": item["type"],
                "file": item["file"],
                "line": item["line"],
                "snippet": item["snippet"]
            }
            for command_result_item in command_result
            for item in command_result_item.get("dangerous_patterns", [])
        ]
    score = 10 if workflow_file_list and not dangerous_patterns else (0 if workflow_file_list else None)
    result = {
        "dangerous_workflow": score,
        "dangerous_workflow_detail": dangerous_patterns
    }
    return result


def fuzzing(client, openchecker_index, repo_list):
    """ Fuzzing, or fuzz testing, is the practice of feeding unexpected or random data into a program to expose bugs 
    """ 
    fuzzing_detail = []

    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "fuzzing-checker")
    if openchecker_data is not None:
        command_result = deep_get(openchecker_data, ["_source", "command_result"], [])
        fuzzing_detail = [
            {
                "tool": item["tool"],
                "found": item["found"],
                "files": item["files"]
            }
            for item in command_result if item['found']
        ]
    score = 10 if len(fuzzing_detail) > 0 else 0
    result = {
        "fuzzing": score,
        "fuzzing_detail": fuzzing_detail
    }
    return result


def packaging(client, openchecker_index, repo_list):
    """ This check tries to determine if the project is published as a package
    """ 
    packaging_detail = []

    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "packaging-checker")
    if openchecker_data is not None:
        command_result = deep_get(openchecker_data, ["_source", "command_result"], [])
        packaging_detail = [
            {
                "matched": item["matched"],
                "file_path": item["file_path"],
                "line_number": item["line_number"]
            }
            for item in command_result if item['matched']
        ]
    score = 10 if len(packaging_detail) > 0 else None
    result = {
        "packaging": score,
        "packaging_detail": packaging_detail
    }
    return result


def pinned_dependencies(client, openchecker_index, repo_list):
    """ This check tries to determine if the project pins dependencies used during its build and release process.
    """ 
    
    
    def calculate_score(analysis_results):
        # 评分权重配置
        OWNED_ACTION_WEIGHT = 2
        THIRD_PARTY_ACTION_WEIGHT = 8
        NORMAL_DEPENDENCY_WEIGHT = 10
        
        # 计算加权分数
        weighted_scores = []
        
        # Actions 分数计算
        actions = analysis_results['actions']
        
        # 官方 Actions
        if actions['owned']['total'] > 0:
            owned_score = (
                actions['owned']['pinned'] / actions['owned']['total'],
                OWNED_ACTION_WEIGHT
            )
            weighted_scores.append(owned_score)
        
        # 第三方 Actions  
        if actions['third_party']['total'] > 0:
            third_party_score = (
                actions['third_party']['pinned'] / actions['third_party']['total'],
                THIRD_PARTY_ACTION_WEIGHT
            )
            weighted_scores.append(third_party_score)
        
        # 其他类型依赖
        for dep_type, stats in analysis_results['by_type'].items():
            if dep_type != "Action" and stats['total'] > 0:
                other_score = (
                    stats['pinned'] / stats['total'],
                    NORMAL_DEPENDENCY_WEIGHT
                )
                weighted_scores.append(other_score)
        
        # 计算最终加权分数
        if not weighted_scores:
            final_score = 0
        else:
            total_weighted_sum = sum(score * weight for score, weight in weighted_scores)
            total_weights = sum(weight for _, weight in weighted_scores)
            final_score = (total_weighted_sum / total_weights) * 10 
        return final_score


    score = None
    detail = {}

    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "pinned-dependencies-checker")
    if openchecker_data is not None:
        command_result = deep_get(openchecker_data, ["_source", "command_result"], {})
        analysis_results = command_result.get('analysis_results', {})
        detail["total_dependencies"] = analysis_results.get("total_dependencies", 0)
        detail["pinned_count"] = analysis_results.get("pinned_count", 0)
        detail["unpinned_count"] = analysis_results.get("unpinned_count", 0)
        
        if len(analysis_results) > 0 and analysis_results.get("total_dependencies", 0) > 0:
              score = calculate_score(analysis_results)
        
    result = {
        "pinned_dependencies": score,
        "pinned_dependencies_detail": detail
    }
    return result


def sast(client, openchecker_index, repo_list):
    """ his check tries to determine if the project uses Static Application Security Testing (SAST), 
    also known as static code analysis
    """ 
    
    sast_workflows = []
    sonar_configs = []

    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "sast-checker")
    if openchecker_data is not None:
        command_result = deep_get(openchecker_data, ["_source", "command_result"], {})
        sast_workflows = command_result.get('sast_workflows', [])
        sonar_configs = command_result.get('sonar_configs', [])
     
    result = {
        "sast": 10 if (len(sast_workflows) + len(sonar_configs)) > 0 else 0,
        "sast_detail": {
            "sast_workflows": sast_workflows,
            "sonar_configs": sonar_configs
        }
    }
    return result


def security_policy(client, openchecker_index, repo_list):
    """ This check tries to determine if the project has published a security policy. 
    It works by looking for a file named SECURITY.md (case-insensitive) in a few well-known directories.
    """ 
    
    security_policy_detail = {}

    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "security-policy-checker")
    if openchecker_data is not None:
        security_policy_detail = deep_get(openchecker_data, ["_source", "command_result"], {})
    
    file_size = security_policy_detail.get("file_size", 0)
    urls = security_policy_detail.get("urls", [])
    emails = security_policy_detail.get("emails", [])
    disclosure_keywords = security_policy_detail.get("disclosure_keywords", [])
    
    # 计算链接内容长度
    linked_content_length = 0
    for url in urls:
        linked_content_length += len(url)
    for email in emails:
        linked_content_length += len(email)
    # 检查是否有实质性文本内容（除了链接和邮箱）
    urls_count = len(urls)
    emails_count = len(emails)
    
    score = 0
    if len(urls) + len(emails) > 0:
        score += 6
    if file_size > 1 and file_size > linked_content_length + ((urls_count + emails_count) * 2):
        score += 3
    if len(disclosure_keywords) > 1:
        score += 1
        
    result = {
        "security_policy": score,
        "security_policy_detail": security_policy_detail
    }
    return result


def token_permissions(client, openchecker_index, repo_list):
    """ This check determines whether the project's automated workflows tokens follow the principle of least privilege
    """ 
    
    def _handle_undeclared_permissions(probe: str, file_path: str, score: float,
                                 has_write_permissions: Dict, undeclared_permissions: Dict) -> float:
        """处理未声明权限的评分"""
        if probe == "jobLevelPermissions":
            undeclared_permissions["jobLevel"][file_path] = True
            # 如果top级别也有写权限或未声明权限，这是特别严重的
            if (has_write_permissions["topLevel"].get(file_path, False) or 
                undeclared_permissions["topLevel"].get(file_path, False)):
                return 0
        elif probe == "topLevelPermissions":
            undeclared_permissions["topLevel"][file_path] = True
            # 如果job级别有未声明权限，这是特别严重的
            if undeclared_permissions["jobLevel"].get(file_path, False):
                return 0
            else:
                score -= 0.5
        
        return score
    
    def _handle_write_permissions(probe: str, file_path: str, token_name: str, score: float,
                            has_write_permissions: Dict, undeclared_permissions: Dict) -> float:
        """处理写权限的评分"""
        if probe == "topLevelPermissions":
            has_write_permissions["topLevel"][file_path] = True
            
            # 检查是否是write-all权限
            if token_name.lower() in ["all", "write-all"]:
                # 如果job级别也有写权限或未声明权限，这是特别严重的
                if (has_write_permissions["jobLevel"].get(file_path, False) or
                    undeclared_permissions["jobLevel"].get(file_path, False)):
                    return 0
                score -= 0.5
            else:
                # 根据具体权限类型扣分
                token_lower_tmp = token_name.lower()
                if token_lower_tmp in ["contents", "packages", "actions"]:
                    score -= 10.0  # 扣除满分
                elif token_lower_tmp in ["deployments", "security-events"]:
                    score -= 1.0
                elif token_lower_tmp in ["checks", "statuses"]:
                    score -= 0.5
                
        elif probe == "jobLevelPermissions":
            has_write_permissions["jobLevel"][file_path] = True
            
            # 如果top级别也有"all"写权限，这是特别严重的
            if has_write_permissions["topLevel"].get(file_path, False):
                return 0
            # 如果top级别有未声明权限
            if undeclared_permissions["topLevel"].get(file_path, False):
                score -= 0.5
        
        return score
    
    num_workflows = 0
    permissions = []
    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "token-permissions-checker")
    if openchecker_data is not None:
        command_result = deep_get(openchecker_data, ["_source", "command_result"], {})
        num_workflows = command_result.get("num_workflows", 0)
        permissions = command_result.get("token_permissions", [])
    score = None
    if num_workflows > 0 and len(permissions) > 0:
        score = 10
        # 跟踪每个文件的权限状态
        has_write_permissions = {"jobLevel": {}, "topLevel": {}}
        undeclared_permissions = {"jobLevel": {}, "topLevel": {}}
        for perm in permissions:
            file_path = perm.get("file_path", "")
            probe = f"{perm.get('locatio_type', '')}LevelPermissions"
            permission_level = perm.get("permission_level", "")
            token_name = perm.get("value", perm.get("name", ""))
            
            if permission_level in ["none", "read"]:
                continue
            
            # 初始化文件路径在映射中
            for level in ["jobLevel", "topLevel"]:
                if file_path not in has_write_permissions[level]:
                    has_write_permissions[level][file_path] = False
                if file_path not in undeclared_permissions[level]:
                    undeclared_permissions[level][file_path] = False
            
            # 处理未声明权限
            # if permission_level == "undeclared":
            #     score = _handle_undeclared_permissions(probe, file_path, score, has_write_permissions, undeclared_permissions)
            #     continue
            
            # 处理写权限
            if permission_level == "write":
                score = _handle_write_permissions(probe, file_path, token_name, score, has_write_permissions, undeclared_permissions)
    
        
    result = {
        "token_permissions": int(max(score, 0)) if score is not None else None,
        "token_permissions_detail": permissions
    }
    return result


def webhooks(client, openchecker_index, repo_list):
    """ his check tries to determine if the project uses Static Application Security Testing (SAST), 
    also known as static code analysis
    """ 
    
    access_token = False
    webhooks_hooks = []
    webhooks_hooks_secret = []

    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "webhooks-checker")
    if openchecker_data is not None:
        command_result = deep_get(openchecker_data, ["_source", "command_result"], {})
        access_token = command_result.get('access_token', False)
        error_msg = command_result.get('error_msg', "")
        webhooks_hooks = command_result.get('webhooks_hooks', [])
        
    score = None

    if access_token and error_msg is None:
        if not webhooks_hooks:
            score = 10
        else:
            webhooks_hooks_secret = [hook for hook in webhooks_hooks if hook.get("password")]
            score = int(len(webhooks_hooks_secret) * 10 / len(webhooks_hooks))
     
    result = {
        "webhooks": score,
        "webhooks_detail": {
            "token_exist": access_token,
            "error_msg": error_msg,
            "webhooks_hook_count": len(webhooks_hooks),
            "webhooks_hook_secret_count": len(webhooks_hooks_secret)
        }
    }
    return result


def dependents_count(client, openchecker_index, repo_list):
    """ his check tries to determine if the project uses Static Application Security Testing (SAST), 
    also known as static code analysis
    """ 
    
    bedependent_count = None

    openchecker_data = get_openchecker_data(client, openchecker_index, repo_list[0], "ohpm-info")
    if openchecker_data is not None:
        command_result = deep_get(openchecker_data, ["_source", "command_result"], {})
        bedependent = command_result.get("bedependent")
        if bedependent and isinstance(bedependent, int) and not isinstance(bedependent, bool):
            bedependent_count = bedependent
    
    result = {
        "dependents_count": bedependent_count
    }
    return result


def ci_tests(client, openchecker_index, repo_list):
    # TODO
    result = {
        "ci_tests": None
    }
    return result

def dependency_update_tool(client, openchecker_index, repo_list):
    # TODO
    result = {
        "dependency_update_tool": None
    }
    return result


def get_openchecker_data(client, openchecker_index, repo_url, command):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "label": repo_url
                        }
                    },
                    {
                        "match_phrase": {
                            "command.keyword": command
                        }
                    }
                ]
            }
        },
        "sort": [
            {
                "grimoire_creation_date": {
                    "order": "desc"
                }
            }
        ]
    }
    hits = client.search(index=openchecker_index, body=query)['hits']['hits']
    if len(hits) > 0:
        return hits[0]
    return None
    
    
            
            
    

