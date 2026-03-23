"""
Telegram Bot 推播模組
使用 Telegram Bot API 發送文字摘要與 HTML 報告檔案
"""
import requests
import os


def send_telegram_notification(
    bot_token: str, chat_id: str, analysis_result: dict, report_path: str
) -> bool:
    """
    透過 Telegram Bot 發送輿情摘要與報告檔案

    Args:
        bot_token: Telegram Bot Token
        chat_id: Telegram Chat ID
        analysis_result: 分析結果
        report_path: 報告檔案路徑

    Returns:
        是否發送成功
    """
    if not bot_token or not chat_id:
        print("  ⚠️  TELEGRAM 設定不完整，跳過 Telegram 通知")
        return False

    success = True

    # Step 1: 發送文字摘要
    text_ok = _send_text_message(bot_token, chat_id, analysis_result)
    if not text_ok:
        success = False

    # Step 2: 發送 HTML 報告檔案
    if report_path and os.path.exists(report_path):
        file_ok = _send_document(bot_token, chat_id, report_path)
        if not file_ok:
            success = False

    return success


def _send_text_message(bot_token: str, chat_id: str, analysis_result: dict) -> bool:
    """發送文字摘要"""
    articles = analysis_result.get("articles", [])
    total = len(articles)
    positive = analysis_result.get("positive_count", 0)
    negative = analysis_result.get("negative_count", 0)
    neutral = analysis_result.get("neutral_count", 0)

    # 使用 Telegram MarkdownV2 格式
    message = (
        f"☕ *Starbucks 輿情日報*\n\n"
        f"📊 *今日統計*\n"
        f"總文章數: {total}\n"
        f"🟢 正面: {positive} 篇\n"
        f"🔴 負面: {negative} 篇\n"
        f"🟡 中立: {neutral} 篇\n\n"
        f"📝 *摘要*\n"
        f"{analysis_result.get('overall_summary', '無')}"
    )

    # 關鍵議題
    topics = analysis_result.get("key_topics", [])
    if topics:
        message += f"\n\n🏷️ *關鍵議題*\n{', '.join(topics)}"

    # 風險警示
    risk = analysis_result.get("risk_alert", "")
    if risk:
        message += f"\n\n🚨 *風險警示*\n{risk}"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200 and response.json().get("ok"):
            print("  ✅ Telegram 文字訊息發送成功")
            return True
        else:
            print(
                f"  ❌ Telegram 文字訊息發送失敗: {response.status_code} - {response.text}"
            )
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Telegram 文字訊息發送錯誤: {e}")
        return False


def _send_document(bot_token: str, chat_id: str, file_path: str) -> bool:
    """發送 HTML 報告檔案"""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

    try:
        with open(file_path, "rb") as f:
            files = {"document": (os.path.basename(file_path), f)}
            data = {
                "chat_id": chat_id,
                "caption": "📄 完整 HTML 報告，請下載後用瀏覽器開啟",
            }
            response = requests.post(url, data=data, files=files, timeout=30)

        if response.status_code == 200 and response.json().get("ok"):
            print("  ✅ Telegram 報告檔案發送成功")
            return True
        else:
            print(
                f"  ❌ Telegram 報告檔案發送失敗: {response.status_code} - {response.text}"
            )
            return False
    except Exception as e:
        print(f"  ❌ Telegram 報告檔案發送錯誤: {e}")
        return False
