"""
Starbucks 網路聲量監控系統 - 主程式
===========================================
整合搜集 → 分析 → 報告 → 通知的自動化 Pipeline
支援排程每日 9:00 AM 自動執行
"""
import argparse
import sys
import os
from datetime import datetime

from config import Config
from collectors.google_news import fetch_google_news
from collectors.news_api import fetch_news_api
from collectors.tavily_search import fetch_tavily_news
from analyzer.sentiment import analyze_articles
from reporter.generator import generate_report
from notifier.line_notify import send_line_notification
from notifier.telegram_bot import send_telegram_notification


def run_pipeline():
    """執行完整 Pipeline：搜集 → 分析 → 報告 → 通知"""
    start_time = datetime.now()
    print("=" * 60)
    print(f"☕ Starbucks 輿情監控 Pipeline 開始執行")
    print(f"⏰ 時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 驗證設定
    warnings = Config.validate()
    for w in warnings:
        print(f"  {w}")

    # ─── Step 1：搜集 ─────────────────────────────
    print("\n📡 Step 1: 搜集資料...")
    articles = []

    # Tavily Search（優先使用，品質較高）
    if Config.TAVILY_API_KEY:
        tavily_articles = fetch_tavily_news(Config.SEARCH_KEYWORDS, Config.TAVILY_API_KEY)
        articles.extend(tavily_articles)

    # Google News RSS（作為補充或備援）
    google_articles = fetch_google_news(Config.SEARCH_KEYWORDS)
    # 避免重複：只加入 Tavily 沒有的文章
    tavily_links = {a["link"] for a in articles}
    for a in google_articles:
        if a["link"] not in tavily_links:
            articles.append(a)

    # NewsAPI（若有設定）
    if Config.NEWS_API_KEY:
        newsapi_articles = fetch_news_api(Config.SEARCH_KEYWORDS, Config.NEWS_API_KEY)
        articles.extend(newsapi_articles)

    if not articles:
        print("  ⚠️  未搜集到任何文章，Pipeline 終止")
        return

    print(f"  ✅ 共搜集到 {len(articles)} 篇文章")

    # ─── Step 2：分析 ─────────────────────────────
    print("\n🔍 Step 2: LLM 情感分析...")
    analysis_result = analyze_articles(
        articles,
        gemini_api_key=Config.GEMINI_API_KEY,
        gemini_model=Config.GEMINI_MODEL,
        openai_api_key=Config.OPENAI_API_KEY,
        openai_model=Config.OPENAI_MODEL,
    )

    # ─── Step 3：報告 ─────────────────────────────
    print("\n📄 Step 3: 產生 HTML 報告...")
    report_path = generate_report(analysis_result, Config.REPORTS_DIR)

    # ─── Step 4：通知 ─────────────────────────────
    print("\n📢 Step 4: 發送通知...")

    # Line Notify
    send_line_notification(Config.LINE_NOTIFY_TOKEN, analysis_result, report_path)

    # Telegram Bot
    send_telegram_notification(
        Config.TELEGRAM_BOT_TOKEN,
        Config.TELEGRAM_CHAT_ID,
        analysis_result,
        report_path,
    )

    # ─── 完成 ─────────────────────────────────────
    elapsed = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print(f"✅ Pipeline 執行完成！耗時 {elapsed:.1f} 秒")
    print(f"📄 報告位置: {report_path}")
    print("=" * 60)


def start_scheduler():
    """啟動排程，每天指定時間執行 Pipeline"""
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = BlockingScheduler()

    # 設定排程：每天指定時間執行
    trigger = CronTrigger(
        hour=Config.SCHEDULE_HOUR,
        minute=Config.SCHEDULE_MINUTE,
        timezone="Asia/Taipei",
    )

    scheduler.add_job(
        run_pipeline,
        trigger=trigger,
        id="starbucks_pipeline",
        name="Starbucks 輿情監控",
        misfire_grace_time=3600,  # 若錯過排程，1 小時內補執行
    )

    next_run = trigger.get_next_fire_time(None, datetime.now())
    print("=" * 60)
    print("☕ Starbucks 輿情監控系統 - 排程模式")
    print(f"⏰ 排程時間: 每日 {Config.SCHEDULE_HOUR:02d}:{Config.SCHEDULE_MINUTE:02d}")
    print(f"📅 下次執行: {next_run}")
    print("🔄 系統運行中... 按 Ctrl+C 停止")
    print("=" * 60)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n⏹️  排程已停止")
        scheduler.shutdown()


def main():
    parser = argparse.ArgumentParser(
        description="☕ Starbucks 網路聲量監控系統",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例用法:
  python main.py --now      立即執行一次 Pipeline
  python main.py            啟動排程模式（每日自動執行）
        """,
    )

    parser.add_argument(
        "--now",
        action="store_true",
        help="立即執行一次 Pipeline（不啟動排程）",
    )

    args = parser.parse_args()

    if args.now:
        run_pipeline()
    else:
        start_scheduler()


if __name__ == "__main__":
    main()
