#!/usr/bin/env python3
"""
JAVBus演员页面解析功能扩展
在javbus.py中添加演员页面解析函数
"""

from lxml import etree
from typing import Optional, List


def get_actress_video_list(html: etree._Element, base_url: str) -> dict:
    """
    从JAVBus演员详情页解析作品列表

    Args:
        html: 已解析的HTML元素
        base_url: JAVBus基础URL

    Returns:
        包含视频信息的字典，格式为：
        {
            "videos": [
                {
                    "number": "番号",
                    "title": "标题", 
                    "date": "发行日期",
                    "url": "详情页URL"
                },
                ...
            ],
            "has_next": True/False
        }
    """
    result = {
        "videos": [],
        "has_next": False
    }
    
    # 基于JAVBus搜索页面的模式，推测演员详情页可能使用类似结构
    # 可能的XPath模式（按优先级排序）
    video_xpath_patterns = [
        # 模式1：类似搜索结果页的movie-box
        "//a[@class='movie-box']",
        # 模式2：演员详情页特有的容器
        "//div[@class='photo-frame']/a",
        # 模式3：通用视频框
        "//div[contains(@class, 'item-box')]/a",
        # 模式4：参考JAVDB的box类
        "//a[@class='box']",
    ]
    
    videos = []
    for pattern in video_xpath_patterns:
        video_elements = html.xpath(pattern)
        if video_elements:
            videos = video_elements
            break
    
    if not videos:
        return result
    
    for video in videos:
        try:
            # 尝试多种XPath模式提取视频信息
            video_data = _extract_video_info(video, base_url)
            if video_data and video_data.get("number"):
                result["videos"].append(video_data)
        except Exception:
            # 单个视频解析失败不影响其他视频
            continue
    
    # 检查是否有下一页
    next_page = html.xpath("//a[@class='next' or contains(text(), '下一页')]")
    result["has_next"] = len(next_page) > 0
    
    return result


def _extract_video_info(video: etree._Element, base_url: str) -> Optional[dict]:
    """
    从单个视频元素中提取信息

    Args:
        video: 视频元素
        base_url: 基础URL

    Returns:
        视频信息字典或None
    """
    # 获取视频URL
    href = video.get("href", "")
    if not href:
        return None
    
    # 补全URL
    if not href.startswith("http"):
        url = base_url + href if href.startswith("/") else base_url + "/" + href
    else:
        url = href
    
    # 尝试多种模式提取番号
    number = None
    number_patterns = [
        ".//div[@class='photo-info']/span/text()",
        ".//date/text()",
        ".//span[@class='date']/text()",
        ".//div[contains(@class, 'video-number')]/text()",
        ".//h3/text()",  # 有时番号在标题中
    ]
    
    for pattern in number_patterns:
        number_elements = video.xpath(pattern)
        if number_elements:
            number = str(number_elements[0]).strip()
            if number:
                break
    
    if not number:
        # 尝试从URL中提取番号
        import re
        number_match = re.search(r'/([A-Z]{2,6}-?\d{3,})', url, re.IGNORECASE)
        if number_match:
            number = number_match.group(1).replace("-", "")
    
    # 尝试提取标题
    title = ""
    title_patterns = [
        ".//div[@class='photo-info']/text()",
        ".//h3/text()",
        ".//div[contains(@class, 'title')]/text()",
        ".//span[@class='title']/text()",
    ]
    
    for pattern in title_patterns:
        title_elements = video.xpath(pattern)
        if title_elements:
            title = str(title_elements[0]).strip()
            if title:
                break
    
    # 尝试提取日期
    date = ""
    date_patterns = [
        ".//div[@class='info']/date/text()",
        ".//span[@class='date']/text()",
        ".//div[contains(@class, 'meta')]/text()",
    ]
    
    for pattern in date_patterns:
        date_elements = video.xpath(pattern)
        if date_elements:
            date = str(date_elements[0]).strip()
            if date:
                break
    
    return {
        "number": number,
        "title": title,
        "date": date,
        "url": url
    }


def get_actress_list(html: etree._Element, base_url: str) -> List[dict]:
    """
    从JAVBus演员列表页解析演员信息

    Args:
        html: 已解析的HTML元素
        base_url: JAVBus基础URL

    Returns:
        演员信息列表，格式为：
        [
            {
                "name": "演员姓名",
                "url": "演员详情页URL",
                "id": "演员ID"
            },
            ...
        ]
    """
    actresses = []
    
    # 尝试多种XPath模式提取演员列表
    actress_patterns = [
        "//a[@class='actress-item']",
        "//div[@class='actress-box']/a", 
        "//div[contains(@class, 'actress')]/a",
        "//div[@class='photo-frame']/a",
    ]
    
    actress_elements = []
    for pattern in actress_patterns:
        elements = html.xpath(pattern)
        if elements:
            actress_elements = elements
            break
    
    for actress in actress_elements:
        try:
            href = actress.get("href", "")
            if not href:
                continue
            
            # 补全URL
            if not href.startswith("http"):
                url = base_url + href if href.startswith("/") else base_url + "/" + href
            else:
                url = href
            
            # 提取演员ID
            import re
            id_match = re.search(r'/actresses/(\d+)', url)
            actor_id = id_match.group(1) if id_match else ""
            
            # 提取演员姓名
            name_patterns = [
                ".//div[@class='actress-name']/text()",
                ".//div[@class='name']/text()",
                ".//h3/text()",
                ".//span[@class='name']/text()",
                ".//text()",  # 最后尝试所有文本
            ]
            
            name = ""
            for pattern in name_patterns:
                name_elements = actress.xpath(pattern)
                if name_elements:
                    name = str(name_elements[0]).strip()
                    if name:
                        break
            
            if name and actor_id:
                actresses.append({
                    "name": name,
                    "url": url,
                    "id": actor_id
                })
        except Exception:
            continue
    
    return actresses


# 示例使用函数
def example_usage():
    """示例代码，展示如何使用这些函数"""
    print("JAVBus演员页面解析功能扩展")
    print("=" * 50)
    print("\n函数列表：")
    print("1. get_actress_video_list(html, base_url)")
    print("   - 从演员详情页解析作品列表")
    print("   - 返回视频信息和分页状态")
    print("\n2. get_actress_list(html, base_url)")  
    print("   - 从演员列表页解析演员信息")
    print("   - 返回演员姓名、URL和ID")
    print("\n3. _extract_video_info(video, base_url)")
    print("   - 从单个视频元素提取信息")
    print("   - 返回番号、标题、日期和URL")
    
    print("\n" + "=" * 50)
    print("集成到javbus.py的步骤：")
    print("1. 将这些函数添加到javbus.py文件中")
    print("2. 在JavbusCrawler类中添加演员页面解析方法")
    print("3. 修改missing.py以使用JAVBus而非JAVDB")
    print("4. 更新文档说明")

if __name__ == "__main__":
    example_usage()