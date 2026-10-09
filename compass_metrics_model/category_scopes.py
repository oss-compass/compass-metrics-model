"""读取「项目分类」的成员名单，供汇总层按分类统计使用。

数据来源
--------
上游 ``compass-projects-information`` 仓库：

- ``collections.yml``          一级领域（27 个），其 ``items`` 是二级分类的 ident
- ``collections/<ident>.yml``  二级分类（341 个），其 ``items`` 是项目 URL 列表

汇总层需要的是后者：``ident -> [url, ...]``，用于查询里的 ``terms`` 过滤。
上游 ``compass-web`` 的 ``apps/web/script/gen_collections_file.ts`` 读的是同一份
数据（它产出前端菜单用的 ``collections.json``），本模块与它同源同构。

为什么不由本层自己去 clone 上游仓库：那会把网络与仓库路径变成汇总层的隐含依赖。
本模块只认一个目录，由入口层从配置传入。
"""
import hashlib
import logging
import subprocess
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


class CategoryScopesError(ValueError):
    """分类名单的读取或格式有问题——必须让人看到，不得静默跳过。"""


def normalize_url(url):
    """把名单里的 URL 归一成与指标文档 ``label`` 相同的形态。

    为什么必须归一化（实测，全量 44,548 个原始条目）
    ----------------------------------------------
    1. **协议**：名单里有 **145 个 ``http://`` 条目**（全部集中在 ``rust-picks``），
       而指标文档的 ``label`` 用 https——上游示例输入（``projects-github-pytorch.json``、
       ``projects-gitee-mindspore.json``）**全部是 https**，且
       ``compass_model/base_metrics_model.py:416`` 把 ``label`` **原样写入**、
       不做任何归一化。不改协议的话这 145 个项目**永远匹配不上** ``terms`` 过滤。
    2. **尾斜杠**：10 个条目以 ``/`` 结尾（如 ``https://github.com/Khan/tota11y/``），
       同样匹配不上。
    3. **去重**：``other-network-communication-sw`` 里 ``FRRouting/frr`` 出现两次；
       ``information-accessibility`` 里 ``Khan/tota11y`` 同时有带斜杠与不带斜杠两种写法。
       归一化后重复的条目由调用方去重。

    这三条都推翻了我更早写在 ``category-data-access-conclusion-v1.0.md`` 里的
    「与名单格式一致，不需要归一化」——那句话的依据是**单个示例文件**，
    不是全量语料。
    """
    url = str(url).strip().rstrip("/")
    if url.startswith("http://"):
        url = "https://" + url[len("http://"):]
    return url


def load_category_scopes(collections_dir):
    """读 ``collections/*.yml``，返回有序的 ``{ident: [url, ...]}``。

    只处理 ``*.yml``；其余文件跳过（上游 ``collections/`` 下有一个 ``list.md``）。
    ``*.yml`` 里缺 ``ident``、缺 ``items``、或 ``items`` 不是列表时**抛错**：
    静默跳过等于少统计一个分类且不留痕迹。

    每个分类的 URL 会被归一化（``normalize_url``）并去重，保持原有顺序。
    """
    directory = Path(collections_dir)
    if not directory.is_dir():
        raise CategoryScopesError("分类名单目录不存在：%s" % directory)

    scopes = {}
    for path in sorted(directory.glob("*.yml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise CategoryScopesError("分类文件无法解析：%s（%s）" % (path.name, exc))
        if not isinstance(data, dict):
            raise CategoryScopesError("分类文件内容不是映射：%s" % path.name)
        ident = data.get("ident")
        items = data.get("items")
        if not ident or not isinstance(ident, str):
            raise CategoryScopesError("分类文件缺少合法的 ident：%s" % path.name)
        if not isinstance(items, list):
            raise CategoryScopesError("分类文件的 items 不是列表：%s" % path.name)
        if ident in scopes:
            raise CategoryScopesError("分类 ident 重复：%s（%s）" % (ident, path.name))

        urls, seen = [], set()
        for raw in items:
            if not isinstance(raw, str):
                raise CategoryScopesError(
                    "分类的 items 里有非字符串项：%s（%r）" % (path.name, raw))
            url = normalize_url(raw)
            if not url:
                raise CategoryScopesError("分类的 items 里有空项：%s" % path.name)
            if url in seen:
                continue
            seen.add(url)
            urls.append(url)
        scopes[ident] = urls

    if not scopes:
        raise CategoryScopesError("分类名单目录里没有任何 *.yml：%s" % directory)
    logger.info("已读取分类名单 %d 个分类（来自 %s）", len(scopes), directory)
    return scopes


def load_category_scopes_from_config(params):
    """从入口配置里取目录并读取；未配置时返回 ``None``。

    返回 ``None`` 表示「不请求分类统计」，汇总层据此退化为原有的全局行为
    （一天一条、不写 ``category`` 字段）——对应验收条目 A01
    「原有全局请求保持兼容」。
    """
    directory = (params or {}).get("collections_dir")
    if not directory:
        return None
    return load_category_scopes(directory)


def membership_digest(scopes):
    """名单内容的确定性摘要。

    提交哈希记的是「哪一版**仓库**」，本摘要记的是「哪一份**名单**」。
    名单可能来自带未提交改动的工作副本，目录也可能不是 git 仓库；
    两种情况都取不到提交哈希，但只要有摘要，基准与它依据的名单就能对上号。

    口径：按 ident 排序，每行为 ``<ident>\\t<url1>,<url2>,...``，UTF-8 后取 sha256。
    排序使结果与文件遍历顺序无关。
    """
    lines = []
    for ident in sorted(scopes):
        lines.append("%s\t%s" % (ident, ",".join(scopes[ident])))
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def collections_source_commit(collections_dir):
    """名单来源仓库的提交哈希；取不到时返回 ``None``。

    取不到**不抛错**：版本号缺失不应阻断统计。但返回 ``None`` 这件事会被写进
    文档元数据的判断里，不会被当成「有版本」。
    """
    try:
        proc = subprocess.run(
            ["git", "-C", str(collections_dir), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    commit = proc.stdout.strip()
    return commit or None


def load_category_inputs_from_config(params):
    """一次取回分类名单与它的两个来源标识。

    返回 ``(scopes, source_commit, source_digest)``；未配置 ``collections_dir`` 时
    三者都是 ``None``，汇总层据此退化为原有全局行为（对应验收条目 A01）。
    """
    scopes = load_category_scopes_from_config(params)
    if scopes is None:
        return None, None, None
    directory = (params or {}).get("collections_dir")
    return scopes, collections_source_commit(directory), membership_digest(scopes)
