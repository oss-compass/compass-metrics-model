# -*- coding: utf-8 -*-
"""
供应链安全 / TPC 毕业评估指标（v2）。

每个指标：`(client, opencheck_raw_index, repo_list)`，内部用 `base_opencheck_query` 查 OpenSearch，
取该 label 下对应 command 最新一条文档的 `command_result`。
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from compass_common.dict_utils import deep_get

try:
    from compass_metrics.opencheck_metrics import get_spdx_license
except Exception:  # pragma: no cover
    get_spdx_license = None  # type: ignore


def base_opencheck_query(repo_list: List[str], command: str) -> Dict[str, Any]:
    """构建 opencheck_raw 查询：command.keyword + label，按时间取最新一条。"""
    return {
        "query": {
            "bool": {
                "must": [
                    {"match": {"command.keyword": command}},
                    {"terms": {"label": repo_list}},
                ]
            }
        },
        "sort": [{"grimoire_creation_date": {"order": "desc"}}],
        "size": 1,
    }


def _fetch_command_result(client: Any, opencheck_raw_index: str, repo_list: List[str], command: str) -> Dict[str, Any]:
    try:
        result = client.search(index=opencheck_raw_index, body=base_opencheck_query(repo_list, command))
    except Exception:
        return {}
    hits = result.get("hits", {}).get("hits") or []
    if not hits:
        return {}
    src = hits[0].get("_source") or {}
    cr = dict(src.get("command_result") or {})
    if command == "oat-scanner" and cr.get("status_code") is None and src.get("status") == "success":
        cr["status_code"] = 200
    return cr


def _oat_ok(oat_full: Dict[str, Any]) -> bool:
    return int(oat_full.get("status_code") or 0) == 200


SOURCE_CODE_EXTS = (
    ".c", ".cpp", ".cc", ".h", ".hpp", ".cxx", ".cs", ".java", ".jsp", ".py", ".pyx", ".rb",
    ".js", ".jsx", ".ts", ".tsx", ".html", ".php", ".go", ".swift", ".kt", ".m", ".mm", ".rs",
    ".pl", ".vue", ".dart", ".erl", ".ex", ".exs", ".scala", ".r", ".nim", ".lua", ".groovy",
)
EXCLUDE_PATH_PATTERNS = (
    re.compile(r"hvigorfile\.ts$"),
    re.compile(r"hvigor-wrapper\.js$"),
    re.compile(r"OpenHarmonyTestRunner\.ts$"),
)


def _spdx_is_osi_approved(token: str) -> bool:
    token = (token or "").strip()
    if not token or get_spdx_license is None:
        return False
    spdx = get_spdx_license()
    info = spdx.get(token) or spdx.get(token.upper())
    if not info:
        return False
    return bool(info.get("isOsiApproved") or info.get("isFsfLibre"))


def _calc_compliance_license(
        scancode_result: Dict[str, Any],
        readme_opensource_checker_result: Dict[str, Any],
        oat_result: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    license_list: List[str] = []
    osi_license_list: List[str] = []
    non_osi_license_list: List[str] = []

    readme_opensource = bool(readme_opensource_checker_result.get("readme-opensource-checker"))
    readme_opensource_result = 1 if readme_opensource else 0
    if oat_result and oat_result.get("error"):
        readme_opensource_result = 2

    raw_rows = []
    for file in scancode_result.get("files") or []:
        if file.get("type") != "file" or not file.get("detected_license_expression"):
            continue
        path = (file.get("path") or "").lower()
        parts = path.split("/")
        if len(parts) == 2 and parts[-1] in ("readme.opensource", "oat.xml"):
            continue
        if not (len(parts) == 2 or (len(parts) >= 2 and parts[1] == "license")):
            continue
        raw_rows.append({
            "path": file.get("path"),
            "type": file.get("type"),
            "detected_license_expression": file.get("detected_license_expression"),
            "detected_license_expression_spdx": file.get("detected_license_expression_spdx"),
        })

    repl = {"(": "", ")": "", "and": "", "or": ""}
    pattern = re.compile("|".join(map(re.escape, repl.keys())))

    for raw in raw_rows:
        expr = (raw.get("detected_license_expression") or "").strip().lower()
        expr = pattern.sub(lambda m: repl.get(m.group(0), m.group(0)), expr)
        for item in expr.split():
            if "unknown" in item:
                continue
            license_list.append(item)
            if _spdx_is_osi_approved(item):
                osi_license_list.append(item)
            else:
                non_osi_license_list.append(item)

    score = 0
    if license_list and not non_osi_license_list and readme_opensource_result == 1:
        score = 10

    oat_detail: List[str] = []
    if oat_result:
        cnt = int(oat_result.get("total_count") or 0)
        if cnt > 0:
            score = 0
        oat_detail = [d.get("file") for d in (oat_result.get("details") or []) if isinstance(d, dict)]
        oat_detail = [x for x in oat_detail if x]
        if oat_result and not oat_detail:
            score = 10

    detail = {
        "readme_opensource": readme_opensource_result,
        "osi_license_list": list(dict.fromkeys(osi_license_list))[:1],
        "non_osi_licenses": list(dict.fromkeys(non_osi_license_list))[:1],
        "oat_detail": oat_detail,
    }
    if len(json.dumps(detail, ensure_ascii=False)) > 500:
        detail["oat_detail"] = oat_detail[:4]

    return {
        "compliance_license": score,
        "compliance_license_detail": json.dumps(detail, ensure_ascii=False),
        "license_included_osi": bool(score == 10),
        "compliance_license_raw": json.dumps((raw_rows[:10] + oat_detail), ensure_ascii=False),
    }


def _calc_compliance_license_compatibility(
        scancode_result: Dict[str, Any],
        oat_license_not_compatible: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    conflicts: List[Any] = []
    score = 10
    if oat_license_not_compatible:
        cnt = int(oat_license_not_compatible.get("total_count") or 0)
        details = oat_license_not_compatible.get("details") or []
        conflicts = [d for d in details if d]
        if cnt > 0:
            score = 0
    else:
        raw = scancode_result.get("license_compatibility") or scancode_result.get("license_conflicts")
        if isinstance(raw, list) and raw:
            conflicts = raw
            score = 0
        elif isinstance(raw, dict) and raw.get("conflicts"):
            conflicts = list(raw["conflicts"])
            score = 0 if conflicts else 10

    return {
        "compliance_license_compatibility": score,
        "compliance_license_compatibility_detail": json.dumps(
            {"conflicts": conflicts[:20], "count": len(conflicts)}, ensure_ascii=False
        ),
        "license_compatibility_conflicts": conflicts,
    }


def _calc_compliance_copyright_statement(
        scancode_result: Dict[str, Any],
        changed_files_result: Dict[str, Any],
        oh_commit_sha: Optional[str],
        oat_copyright_header_invalid: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    new_files = set(changed_files_result.get("new_files") or [])
    include_copyrights: List[str] = []
    not_included: List[str] = []
    raw_list: List[Dict[str, Any]] = []

    for file in scancode_result.get("files") or []:
        file_path = file.get("path") or ""
        parts = file_path.split("/")
        if len(parts) > 2 and parts[1] == "hvigor":
            continue
        rel = file_path.split("/", 1)[-1] if "/" in file_path else file_path
        if oh_commit_sha and new_files and rel not in new_files:
            continue
        if any(p.search(file_path) for p in EXCLUDE_PATH_PATTERNS):
            continue
        if file.get("type") != "file":
            continue
        if not file_path.lower().endswith(SOURCE_CODE_EXTS):
            continue
        cr = file.get("copyrights") or []
        if cr:
            include_copyrights.append(file_path)
        else:
            not_included.append(file_path)

        raw_list.append({
            "path": file_path,
            "copyrights": [c.get("copyright") for c in cr if isinstance(c, dict)],
        })

    score = 0
    if include_copyrights and not not_included:
        score = 10
    if not include_copyrights and not not_included:
        score = 10

    oat_detail: List[str] = []
    if oat_copyright_header_invalid:
        cnt = int(oat_copyright_header_invalid.get("total_count") or 0)
        if cnt > 0:
            score = 0
        oat_detail = [d.get("file") for d in (oat_copyright_header_invalid.get("details") or []) if isinstance(d, dict)]
        oat_detail = [x for x in oat_detail if x]
        if oat_copyright_header_invalid and not oat_detail:
            score = 10

    detail = {
        "include_copyrights": list(dict.fromkeys(include_copyrights))[:1],
        "not_included_copyrights": list(dict.fromkeys(not_included)),
        "oat_detail": oat_detail,
    }
    if len(json.dumps(detail, ensure_ascii=False)) > 500:
        detail["not_included_copyrights"] = list(dict.fromkeys(not_included))[:1]
        detail["oat_detail"] = oat_detail[:4]

    return {
        "compliance_copyright_statement": score,
        "compliance_copyright_statement_detail": json.dumps(detail, ensure_ascii=False),
        "non_compliant_files": list(dict.fromkeys(not_included)),
        "compliance_copyright_statement_raw": json.dumps((raw_list[:5] + oat_detail), ensure_ascii=False),
    }


def _calc_compliance_copyright_anti_tamper(oat_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not oat_result:
        return {
            "compliance_copyright_statement_anti_tamper": -1,
            "compliance_copyright_statement_anti_tamper_detail": json.dumps({"unavailable": True}),
            "tampering_risk": None,
        }
    candidates = [
        "License Copyright Tamper",
        "Copyright Tamper",
        "Third Party License Tamper",
        "Snippet Reference Invalid",
    ]
    block = None
    for k in candidates:
        if k in oat_result and isinstance(oat_result[k], dict):
            block = oat_result[k]
            break
    if not block:
        for k, v in oat_result.items():
            if isinstance(v, dict) and "tamper" in k.lower() and "total_count" in v:
                block = v
                break
    if not block:
        return {
            "compliance_copyright_statement_anti_tamper": -1,
            "compliance_copyright_statement_anti_tamper_detail": json.dumps({"unavailable": True}),
            "tampering_risk": None,
        }
    cnt = int(block.get("total_count") or 0)
    score = 0 if cnt > 0 else 10
    details = [d.get("file") for d in (block.get("details") or []) if isinstance(d, dict)]
    details = [x for x in details if x]
    return {
        "compliance_copyright_statement_anti_tamper": score,
        "compliance_copyright_statement_anti_tamper_detail": json.dumps(
            {"total_count": cnt, "sample_files": details[:10]}, ensure_ascii=False
        ),
        "tampering_risk": cnt > 0,
    }


def _calc_compliance_snippet_reference(oat_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    keys = ["Snippet Reference Invalid", "Snippet Reference", "snippet-reference"]
    block = None
    for k in keys:
        if oat_result and k in oat_result and isinstance(oat_result[k], dict):
            block = oat_result[k]
            break
    if not block:
        return {
            "compliance_snippet_reference": -1,
            "compliance_snippet_reference_detail": json.dumps({"unavailable": True}),
            "violation_count": None,
        }
    cnt = int(block.get("total_count") or 0)
    score = 0 if cnt > 0 else 10
    return {
        "compliance_snippet_reference": score,
        "compliance_snippet_reference_detail": json.dumps(
            {"total_count": cnt, "details": (block.get("details") or [])[:10]}, ensure_ascii=False
        ),
        "violation_count": cnt,
    }


def _calc_import_valid(oat_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not oat_result:
        return {"import_valid": -1, "import_valid_detail": "[]", "import_valid_raw": "[]"}
    cnt = int(oat_result.get("total_count") or 0)
    score = 0 if cnt > 0 else 10
    oat_detail = [d.get("file") for d in (oat_result.get("details") or []) if isinstance(d, dict)]
    oat_detail = [x for x in oat_detail if x]
    return {
        "import_valid": score,
        "import_valid_detail": json.dumps(oat_detail[:4], ensure_ascii=False),
        "import_valid_raw": json.dumps(oat_detail[:30], ensure_ascii=False),
    }


def _calc_security_binary_artifact(
        binary_checker_result: Dict[str, Any],
        oat_invalid_file_type: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    binary_list = list(binary_checker_result.get("binary_file_list") or [])
    suffix = {x.lower() for x in [
        ".crx", ".deb", ".dex", ".dey", ".elf", ".o", ".a", ".so", ".macho", ".iso", ".class", ".jar",
        ".bundle", ".dylib", ".lib", ".msi", ".dll", ".drv", ".efi", ".exe", ".ocx", ".pyc", ".pyo",
        ".par", ".rpm", ".wasm", ".whl",
    ]}
    matched = []
    for f in binary_list:
        if "." in f and f[f.rfind("."):].lower() in suffix:
            matched.append(f)
    if oat_invalid_file_type and int(oat_invalid_file_type.get("total_count") or 0) > 0:
        extra = [d.get("file") for d in (oat_invalid_file_type.get("details") or []) if isinstance(d, dict)]
        matched.extend(x for x in extra if x)
    matched = list(dict.fromkeys(matched))
    return {
        "security_binary_artifact": max(10 - len(matched), 0) if matched else 10,
        "security_binary_artifact_detail": json.dumps(matched[:50], ensure_ascii=False),
        "binary_violation_files": matched,
        "binary_archive_list": list(binary_checker_result.get("binary_archive_list") or []),
        "security_binary_artifact_raw": json.dumps(matched[:30], ensure_ascii=False),
    }


def _osv_severity_bucket(vuln: Dict[str, Any]) -> str:
    for s in (vuln.get("severity") or []):
        if isinstance(s, dict):
            try:
                score = float(s.get("score") or 0)
                if score >= 9:
                    return "CRITICAL"
                if score >= 7:
                    return "HIGH"
                if score >= 4:
                    return "MEDIUM"
            except (TypeError, ValueError):
                pass
    return "UNKNOWN"


def _calc_security_vulnerability(osv_scanner_result: Dict[str, Any]) -> Dict[str, Any]:
    results = osv_scanner_result.get("results") or []
    all_vulns: List[Dict[str, Any]] = []
    for item in results:
        for pkg in item.get("packages") or []:
            for v in pkg.get("vulnerabilities") or []:
                all_vulns.append(v)

    high = medium = critical = 0
    for v in all_vulns:
        b = _osv_severity_bucket(v)
        if b == "CRITICAL":
            critical += 1
        elif b == "HIGH":
            high += 1
        elif b == "MEDIUM":
            medium += 1
        elif v.get("id"):
            medium += 1

    total_unique = len({v.get("id") for v in all_vulns if v.get("id")})
    score = max(10 - min(total_unique, 10), 0)

    return {
        "security_vulnerability": score,
        "security_vulnerability_detail": json.dumps(
            {"critical": critical, "high": high, "medium": medium, "unique_ids": total_unique},
            ensure_ascii=False,
        ),
        "vuln_counts": {"critical": critical, "high": high, "medium": medium, "total_unique": total_unique},
        "security_vulnerability_raw": json.dumps(all_vulns[:30], ensure_ascii=False),
    }


def _calc_security_package_sig(release_checker_result: Dict[str, Any]) -> Dict[str, Any]:
    sig_list = list(release_checker_result.get("signature_files") or [])
    if "error" in release_checker_result:
        return {
            "security_package_sig": -1,
            "security_package_sig_detail": "[]",
            "signature_valid": None,
            "security_package_sig_raw": "[]",
        }
    score = 10 if sig_list else 6
    return {
        "security_package_sig": score,
        "security_package_sig_detail": json.dumps(sig_list[:2], ensure_ascii=False),
        "signature_valid": bool(sig_list),
        "security_package_sig_raw": json.dumps(sig_list[:30], ensure_ascii=False),
    }


def _calc_lifecycle_release_note(release_checker_result: Dict[str, Any]) -> Dict[str, Any]:
    notes = list(release_checker_result.get("release_notes") or [])
    if "error" in release_checker_result:
        return {
            "lifecycle_release_note": -1,
            "lifecycle_release_note_detail": "[]",
            "has_release_notes": None,
            "lifecycle_release_note_raw": "[]",
        }
    return {
        "lifecycle_release_note": 10 if notes else 0,
        "lifecycle_release_note_detail": json.dumps(notes[:1], ensure_ascii=False),
        "has_release_notes": bool(notes),
        "lifecycle_release_note_raw": json.dumps(notes[:30], ensure_ascii=False),
    }


def _calc_sbom_in_release(release_checker_result: Dict[str, Any]) -> Dict[str, Any]:
    sbom_part = release_checker_result.get("sbom") or {}
    contents = sbom_part.get("release_contents") or []
    has_sbom = any((c.get("content_files") or []) for c in contents if isinstance(c, dict))
    return {
        "sbom_in_release": has_sbom,
        "sbom_detail": json.dumps(contents[:3], ensure_ascii=False),
    }


def _calc_ecology_readme(
        readme_checker_result: Dict[str, Any],
        oat_no_readme: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readme_files = readme_checker_result.get("readme_file") or []
    score = 0
    for rf in readme_files:
        parts = rf.split("/")
        if len(parts) == 2 and any(x in parts[1].lower() for x in ("readme", "readme.")):
            score = 10
            break
    if oat_no_readme and int(oat_no_readme.get("total_count") or 0) > 0:
        score = 0
    return {
        "ecology_readme": score,
        "ecology_readme_detail": json.dumps({"score_0_10": score, "readme_file_count": len(readme_files)}),
        "readme_completeness_score": score,
        "ecology_readme_raw": json.dumps(readme_files[:50], ensure_ascii=False),
    }


def _calc_ecology_maintainer_doc(maintainers_checker_result: Dict[str, Any]) -> Dict[str, Any]:
    raw = list(maintainers_checker_result.get("maintainers_file") or [])
    return {
        "ecology_maintainer_doc": 10 if raw else 0,
        "ecology_maintainer_doc_detail": None,
        "committers_file_exists": bool(raw),
        "ecology_maintainer_doc_raw": json.dumps(raw[:30], ensure_ascii=False),
    }


def _calc_ecology_build_doc(build_doc_checker_result: Dict[str, Any]) -> Dict[str, Any]:
    raw = list(build_doc_checker_result.get("build-doc-checker") or [])
    return {
        "ecology_build_doc": 10 if raw else 0,
        "ecology_build_doc_detail": None,
        "has_build_install_docs": bool(raw),
        "ecology_build_doc_raw": json.dumps(raw[:30], ensure_ascii=False),
    }


def _calc_ecology_interface_doc(api_doc_checker_result: Dict[str, Any]) -> Dict[str, Any]:
    raw = list(api_doc_checker_result.get("api-doc-checker") or [])
    return {
        "ecology_interface_doc": 10 if raw else 0,
        "ecology_interface_doc_detail": None,
        "has_api_docs": bool(raw),
        "ecology_interface_doc_raw": json.dumps(raw[:30], ensure_ascii=False),
    }


def _calc_ecology_test_coverage(sonar_scanner_result: Dict[str, Any]) -> Dict[str, Any]:
    measures = deep_get(sonar_scanner_result, ["component", "measures"]) or []
    duplication_score = coverage_score = 0
    duplication_ratio = coverage_ratio = None
    ranges_dup = [(0, 2, 10), (3, 4, 8), (5, 9, 6), (10, 19, 4), (20, 99, 2), (100, 100, 0)]
    ranges_cov = [(0, 0, 0), (1, 29, 2), (30, 49, 4), (50, 69, 6), (70, 79, 8), (80, 100, 10)]

    for m in measures:
        metric = m.get("metric")
        if metric == "duplicated_lines_density":
            try:
                duplication_ratio = int(m.get("value") or 0)
            except (TypeError, ValueError):
                duplication_ratio = None
            for lo, hi, sc in ranges_dup:
                if duplication_ratio is not None and lo <= duplication_ratio <= hi:
                    duplication_score = sc
                    break
        elif metric == "coverage":
            try:
                coverage_ratio = int(m.get("value") or 0)
            except (TypeError, ValueError):
                coverage_ratio = None
            for lo, hi, sc in ranges_cov:
                if coverage_ratio is not None and lo <= coverage_ratio <= hi:
                    coverage_score = sc
                    break

    score = (duplication_score + coverage_score) / 2.0
    detail = {
        "duplication_score": duplication_score,
        "duplication_ratio": duplication_ratio,
        "coverage_score": coverage_score,
        "coverage_ratio": coverage_ratio,
    }
    return {
        "ecology_test_coverage": score,
        "ecology_test_coverage_detail": json.dumps(detail, ensure_ascii=False),
        "test_coverage_percent": coverage_ratio,
        "ecology_test_coverage_raw": json.dumps(sonar_scanner_result, ensure_ascii=False)[:20000],
    }


def _calc_vulnerability_disclosure(security_policy_result: Dict[str, Any]) -> Dict[str, Any]:
    file_size = int(security_policy_result.get("file_size") or 0)
    urls = security_policy_result.get("urls") or []
    emails = security_policy_result.get("emails") or []
    avg_close = security_policy_result.get("avg_vuln_close_days") or security_policy_result.get("avg_close_days")
    has_channel = file_size > 0 or bool(urls) or bool(emails)
    return {
        "vulnerability_disclosure_has_channel": has_channel,
        "security_md_exists": file_size > 0,
        "avg_vuln_close_days": avg_close,
        "vulnerability_disclosure_detail": json.dumps(
            {"file_size": file_size, "url_count": len(urls), "email_count": len(emails)}, ensure_ascii=False
        ),
    }


def _calc_dependency_reachable(dep_result: Dict[str, Any]) -> Dict[str, Any]:
    unreachable = dep_result.get("unreachable") or dep_result.get("unreachable_dependencies") or []
    if isinstance(unreachable, dict):
        unreachable = unreachable.get("list") or unreachable.get("items") or []
    if not isinstance(unreachable, list):
        unreachable = []
    return {
        "dependency_unreachable_list": unreachable,
        "dependency_reachable_ok": len(unreachable) == 0,
        "dependency_reachable_detail": json.dumps(
            {"unreachable_count": len(unreachable), "sample": unreachable[:20]}, ensure_ascii=False
        ),
    }


def _calc_patent_risk_oin(dep_or_oat: Dict[str, Any]) -> Dict[str, Any]:
    oin = dep_or_oat.get("oin_risk") or dep_or_oat.get("oin")
    if oin is None:
        return {"patent_risk_level": None, "patent_risk_unavailable": True, "patent_risk_detail": "{}"}
    return {
        "patent_risk_level": oin.get("level") or oin.get("risk"),
        "patent_risk_unavailable": False,
        "patent_risk_detail": json.dumps(oin, ensure_ascii=False)[:500],
    }


def _calc_lifecycle_statement(lifecycle_doc: Dict[str, Any]) -> Dict[str, Any]:
    has_eol = bool(lifecycle_doc.get("has_eol") or lifecycle_doc.get("eol_declared"))
    keywords_hit = lifecycle_doc.get("keywords_found") or []
    return {
        "lifecycle_statement": 10 if has_eol else (6 if keywords_hit else 0),
        "lifecycle_statement_exists": bool(has_eol or keywords_hit),
        "lifecycle_statement_detail": json.dumps(lifecycle_doc, ensure_ascii=False)[:500],
    }


def _calc_avg_vulnerability_fix_time(osv_or_platform: Dict[str, Any]) -> Dict[str, Any]:
    days = osv_or_platform.get("avg_vulnerability_fix_days") or osv_or_platform.get("avg_fix_days")
    if days is None:
        return {"avg_vulnerability_fix_days": None, "avg_vulnerability_fix_unavailable": True}
    return {"avg_vulnerability_fix_days": float(days), "avg_vulnerability_fix_unavailable": False}


def _extract_license_from_scancode(scancode_result: Dict[str, Any]) -> Optional[str]:
    for file in scancode_result.get("files") or []:
        if file.get("type") != "file":
            continue
        path = (file.get("path") or "").lower()
        parts = path.split("/")
        if not file.get("detected_license_expression"):
            continue
        if len(parts) >= 2 and parts[1] == "license":
            return file.get("detected_license_expression_spdx") or file.get("detected_license_expression")
    return None


def _oat_block_if_present(oat_full: Dict[str, Any], key: str) -> Optional[Dict[str, Any]]:
    if not oat_full or not _oat_ok(oat_full):
        return None
    v = oat_full.get(key)
    if not isinstance(v, dict) or not v:
        return None
    return v


def compliance_license(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    scancode = _fetch_command_result(client, opencheck_raw_index, repo_list, "scancode")
    readme_os = _fetch_command_result(client, opencheck_raw_index, repo_list, "readme-opensource-checker")
    oat_full = _fetch_command_result(client, opencheck_raw_index, repo_list, "oat-scanner")
    if not scancode:
        return {"compliance_license": -1, "detail": "no scancode data"}
    return _calc_compliance_license(scancode, readme_os, _oat_block_if_present(oat_full, "No Readme.OpenSource"))


def compliance_license_compatibility(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    scancode = _fetch_command_result(client, opencheck_raw_index, repo_list, "scancode")
    oat_full = _fetch_command_result(client, opencheck_raw_index, repo_list, "oat-scanner")
    return _calc_compliance_license_compatibility(scancode or {},
                                                  _oat_block_if_present(oat_full, "License Not Compatible"))


def compliance_copyright_statement(
        client: Any, opencheck_raw_index: str, repo_list: List[str], oh_commit_sha: Optional[str] = None
) -> Dict[str, Any]:
    scancode = _fetch_command_result(client, opencheck_raw_index, repo_list, "scancode")
    changed = _fetch_command_result(client, opencheck_raw_index, repo_list, "changed-files-since-commit-detector")
    oat_full = _fetch_command_result(client, opencheck_raw_index, repo_list, "oat-scanner")
    if not scancode:
        return {"compliance_copyright_statement": -1, "non_compliant_files": []}
    return _calc_compliance_copyright_statement(
        scancode, changed or {}, oh_commit_sha, _oat_block_if_present(oat_full, "Copyright Header Invalid")
    )


def compliance_copyright_anti_tamper(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    oat_full = _fetch_command_result(client, opencheck_raw_index, repo_list, "oat-scanner")
    return _calc_compliance_copyright_anti_tamper(oat_full or None)


def compliance_snippet_reference(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    oat_full = _fetch_command_result(client, opencheck_raw_index, repo_list, "oat-scanner")
    return _calc_compliance_snippet_reference(oat_full or None)


def import_valid(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    oat_full = _fetch_command_result(client, opencheck_raw_index, repo_list, "oat-scanner")
    return _calc_import_valid(_oat_block_if_present(oat_full, "Import Invalid"))


def security_binary_artifact(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    binary = _fetch_command_result(client, opencheck_raw_index, repo_list, "binary-checker")
    oat_full = _fetch_command_result(client, opencheck_raw_index, repo_list, "oat-scanner")
    if not binary:
        return {"security_binary_artifact": -1, "binary_violation_files": [], "detail": "no binary-checker data"}
    return _calc_security_binary_artifact(binary, _oat_block_if_present(oat_full, "Invalid File Type"))


def security_vulnerability(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    osv = _fetch_command_result(client, opencheck_raw_index, repo_list, "osv-scanner")
    if not osv:
        return {"security_vulnerability": -1, "vuln_counts": {}, "detail": "no osv-scanner data"}
    return _calc_security_vulnerability(osv)


def vulnerability_disclosure(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    sec = _fetch_command_result(client, opencheck_raw_index, repo_list, "security-policy-checker")
    return _calc_vulnerability_disclosure(sec or {})


def ecology_readme(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    readme = _fetch_command_result(client, opencheck_raw_index, repo_list, "readme-checker")
    oat_full = _fetch_command_result(client, opencheck_raw_index, repo_list, "oat-scanner")
    return _calc_ecology_readme(readme or {}, _oat_block_if_present(oat_full, "No Readme"))


def ecology_build_doc(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    return _calc_ecology_build_doc(
        _fetch_command_result(client, opencheck_raw_index, repo_list, "build-doc-checker") or {})


def ecology_interface_doc(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    return _calc_ecology_interface_doc(
        _fetch_command_result(client, opencheck_raw_index, repo_list, "api-doc-checker") or {})


def ecology_maintainer_doc(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    return _calc_ecology_maintainer_doc(
        _fetch_command_result(client, opencheck_raw_index, repo_list, "maintainers-checker") or {})


def dependency_reachable(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    dep = _fetch_command_result(client, opencheck_raw_index, repo_list, "dependency-reachable-checker")
    if not dep:
        return {
            "dependency_reachable_ok": None,
            "dependency_unreachable_list": [],
            "detail": "no dependency-reachable-checker data",
        }
    return _calc_dependency_reachable(dep)


def patent_risk_oin(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    dep = _fetch_command_result(client, opencheck_raw_index, repo_list, "dependency-reachable-checker")
    return _calc_patent_risk_oin(dep or {})


def ecology_test_coverage(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    sonar = _fetch_command_result(client, opencheck_raw_index, repo_list, "sonar-scanner")
    if not sonar:
        return {"ecology_test_coverage": -1, "test_coverage_percent": None, "detail": "no sonar-scanner data"}
    return _calc_ecology_test_coverage(sonar)


def trusted_build_success(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    b = _fetch_command_result(client, opencheck_raw_index, repo_list, "build-checker")
    rate = b.get("build_success_rate") if b else None
    if rate is None and b:
        rate = b.get("success_rate")
    return {"ecology_build_success_rate": rate, "build_checker_present": bool(b)}


def ci_integration(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    ci = _fetch_command_result(client, opencheck_raw_index, repo_list, "ci-checker")
    on = bool(ci.get("ci_enabled") or ci.get("workflows") or ci.get("ci_config_present")) if ci else False
    return {"ecology_ci": 10 if on else 0, "ci_integration": on}


def build_metadata_available(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    for cmd in ("build-metadata-checker", "artifact-metadata-checker"):
        m = _fetch_command_result(client, opencheck_raw_index, repo_list, cmd)
        if m:
            ok = bool(m.get("metadata_available") or m.get("artifact_metadata"))
            return {"build_metadata_available": ok, "command": cmd}
    return {"build_metadata_available": None, "detail": "no metadata checker data"}


def reproducible_build(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    r = _fetch_command_result(client, opencheck_raw_index, repo_list, "reproducible-build-checker")
    repro = r.get("reproducible") if r else None
    if repro is None and r:
        repro = r.get("checksum_match")
    return {"reproducible_build": bool(repro) if repro is not None else None}


def sbom_in_release(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    rel = _fetch_command_result(client, opencheck_raw_index, repo_list, "release-checker")
    if not rel:
        return {"sbom_in_release": None, "detail": "no release-checker data"}
    return _calc_sbom_in_release(rel)


def security_package_sig(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    rel = _fetch_command_result(client, opencheck_raw_index, repo_list, "release-checker")
    if not rel:
        return {"security_package_sig": -1}
    return _calc_security_package_sig(rel)


def lifecycle_release_note(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    rel = _fetch_command_result(client, opencheck_raw_index, repo_list, "release-checker")
    if not rel:
        return {"lifecycle_release_note": -1}
    return _calc_lifecycle_release_note(rel)


def lifecycle_statement(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    return _calc_lifecycle_statement(
        _fetch_command_result(client, opencheck_raw_index, repo_list, "lifecycle-doc-checker") or {})


def avg_vulnerability_fix_time(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    osv = _fetch_command_result(client, opencheck_raw_index, repo_list, "osv-scanner")
    r = _calc_avg_vulnerability_fix_time(osv or {})
    if r.get("avg_vulnerability_fix_unavailable"):
        sec = _fetch_command_result(client, opencheck_raw_index, repo_list, "security-policy-checker")
        r2 = _calc_avg_vulnerability_fix_time(sec or {})
        if not r2.get("avg_vulnerability_fix_unavailable"):
            return r2
    return r


def declared_license(client: Any, opencheck_raw_index: str, repo_list: List[str]) -> Dict[str, Any]:
    scancode = _fetch_command_result(client, opencheck_raw_index, repo_list, "scancode")
    return {"declared_license": _extract_license_from_scancode(scancode) if scancode else None}
