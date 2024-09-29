'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2024-09-04 08:46:31
LastEditors: zyx
LastEditTime: 2024-09-19 03:28:48
'''
import requests
import json
from datetime import datetime
def bug_issue(repo_url,beginDate,endDate):
    # 定义接口地址
    url = "https://compass.gitee.com/api/graphql"

    # 定义 GraphQL 查询
    query = f"""
        query {{
             metricCommunity(
                label: "{repo_url.replace(".git","")}"
                level: "repo"
                beginDate: "{beginDate}"
                endDate: "{endDate}"
                repoType: ""
            ) {{
                grimoireCreationDate 
                bugIssueOpenTimeAvg 
            }}
        }}
        """
    # 定义请求头
    headers = {
        "Content-Type": "application/json",
    }
    #print(query)

    # 发送请求
    response = requests.post(
        url,
        headers=headers,
        data=json.dumps({"query": query})
    )

    # 解析响应
    if response.status_code == 200:
        data = response.json()
        if len(data['data']['metricCommunity']) != 0 and data['data']['metricCommunity'][-1]["bugIssueOpenTimeAvg"]!=None:
            return data['data']['metricCommunity'][-1]["bugIssueOpenTimeAvg"]
        else:
            return 600

        # return json.dumps(data, indent=2, ensure_ascii=False)
    else:
        print(f"请求失败，状态码: {response.status_code}")
        return None

if __name__=="__main__":
    bug_issue("https://github.com/pytorch/pytorch")
    # from datetime import datetime, timezone

    # # 获取当前 UTC 时间
    # current_time = datetime.now(timezone.utc)

    # # 转换为 ISO 8601 格式
    # iso_time_str = current_time.isoformat(timespec='milliseconds').replace('+00:00', 'Z')

    # # 输出时间字符串
    # print(iso_time_str)  # 例如：2023-08-28T13:45:23.123Z
