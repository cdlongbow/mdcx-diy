"""
测试 graphis.ne.jp 网站当前结构，验证代码中的 XPath 选择器是否仍然有效。

使用方式:
    python test_graphis_structure.py  # 默认测试一位已知女优
    python test_graphis_structure.py 梦乃爱华  # 测试指定女优
    python test_graphis_structure.py --names "梦乃爱华,苍井空,上原亚衣"  # 批量测试

输出说明:
    会打印出实际请求到的 HTML 中:
    - //div[@class='gp-model-box'] 的匹配结果
    - //div[contains(@class,'model')] 等常见 class 的匹配结果
    - //li[@class='name-jp'] 的匹配结果
    - 页面上所有的 img @src 前几个
    - 页面上所有的 li 的 class 属性
    以便判断网站结构是否发生了改变。
"""

import asyncio
import sys
from urllib.parse import quote

import httpx
from lxml import etree
from parsel import Selector

# 代码中的原始 XPath 选择器
ORIG_AV_SRC_XPATH = "//div[@class='gp-model-box']/ul/li/a/img/@src"
ORIG_NAME_XPATH = "//li[@class='name-jp']/span/text()"


def analyze_html(html: str, url: str, logs: list[str]):
    """分析 HTML 并输出诊断信息"""
    logs.append(f"\n{'=' * 70}")
    logs.append(f"URL: {url}")
    logs.append(f"HTML 长度: {len(html)} 字符")
    logs.append("")

    sel = Selector(text=html)
    tree = etree.HTML(html.encode("utf-8", errors="replace"))

    # 1. 原始选择器匹配情况
    orig_av = sel.xpath(ORIG_AV_SRC_XPATH).getall()
    orig_names = sel.xpath(ORIG_NAME_XPATH).getall()
    logs.append(f"【原始选择器 //div[@class='gp-model-box']/ul/li/a/img/@src】匹配 {len(orig_av)} 个结果:")
    for i, src in enumerate(orig_av[:10]):
        logs.append(f"  [{i}] {src}")

    logs.append(f"\n【原始选择器 //li[@class='name-jp']/span/text()】匹配 {len(orig_names)} 个结果:")
    for i, name in enumerate(orig_names[:10]):
        logs.append(f"  [{i}] {repr(name)}")

    # 2. 寻找 gp-model-box 相关 class
    logs.append("\n【所有包含 'model' 的 div 标签及 class 属性】:")
    model_divs = tree.xpath("//div[contains(@class, 'model')]")
    for i, d in enumerate(model_divs[:20]):
        cls = d.get("class", "")
        logs.append(f"  [{i}] class='{cls}'")
        imgs = d.xpath(".//img/@src")
        if imgs:
            for j, img in enumerate(imgs[:3]):
                logs.append(f"       img[{j}]: {img}")

    # 3. 寻找 name-jp 相关
    logs.append("\n【所有包含 'name-jp' 的元素及 class 属性】:")
    name_jp = tree.xpath("//*[contains(@class, 'name-jp')]")
    for i, el in enumerate(name_jp[:10]):
        cls = el.get("class", "")
        tag = el.tag
        text = (etree.tostring(el, encoding="unicode", method="text") or "").strip()[:100]
        logs.append(f"  [{i}] <{tag}> class='{cls}' text='{text}'")
        children = el.xpath(".//*[@class]")
        if children:
            for c in children[:3]:
                logs.append(f"       child: <{c.tag}> class='{c.get('class', '')}'")

    # 4. 列出所有 li 的 class
    logs.append("\n【所有 li 标签的 class 属性（去重）】:")
    li_classes = set()
    for li in tree.xpath("//li"):
        c = li.get("class", "")
        if c:
            li_classes.add(c)
    for c in sorted(li_classes)[:30]:
        logs.append(f"  '{c}'")

    # 5. 列出所有 img 标签的 src 前 20 个
    logs.append("\n【前 20 个 img @src】:")
    imgs = tree.xpath("//img/@src")
    for i, src in enumerate(imgs[:20]):
        logs.append(f"  [{i}] {src}")

    # 6. 页面标题和 meta
    logs.append("\n【页面标题】:")
    title = tree.xpath("//title/text()")
    logs.append(f"  {title[0] if title else '(无)'}")

    # 7. HTTP 状态码
    logs.append("\n【HTTP 响应状态码】:")
    logs.append("  (需要结合实际请求结果判断)")

    # 8. HTML 片段预览（前 3000 字符）
    logs.append("\n【HTML 前 3000 字符预览】:")
    logs.append(f"  {html[:3000]}")

    return orig_av, orig_names


async def test_actor(actor_name: str, version: str = "old"):
    """测试单个演员"""
    logs = []
    encoded_name = quote(actor_name, safe="")

    if version == "new":
        url = f"https://graphis.ne.jp/monthly/?K={encoded_name}"
    else:
        url = f"https://graphis.ne.jp/monthly/?S=1&K={encoded_name}"

    logs.append(f"\n{'#' * 70}")
    logs.append(f"# 测试演员: {actor_name} (版本: {version})")
    logs.append(f"# URL: {url}")
    logs.append("")

    orig_av = []
    orig_names = []
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "ja,zh-CN;q=0.9,zh;q=0.8,en;q=0.7",
                },
            )
            status = resp.status_code
            logs.append(f"HTTP 状态码: {status}")
            if status != 200:
                logs.append(f"响应内容: {resp.text[:500]}")
                logs.append(f"无法继续分析，HTTP {status}")
                return orig_av, orig_names, False

            html = resp.text
            orig_av, orig_names = analyze_html(html, url, logs)

            # 判断匹配结果
            if orig_av or orig_names:
                logs.append("\n结论: 网站结构【未】改变，XPath 选择器可能仍然有效")
                return orig_av, orig_names, True
            else:
                logs.append("\n结论: 网站结构【可能】已改变，XPath 选择器未匹配到任何内容")
                return orig_av, orig_names, False

    except httpx.HTTPError as e:
        logs.append(f"请求失败: {e}")
        return [], [], False
    except Exception as e:
        logs.append(f"异常: {e}")
        return [], [], False


async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--names":
        names = [n.strip() for n in sys.argv[2].split(",") if n.strip()]
        for name in names:
            for ver in ["old", "new"]:
                await test_actor(name, version=ver)
    else:
        name = sys.argv[1] if len(sys.argv) > 1 else "梦乃爱华"
        for ver in ["old", "new"]:
            await test_actor(name, version=ver)

    # 最后打印所有日志
    pass


# 需要改写: 把 logs 收集到全局
_all_logs: list[str] = []


async def test_actor_with_logs(actor_name: str, version: str = "old"):
    logs = []
    logs.append(f"\n{'#' * 70}")
    logs.append(f"# 测试演员: {actor_name} (版本: {version})")
    encoded_name = quote(actor_name, safe="")

    if version == "new":
        url = f"https://graphis.ne.jp/monthly/?K={encoded_name}"
    else:
        url = f"https://graphis.ne.jp/monthly/?S=1&K={encoded_name}"

    logs.append(f"# URL: {url}")
    logs.append("")

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "ja,zh-CN;q=0.9,zh;q=0.8,en;q=0.7",
                },
            )
            logs.append(f"HTTP 状态码: {resp.status_code}")

            if resp.status_code != 200:
                logs.append(f"响应内容(前500字符): {resp.text[:500]}")
                logs.append("无法继续分析，HTTP 非 200")
                _all_logs.extend(logs)
                return

            orig_av, orig_names = analyze_html(resp.text, url, logs)
            _all_logs.extend(logs)

    except Exception as e:
        logs.append(f"异常: {e}")
        _all_logs.extend(logs)


async def main_with_output():
    names = []
    if len(sys.argv) > 1 and sys.argv[1] == "--names":
        names = [n.strip() for n in sys.argv[2].split(",") if n.strip()]
    else:
        names = [sys.argv[1]] if len(sys.argv) > 1 else ["梦乃爱华"]

    for name in names:
        for ver in ["old", "new"]:
            await test_actor_with_logs(name, version=ver)

    # 输出所有收集到的日志
    for log in _all_logs:
        print(log)


if __name__ == "__main__":
    asyncio.run(main_with_output())
