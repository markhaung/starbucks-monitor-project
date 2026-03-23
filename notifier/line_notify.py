"""
Line Notify 推播模組
使用 Line Notify API 發送文字摘要通知
"""
import requests


def send_line_notification(token: str, analysis_result: dict, report_path: str) -> bool:
    """
    透過 Line Notify 發送輿情摘要

    Args:
        token: Line Notify Token
        analysis_result: 分析結果
        report_path: 報告檔案路徑

    Returns:
        是否發送成功
    """
    if not token:
        print("  ⚠️  LINE_NOTIFY_TOKEN 未設定，跳過 Line 通知")
        return False

    # 組合訊息內容
    articles = analysis_result.get("articles", [])
    total = len(articles)
    positive = analysis_result.get("positive_count", 0)
    negative = analysis_result.get("negative_count", 0)
    neutral = analysis_result.get("neutral_count", 0)

    message = f"""
☕ Starbucks 輿情日報

📊 今日統計
總文章數: {total}
🟢 正面: {positive} 篇
🔴 負面: {negative} 篇
🟡 中立: {neutral} 篇

📝 摘要
{analysis_result.get('overall_summary', '無')}"""

    # 關鍵議題
    topics = analysis_result.get("key_topics", [])
    if topics:
        message += f"\n\n🏷️ 關鍵議題\n{', '.join(topics)}"

    # 風險警示
    risk = analysis_result.get("risk_alert", "")
    if risk:
        message += f"\n\n🚨 風險警示\n{risk}"

    # 發送通知
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message}

    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            print("  ✅ Line 通知發送成功")
            return True
        else:
            print(f"  ❌ Line 通知發送失敗: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Line 通知發送錯誤: {e}")
        return False
