import requests
from bs4 import BeautifulSoup
import datetime
import time
import random
import json
import os
import hashlib

# ==================== 配置区域（你需要修改的部分）====================
# 你的PushPlus token（替换成第一步复制的token）
PUSHPLUS_TOKEN = "78fad57be30f455c9b53d8d4b7c905d0"

# 要监控的关键词列表
KEYWORDS = ["采购管理", "内控管理", "招标采购管理", "智慧实验室", "智慧教室"]

# 要监控的政府采购网站列表（你可以自己添加或修改）
# 格式：[网站名称, 网址]
WEBSITES = [
    ["中国政府采购网", "http://www.ccgp.gov.cn"],
    # 添加更多省份的政府采购网（示例）
    # ["北京市政府采购网", "http://www.ccgp-beijing.gov.cn"],
    # ["上海市政府采购网", "http://www.ccgp-shanghai.gov.cn"],
    # ["广东省政府采购网", "http://www.ccgp-guangdong.gov.cn"],
]
# ==================== 配置结束 ====================


def send_to_wechat(content):
    """通过PushPlus推送消息到微信"""
    url = "http://www.pushplus.plus/send"
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": f"政府采购意向监控 {today}",
        "content": content
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        print(f"推送结果: {response.text}")
    except Exception as e:
        print(f"推送失败: {e}")


def search_website(website_name, website_url):
    """搜索单个网站（这是一个示例函数，你需要根据实际网站结构调整）"""
    results = []
    
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"正在搜索: {website_name}")
        
        # 这里需要根据实际网站结构编写爬取逻辑
        # 下面是一个示例，假设网站有一个公告列表页
        search_url = f"{website_url}/cggg/dfgg/"
        
        # 发送请求
        response = requests.get(search_url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 示例：假设公告列表在class为"notice-list"的ul里
            # 你需要根据实际网站的HTML结构调整这里的选择器
            notice_items = soup.select('.notice-list li')  # 这行需要修改
            
            for item in notice_items[:10]:  # 只取前10条最新公告
                # 提取标题和链接
                link_tag = item.find('a')
                if not link_tag:
                    continue
                    
                title = link_tag.get_text(strip=True)
                href = link_tag.get('href')
                
                # 拼接完整链接
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = website_url + href if website_url.endswith('/') else website_url + '/' + href
                
                # 提取发布日期
                date_tag = item.find('span', class_='date')
                date = date_tag.get_text(strip=True) if date_tag else datetime.date.today().strftime("%Y-%m-%d")
                
                # 检查标题是否包含关键词
                matched_keywords = []
                for kw in KEYWORDS:
                    if kw in title:
                        matched_keywords.append(kw)
                
                # 如果匹配到关键词，保存结果
                if matched_keywords:
                    results.append({
                        "website": website_name,
                        "date": date,
                        "title": title,
                        "url": full_url,
                        "keywords": "、".join(matched_keywords)
                    })
        
        # 随机延时，避免请求过于频繁
        time.sleep(random.uniform(1, 3))
        
    except Exception as e:
        print(f"搜索{website_name}时出错: {e}")
    
    return results


def main():
    """主函数"""
    print(f"开始监控政府采购意向 - {datetime.datetime.now()}")
    
    all_results = []
    
    # 遍历所有网站
    for website_name, website_url in WEBSITES:
        results = search_website(website_name, website_url)
        all_results.extend(results)
    
    # 生成推送内容
    if not all_results:
        content = f"今日无新增相关采购意向（{datetime.date.today().strftime('%Y-%m-%d')}）"
    else:
        content = f"今日发现 {len(all_results)} 条相关采购意向：\n\n"
        for item in all_results:
            content += f"【{item['website']}】\n"
            content += f"发布日期：{item['date']}\n"
            content += f"项目名称：{item['title']}\n"
            content += f"匹配关键词：{item['keywords']}\n"
            content += f"原文链接：{item['url']}\n"
            content += "-" * 40 + "\n"
    
    # 推送消息
    send_to_wechat(content)
    print("监控完成")


if __name__ == "__main__":
    main()