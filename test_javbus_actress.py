#!/usr/bin/env python3
"""
测试脚本：分析JAVBus演员页面HTML结构
用于扩展javbus.py以支持演员页面解析
"""

import asyncio
import aiohttp
from lxml import etree

# 基于javbus.py的现有模式，推测演员页面可能的结构
# JAVBus演员详情页URL格式: /actresses/{actor_id}
# 演员作品列表可能有分页

# 从missing.py的JAVDB实现中看到的XPath模式：
# //a[@class="box"] - 视频框容器
# div[@class="video-title"]/strong/text() - 番号
# div[@class="video-title"]/text() - 标题
# div[@class="meta"]/text() - 日期

# JAVBus番号页面的XPath模式（来自javbus.py）：
# //h3/text() - 标题
# //span[@class="header"][contains(text(), "識別碼:")]/../span[2]/text() - 番号
# //div[@class="star-name"]/a/text() - 演员
# //a[@class="bigImage"]/@href - 封面

# 推测JAVBus演员页面可能使用的XPath：
# 1. 演员列表页 (/actresses):
#    - 演员卡片：可能使用 //div[@class="actress-item"] 或类似的容器
#    - 演员姓名：可能包含在链接或特定标签中
#    - 演员封面：可能是img标签的src属性

# 2. 演员详情页 (/actresses/{id}):
#    - 作品列表：可能使用类似 //a[@class="movie-box"]（搜索结果页使用）
#    - 番号：可能使用 //div[@class="photo-info"]/span/text() 或其他模式
#    - 标题：可能包含在h3或其他标签中
#    - 日期：可能使用 //div[@class="info"]/p/date/text() 或类似

async def test_javbus_actress_page():
    """测试JAVBus演员页面解析"""
    
    # 注意：实际使用时需要绕过年龄验证
    base_url = "https://www.dmmsee.cyou"  # 镜像站点
    actress_list_url = f"{base_url}/actresses"
    actress_detail_url = f"{base_url}/actresses/1"  # 示例演员ID
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    # 测试用的XPath表达式
    test_xpaths = {
        "actor_list": [
            "//a[@class='actress-item']",  # 演员卡片链接
            "//div[@class='actress-box']",  # 演员卡片容器
            "//div[@class='photo-frame']",  # 照片框架
            "//div[contains(@class, 'actress')]/a",  # 通用演员链接
        ],
        "actor_name": [
            ".//div[@class='actress-name']/text()",  # 演员姓名
            ".//div[@class='name']/text()",  # 姓名标签
            ".//h3/text()",  # h3标题
            ".//span[@class='name']/text()",  # 姓名span
        ],
        "video_list": [
            "//a[@class='movie-box']",  # 视频框（来自搜索页）
            "//div[@class='photo-info']/a",  # 照片信息链接
            "//div[@class='item-box']/a",  # 项目框
            "//a[contains(@href, '/') and contains(., '日期')]",  # 包含日期的链接
        ],
        "video_number": [
            ".//div[@class='photo-info']/span/text()",  # 照片信息中的span
            ".//date/text()",  # 日期标签
            ".//span[@class='date']/text()",  # 日期span
            ".//div[contains(@class, 'info')]//text()",  # 信息区文本
        ],
    }
    
    print("JAVBus演员页面XPath测试脚本")
    print("=" * 60)
    print("\n待测试的XPath表达式：")
    print(f"演员列表页URL: {actress_list_url}")
    print(f"演员详情页URL: {actress_detail_url}")
    print("\n测试XPath模式：")
    for category, xpath_list in test_xpaths.items():
        print(f"\n{category}:")
        for xpath in xpath_list:
            print(f"  - {xpath}")
    
    print("\n" + "=" * 60)
    print("\n建议的实现步骤：")
    print("1. 访问演员页面并获取HTML")
    print("2. 使用上述XPath表达式测试解析")
    print("3. 确定正确的XPath规则")
    print("4. 在javbus.py中添加演员页面解析函数")
    print("5. 修改missing.py以使用JAVBus而非JAVDB")
    
    return test_xpaths

if __name__ == "__main__":
    # 运行测试准备
    xpaths = asyncio.run(test_javbus_actress_page())
    print("\n测试脚本完成！")
    print("注意：由于年龄验证，实际测试需要在浏览器中手动完成")