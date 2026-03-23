"""
HTML 報告產生模組
使用 Jinja2 渲染 HTML 報告
"""
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


def generate_report(analysis_result: dict, output_dir: str) -> str:
    """
    根據分析結果產生 HTML 報告

    Args:
        analysis_result: 情感分析結果字典
        output_dir: 報告輸出目錄

    Returns:
        報告檔案的完整路徑
    """
    # 確保輸出目錄存在
    os.makedirs(output_dir, exist_ok=True)

    # 載入模板
    template_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("template.html")

    # 準備模板變數
    articles = analysis_result.get("articles", [])
    positive_count = analysis_result.get("positive_count", 0)
    negative_count = analysis_result.get("negative_count", 0)
    neutral_count = analysis_result.get("neutral_count", 0)
    total_count = len(articles)

    # 計算百分比
    if total_count > 0:
        positive_pct = round(positive_count / total_count * 100)
        negative_pct = round(negative_count / total_count * 100)
        neutral_pct = 100 - positive_pct - negative_pct
    else:
        positive_pct = negative_pct = neutral_pct = 0

    now = datetime.now()
    report_date = now.strftime("%Y-%m-%d")
    generated_at = now.strftime("%Y-%m-%d %H:%M:%S")

    # 渲染 HTML
    html_content = template.render(
        report_date=report_date,
        generated_at=generated_at,
        overall_summary=analysis_result.get("overall_summary", ""),
        total_count=total_count,
        positive_count=positive_count,
        negative_count=negative_count,
        neutral_count=neutral_count,
        positive_pct=positive_pct,
        negative_pct=negative_pct,
        neutral_pct=neutral_pct,
        key_topics=analysis_result.get("key_topics", []),
        risk_alert=analysis_result.get("risk_alert", ""),
        articles=articles,
    )

    # 儲存報告
    filename = f"starbucks_report_{report_date}.html"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"  📄 報告已產生: {filepath}")
    return filepath
