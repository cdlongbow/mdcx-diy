"""
Amazon ASIN 数据库保存功能
用于保存影片番号与 ASIN 对应关系，方便后续统计和复用
"""

from datetime import datetime
from pathlib import Path
from typing import TypedDict


class AsinRecord(TypedDict, total=False):
    """ASIN 记录结构"""

    number: str  # 影片番号
    asin: str  # 亚马逊 ASIN
    product_url: str  # 亚马逊商品详情页链接
    title: str  # 商品标题
    poster_url: str  # 封面图片 URL
    search_keyword: str  # 搜索关键词


def _get_default_excel_path() -> Path:
    """获取默认的 Excel 文件路径，位于 userdata 目录下（与 mapping、watermark 等同目录）"""
    from ..config.manager import manager
    userdata_dir = manager.data_folder / "userdata"
    userdata_dir.mkdir(parents=True, exist_ok=True)
    return userdata_dir / "amazon_asin_database.xlsx"


async def save_asin_to_excel(
    records: list[AsinRecord],
    excel_path: Path | None = None,
    *,
    sheet_name: str = "ASIN 数据库",
    max_rows: int = 100000,
) -> Path:
    """
    保存 ASIN 记录到 Excel 文件

    Args:
        records: ASIN 记录列表
        excel_path: Excel 文件路径，默认保存到运行目录下的 amazon_asin_database.xlsx
        sheet_name: 工作表名称
        max_rows: 单个 sheet 最大行数，超过会自动分 sheet

    Returns:
        Excel 文件路径

    注意：
        需要安装 openpyxl 库：pip install openpyxl
    """
    try:
        import openpyxl
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise ImportError("请安装 openpyxl 库：pip install openpyxl")

    if excel_path is None:
        excel_path = _get_default_excel_path()
    elif isinstance(excel_path, str):
        excel_path = Path(excel_path)

    excel_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        wb = openpyxl.load_workbook(excel_path)
    except FileNotFoundError:
        wb = openpyxl.Workbook()

    ws = wb.active
    ws.title = sheet_name

    if not ws["A1"].value:
        headers = [
            "影片番号",
            "ASIN 编号",
            "影片链接",
            "商品标题",
            "封面 URL",
            "搜索关键词",
        ]
        # 使用 cell() 直接设置表头，避免 append() 的空行问题
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = openpyxl.styles.Font(bold=True)
            cell.fill = openpyxl.styles.PatternFill("solid", fgColor="C0C0C0")
            cell.alignment = openpyxl.styles.Alignment(horizontal="center")

        ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"

    for record in records:
        row_data = [
            record.get("number", ""),
            record.get("asin", ""),
            record.get("product_url", ""),
            record.get("title", ""),
            record.get("poster_url", ""),
            record.get("search_keyword", ""),
        ]
        ws.append(row_data)

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)) + 2)
            except (TypeError, AttributeError):
                pass
        adjusted_width = min(max_length, 100)
        ws.column_dimensions[column].width = adjusted_width

    try:
        wb.save(excel_path)
        wb.close()
    except PermissionError as e:
        raise PermissionError(f"无法保存 Excel 文件，可能文件正被其他程序打开：{excel_path}") from e

    return excel_path


async def save_single_asin_record(
    number: str,
    asin: str,
    title: str = "",
    product_url: str = "",
    poster_url: str = "",
    search_keyword: str = "",
    excel_path: Path | None = None,
) -> bool:
    """
    保存单条 ASIN 记录

    Args:
        number: 影片番号
        asin: ASIN 编号（必须为 10 位字母数字）
        title: 商品标题
        product_url: 亚马逊商品详情页链接
        poster_url: 封面图片 URL
        search_keyword: 搜索关键词
        excel_path: Excel 文件路径

    Returns:
        bool: 保存成功返回 True，失败或跳过返回 False

    示例:
        success = await save_single_asin_record(
            number="ABC-123",
            asin="B0000001",
            title="作品标题",
            product_url="https://www.amazon.co.jp/dp/B0000001",
            poster_url="https://m.media-amazon.com/images/I/xxx.jpg",
        )
        if success:
            print("保存成功")
        else:
            print("保存失败或跳过")
    """
    import re

    if not asin or not asin.strip():
        return False

    asin = asin.strip().upper()

    if not re.match(r"^[A-Z0-9]{10}$", asin):
        return False

    record: AsinRecord = {
        "number": number,
        "asin": asin,
        "product_url": product_url,
        "title": title,
        "poster_url": poster_url,
        "search_keyword": search_keyword,
    }

    try:
        await save_asin_to_excel([record], excel_path)
        return True
    except Exception:
        return False


async def query_asin_database(
    number: str | None = None,
    asin: str | None = None,
    excel_path: Path | None = None,
) -> list[AsinRecord]:
    """
    查询 ASIN 数据库

    Args:
        number: 按番号查询
        asin: 按 ASIN 查询
        excel_path: Excel 文件路径

    Returns:
        匹配的记录列表

    示例:
        results = await query_asin_database(number="ABC-123")
        results = await query_asin_database(asin="B0000001")
    """
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        raise ImportError("请安装 openpyxl 库：pip install openpyxl")

    if excel_path is None:
        excel_path = _get_default_excel_path()

    if not excel_path.exists():
        return []

    wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
    ws = wb.active

    results: list[AsinRecord] = []

    for row_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if row_idx == 1:
            continue

        if len(row) < 6:
            continue

        record = AsinRecord(
            number=str(row[0] or ""),
            asin=str(row[1] or ""),
            product_url=str(row[2] or ""),
            title=str(row[3] or ""),
            poster_url=str(row[4] or ""),
            search_keyword=str(row[5] or ""),
        )

        if number and str(record.get("number", "")).upper() == number.upper():
            results.append(record)
        elif asin and str(record.get("asin", "")).upper() == asin.upper():
            results.append(record)

    wb.close()
    return results


async def export_asin_statistics(
    excel_path: Path | None = None,
    output_path: Path | None = None,
) -> dict:
    """
    导出 ASIN 数据库统计信息

    Returns:
        统计信息字典
    """
    try:
        import openpyxl
    except ImportError:
        raise ImportError("请安装 openpyxl 库：pip install openpyxl")

    if excel_path is None:
        excel_path = _get_default_excel_path()

    if not excel_path.exists():
        return {}

    if output_path is None:
        output_path = excel_path.parent / "amazon_statistics.txt"

    wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
    ws = wb.active

    total_records = 0

    for row_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if row_idx == 1:
            continue

        if len(row) < 2:
            continue

        total_records += 1

    wb.close()

    stats = {
        "total_records": total_records,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("Amazon ASIN 数据库统计报告\n")
        f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"总记录数：{total_records}\n")
        f.write("\n" + "=" * 60 + "\n")

    return stats
