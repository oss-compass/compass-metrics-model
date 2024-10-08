import requests
import json
import requests
from bs4 import BeautifulSoup
# /html/body/div/div[1]/div/div/div/div/table
url = "https://deps.dev/pypi/torch/2.4.0/dependents"

import requests
from lxml import etree
https://deps.dev/_/s/pypi/p/accelerate/v/0.34.0/dependents
# Step 1: 发送 HTTP 请求获取网页内容
url = 'https://deps.dev/pypi/torch/2.4.0/dependents'  # 替换为你要爬取的实际网址
import requests
from lxml import html

# Step 1: 发送 HTTP 请求获取网页内容
#url = 'https://example.com'  # 将此替换为你要爬取的实际网址
response = requests.get(url)

# 检查请求是否成功
if response.status_code == 200:
    # Step 2: 使用 lxml 解析 HTML
    tree = html.fromstring(response.content)

    # Step 3: 使用 XPath 查找特定的链接元素
    link_element = tree.xpath('/html/body/div/div[1]/div/div/div/div/table/tbody/tr[1]/td[1]/a')

    # 检查是否找到链接
    if link_element:
        link_text = link_element[0].text_content().strip()  # 获取链接文本内容
        link_href = link_element[0].get('href')  # 获取链接的 href 属性值
        print(f"Link Text: {link_text}")
        print(f"Link Href: {link_href}")
    else:
        print("No link found with the given XPath.")
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
