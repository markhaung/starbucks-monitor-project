"""
Line Messaging API 推播模組
使用 LINE 官方帳號發送文字摘要通知
"""
import requests
import json

def send_line_notification(token: str, user_id: str, analysis_result: dict, report_path: str) -> bool:
    """
    透過 Line Messaging API (官方帳號) 發送輿情摘要

    Args:
        token: Line Channel Access Token
        user_id: 你的 Line User ID
        analysis_result: 分析結果
        report_path: 報告檔案路徑

    Returns:
        是否發送成功
    """
    if not token or not user_id:
        print("  ⚠️  LINE Channel Access Token 或 User ID 未設定，跳過 Line 通知")
        return False

    # 組合訊息內容
    articles = analysis_result.get("articles", [])
    total = len(articles)
    positive = analysis_result.get("positive_count", 0)
    negative = analysis_result.get("negative_count", 0)
    neutral = analysis_result.get("neutral_count", 0)

    message_text = f"☕ Starbucks 輿情日報\n\n📊 今日統計\n總文章數: {total}\n🟢 正面: {positive} 篇\n🔴 負面: {negative} 篇\n🟡 中立: {neutral} 篇\n\n📝 摘要\n{analysis_result.get('overall_summary', '無')}"

    # 關鍵議題
    topics = analysis_result.get("key_topics", [])
    if topics:
        message_text += f"\n\n🏷️ 關鍵議題\n{', '.join(topics)}"

    # 風險警示
    risk = analysis_result.get("risk_alert", "")
    if risk:
        message_text += f"\n\n🚨 風險警示\n{risk}"

    # 發送通知給指定 User ID
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message_text
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        if response.status_code == 200:
            print("  ✅ Line 通知發送成功")
            return True
        else:
            print(f"  ❌ Line 通知發送失敗: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Line 通知發送錯誤: {e}")
        return False
