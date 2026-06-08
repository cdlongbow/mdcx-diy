"""
查找指定演员缺少作品
"""

import json
import re
import time
from pathlib import Path
from typing import cast

import aiofiles
import aiofiles.os
from lxml import etree

from ..base.file import movie_lists
from ..config.manager import manager
from ..config.resources import resources
from ..core.file import get_file_info_v2
from ..models.flags import Flags
from ..signals import signal
from ..utils import get_used_time


async def _scraper_web(url):
    async with manager.acquire_computed() as computed:
        html, error = await computed.async_client.get_text(url)
    if html is None:
        signal.show_log_text(f"请求错误: {error}")
        return ""
    if "The owner of this website has banned your access based on your browser's behaving" in html:
        signal.show_log_text(f"由于请求过多，javdb网站暂时禁止了你当前IP的访问！！可访问javdb.com查看详情！ {html}")
        return ""
    if "Cloudflare" in html:
        signal.show_log_text("被 Cloudflare 5 秒盾拦截！请尝试更换cookie！")
        return ""
    return html


async def _get_actor_numbers(actor_url, actor_single_url):
    """
    获取演员的番号列表（使用JAVBus替代JAVDB）
    """
    from ..config.enums import Website
    from ..config.manager import manager
    
    # 获取JAVBus基础URL
    javbus_url = manager.config.get_site_url(Website.JAVBUS, "https://www.javbus.com")
    
    # 获取单体番号
    next_page = True
    number_single_list = set()
    i = 1
    while next_page:
        # 使用JAVBus的演员详情页URL格式
        page_url = f"{actor_url}?page={i}"
        async with manager.acquire_computed() as computed:
            html, error = await computed.async_client.get_text(page_url)
        if html is None:
            if i == 1:  # 第一页就失败，可能是URL格式问题
                # 尝试使用JAVBus格式的URL
                page_url = f"{actor_url}?page={i}&t=s"
                async with manager.acquire_computed() as computed:
                    html, error = await computed.async_client.get_text(page_url)
            if html is None:
                return
        
        # 检查是否被年龄验证挡住
        if "你是否已經成年" in html or "Age Verification" in html:
            signal.show_log_text("   提示：JAVBus需要年龄验证，请先在浏览器中访问并确认年龄")
            return
            
        # 检查是否有错误页面
        if "404" in html or "Not Found" in html:
            signal.show_log_text("   演员页面不存在或URL错误")
            return
        
        from lxml import etree
        from ..crawlers.javbus import get_actress_video_list
        
        html_obj = etree.fromstring(html, etree.HTMLParser())
        result = get_actress_video_list(html_obj, javbus_url)
        
        if not result["videos"]:
            break
            
        for video in result["videos"]:
            number_single_list.add(video["number"])
        
        if not result["has_next"] or i >= 60:
            next_page = False
            if i == 60:
                signal.show_log_text("   已达 60 页上限！！！（JAVBus 可能限制显示数量）")
        i += 1
    
    Flags.actor_numbers_dic[actor_single_url] = number_single_list

    # 获取全部番号
    next_page = True
    i = 1
    while next_page:
        page_url = f"{actor_url}?page={i}"
        html = await _scraper_web(page_url)
        if len(html) < 1:
            return
        
        # 检查是否被年龄验证挡住
        if "你是否已經成年" in html or "Age Verification" in html:
            signal.show_log_text("   提示：JAVBus需要年龄验证，请先在浏览器中访问并确认年龄")
            return
            
        html_obj = etree.fromstring(html, etree.HTMLParser(encoding="utf-8"))
        result = get_actress_video_list(html_obj, javbus_url)
        
        if not result["videos"]:
            break
            
        for video in result["videos"]:
            video_number = video["number"]
            video_title = video["title"]
            video_date = video["date"]
            video_url = video["url"]
            
            # 格式化日期
            time_list = re.split(r"[./-]", video_date)
            if len(time_list) >= 3:
                if len(time_list[0]) == 2:
                    video_date = f"{time_list[2]}/{time_list[0]}/{time_list[1]}"
                else:
                    video_date = f"{time_list[0]}/{time_list[1]}/{time_list[2]}"
            
            # JAVBus可能不提供磁力链接信息，使用空字符串
            download_info = "   "
            single_info = "单体" if video_number in number_single_list else "\u3000\u3000"
            
            Flags.actor_numbers_dic[actor_url].update(
                {video_number: [video_number, video_date, video_url, download_info, video_title, single_info]}
            )
        
        if not result["has_next"] or i >= 60:
            next_page = False
            if i == 60:
                signal.show_log_text("   已达 60 页上限！！！（JAVBus 可能限制显示数量）")
        i += 1


async def _get_actor_missing_numbers(actor_name, actor_url, actor_flag):
    """
    获取演员缺少的番号列表
    """
    start_time = time.time()
    actor_single_url = actor_url + "?t=s"

    # 获取演员的所有番号，如果字典有，就从字典读取，否则去网络请求
    if not Flags.actor_numbers_dic.get(actor_url):
        Flags.actor_numbers_dic[actor_url] = {}
        Flags.actor_numbers_dic[actor_single_url] = {}  # 单体作品
        await _get_actor_numbers(actor_url, actor_single_url)  # 如果字典里没有该演员主页的番号，则从网络获取演员番号

    # 演员信息排版和显示
    actor_info = Flags.actor_numbers_dic.get(actor_url)
    len_single = len(Flags.actor_numbers_dic.get(actor_single_url))
    signal.show_log_text(
        f"🎉 获取完毕！共找到 [ {actor_name} ] 番号数量（{len(actor_info)}）单体数量（{len_single}）({get_used_time(start_time)}s)"
    )
    if actor_info:
        actor_numbers = actor_info.keys()
        all_list = set()
        not_download_list = set()
        not_download_magnet_list = set()
        not_download_cnword_list = set()
        for actor_number in actor_numbers:
            video_number, video_date, video_url, download_info, video_title, single_info = actor_info.get(actor_number)
            if actor_flag:
                video_url = video_title[:30]
            space_char = "　"  # 全角空格
            number_str = (
                f"{video_date:>13}  {video_number:<10} {single_info}  {download_info:{space_char}>5}   {video_url}"
            )
            all_list.add(number_str)
            if actor_number not in Flags.local_number_set:
                not_download_list.add(number_str)
                if "🧲" in download_info:
                    not_download_magnet_list.add(number_str)

                if "🀄️" in download_info:
                    not_download_cnword_list.add(number_str)
            elif actor_number not in Flags.local_number_cnword_set and "🀄️" in download_info:
                not_download_cnword_list.add(number_str)

        all_list = sorted(all_list, reverse=True)
        not_download_list = sorted(not_download_list, reverse=True)
        not_download_magnet_list = sorted(not_download_magnet_list, reverse=True)
        not_download_cnword_list = sorted(not_download_cnword_list, reverse=True)

        signal.show_log_text(f"\n👩 [ {actor_name} ] 的全部网络番号({len(all_list)})...\n{('=' * 97)}")
        if all_list:
            for each in all_list:
                signal.show_log_text(each)
        else:
            signal.show_log_text("🎉 没有缺少的番号...\n")

        signal.show_log_text(f"\n👩 [ {actor_name} ] 本地缺失的番号({len(not_download_list)})...\n{('=' * 97)}")
        if not_download_list:
            for each in not_download_list:
                signal.show_log_text(each)
        else:
            signal.show_log_text("🎉 没有缺少的番号...\n")

        signal.show_log_text(
            f"\n👩 [ {actor_name} ] 本地缺失的有磁力的番号({len(not_download_magnet_list)})...\n{('=' * 97)}"
        )
        if not_download_magnet_list:
            for each in not_download_magnet_list:
                signal.show_log_text(each)
        else:
            signal.show_log_text("🎉 没有缺少的番号...\n")

        signal.show_log_text(
            f"\n👩 [ {actor_name} ] 本地缺失的有字幕的番号({len(not_download_cnword_list)})...\n{('=' * 97)}"
        )
        if not_download_cnword_list:
            for each in not_download_cnword_list:
                signal.show_log_text(each)
        else:
            signal.show_log_text("🎉 没有缺少的番号...\n")


async def check_missing_number(actor_flag):
    """
    检查缺失番号
    """
    signal.change_buttons_status.emit()
    start_time = time.time()
    local_movies: dict[str, tuple[str, bool]] = {}

    # 获取资源库配置
    movie_type = manager.config.media_type
    libraries = manager.config.local_library  # 用户设置的扫描媒体路径
    libraries = {Path(p) for p in libraries if p.strip()}

    # 遍历本地资源库
    signal.show_log_text("")
    signal.show_log_text(
        f"\n本地资源库地址:\n   {'\n   '.join(str(p) for p in libraries)}\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n⏳ 开始遍历本地资源库，以获取本地视频的最新列表...\n   提示：每次启动第一次查询将更新本地视频数据。（大概1000个/30秒，如果视频较多，请耐心等待。）"
    )
    all_movies: list[Path] = []
    for p in libraries:
        movies = await movie_lists([], movie_type, p)  # 获取所有需要刮削的影片列表
        all_movies.extend(movies)
    signal.show_log_text(f"🎉 获取完毕！共找到视频数量（{len(all_movies)}）({get_used_time(start_time)}s)")

    # 获取本地番号
    start_time_local = time.time()
    signal.show_log_text("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n⏳ 开始获取本地视频的番号信息...")
    local_number_list = resources.u("number_list.json")
    if not await aiofiles.os.path.exists(local_number_list):
        signal.show_log_text(
            "   提示：正在生成本地视频的番号信息数据...（第一次较慢，请耐心等待，以后只需要查找新视频，速度很快）"
        )
        async with aiofiles.open(local_number_list, "w", encoding="utf-8") as f:
            await f.write("{}")
    async with aiofiles.open(local_number_list, encoding="utf-8") as data:
        json_data = json.loads(await data.read())
        json_data = cast("dict[str, tuple[str, bool]]", json_data)
    for movie in all_movies:
        nfo_path = movie.with_suffix(".nfo")
        number = ""
        has_sub = False
        if r := json_data.get(movie.as_posix()):
            number, has_sub = r
        else:
            if await aiofiles.os.path.exists(nfo_path):
                async with aiofiles.open(nfo_path, encoding="utf-8") as f:
                    nfo_content = await f.read()
                number_result = re.findall(r"<num>(.+)</num>", nfo_content)
                if number_result:
                    number = number_result[0]

                    if "<genre>中文字幕</genre>" in nfo_content or "<tag>中文字幕</tag>" in nfo_content:
                        has_sub = True
                    else:
                        has_sub = False
            if not number:
                file_info = await get_file_info_v2(movie, copy_sub=False)
                has_sub = file_info.has_sub
                number = file_info.number
            cn_word_icon = "🀄️" if has_sub else ""
            signal.show_log_text(f"   发现新番号：{number:<10} {cn_word_icon}")
        temp_number = re.findall(r"\d{3,}([a-zA-Z]+-\d+)", number)  # 去除前缀，因为 javdb 不带前缀
        number = temp_number[0] if temp_number else number
        local_movies[movie.as_posix()] = (number, has_sub)  # 用新表，更新完重新写入到本地文件中
        Flags.local_number_set.add(number)  # 添加到本地番号集合
        if has_sub:
            Flags.local_number_cnword_set.add(number)  # 添加到本地有字幕的番号集合

    async with aiofiles.open(local_number_list, "w", encoding="utf-8") as f:
        await f.write(
            json.dumps(
                local_movies,
                ensure_ascii=False,
                sort_keys=True,
                indent=4,
                separators=(",", ": "),
            )
        )
    signal.show_log_text(f"🎉 获取完毕！共获取番号数量（{len(local_movies)}）({get_used_time(start_time_local)}s)")

    # 查询演员番号
    if manager.config.actors_name:
        actor_list = re.split(r"[,，]", manager.config.actors_name)
        signal.show_log_text(
            f"\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n🔍 需要查询的演员：\n   {', '.join(actor_list)}"
        )
        for actor_name in actor_list:
            if not actor_name:
                continue
            actor_url = actor_name if "http" in actor_name else resources.get_actor_data(actor_name).get("href")
            if actor_url:
                signal.show_log_text(
                    f"\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n⏳ 从 JAVBus 获取 [ {actor_name} ] 的所有番号列表..."
                )
                await _get_actor_missing_numbers(actor_name, actor_url, actor_flag)
            else:
                signal.show_log_text(
                    f"\n🔴 未找到 [ {actor_name} ] 的主页地址，你可以填写演员的 JAVBus 主页地址替换演员名称..."
                )
    else:
        signal.show_log_text("\n🔴 没有要查询的演员！")

    signal.show_log_text(f"\n🎉 查询完毕！共用时({get_used_time(start_time)}s)")
    signal.reset_buttons_status.emit()
