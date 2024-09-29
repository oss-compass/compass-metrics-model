'''
Descripttion: software universality
version: 
Author: zyx
Date: 2024-08-17 16:39:45
LastEditors: zyx
LastEditTime: 2024-08-18 16:11:41
'''

import requests
import json

def Get_software_universality():
    url = r"https://ohpm.openharmony.cn/ohpmweb/registry/oh-package/openapi/v1/detail/@pura/harmony-utils"
    request = requests.get(url)
    content = json.loads(request.content)['body']
    downloads_all = content["downloads"]
    downloads_60 = content["popularity"] # 过去六十天的下载量
    likes = content["likes"] # 点赞数
    dependencies = content["dependencies"]["total"] # 依赖数
    versions = content["versions"] # 版本更新时间

    return dependencies
    

import requests
from datetime import datetime
from pkg_resources import parse_version
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 获取包的版本历史
def get_pypi_versions(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    data = response.json()
    releases = data.get("releases", {})
    return releases

# 规范化日期字符串
def normalize_isoformat(date_str):
    if len(date_str.split("T")[-1].split(":")[-1]) == 1:
        date_str += "0"
    return date_str

# 获取指定版本的依赖项数量
def get_dependencies(package_name, version):
    try:
        dist = pkg_resources.get_distribution(f"{package_name}=={version}")
        dependencies = dist.requires()
        return len(dependencies)
    except Exception as e:
        print(f"Failed to get dependencies for {package_name}=={version}: {e}")
        return None

# 主程序
def main(package_name):
    releases = get_pypi_versions(package_name)
    version_dates = []
    dependency_counts = []

    for version, release_info in sorted(releases.items(), key=lambda x: parse_version(x[0])):
        if release_info:
            release_date_str = release_info[0]['upload_time']
            normalized_date_str = normalize_isoformat(release_date_str)
            release_date = datetime.fromisoformat(normalized_date_str[:-1])
            version_dates.append(release_date)

            num_dependencies = get_dependencies(package_name, version)
            if num_dependencies is not None:
                dependency_counts.append(num_dependencies)
            else:
                dependency_counts.append(0)

    # 绘制折线图
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(version_dates, dependency_counts, marker='o', linestyle='-', color='b')
    ax.set_xlabel("Release Date")
    ax.set_ylabel("Dependency Count")
    ax.set_title(f"Dependency Count over Time for {package_name}")

    # 设置日期格式和间隔
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))

    # 设置横轴范围和标签
    ax.set_xlim([datetime(2023, 3, 1), datetime(2024, 9, 30)])
    fig.autofmt_xdate()

    plt.show()

# 执行主程序
if __name__ == "__main__":
    package_name = "requests"  # 替换为你要分析的包名
    main(package_name)

    



if __name__=="__main__":
    Get_software_universality()