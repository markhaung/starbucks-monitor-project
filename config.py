"""
設定管理模組 - 從 .env 讀取所有環境變數
"""
import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()


class Config:
    """統一設定存取介面"""

    # Tavily Search API
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

    # Google Gemini（情感分析）
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # OpenAI（備用，若有設定則優先）
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Line Messaging API
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    LINE_USER_ID = os.getenv("LINE_USER_ID", "")

    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # NewsAPI（可選）
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

    # 排程設定
    SCHEDULE_HOUR = int(os.getenv("SCHEDULE_HOUR", "9"))
    SCHEDULE_MINUTE = int(os.getenv("SCHEDULE_MINUTE", "0"))

    # 搜尋關鍵字
    SEARCH_KEYWORDS = os.getenv("SEARCH_KEYWORDS", "Starbucks,星巴克").split(",")

    # 報告輸出目錄
    REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")

    @classmethod
    def validate(cls):
        """驗證必要設定是否已填入"""
        warnings = []
        if not cls.OPENAI_API_KEY:
            warnings.append("⚠️  OPENAI_API_KEY 未設定，分析功能將無法使用")
        if not cls.LINE_CHANNEL_ACCESS_TOKEN or not cls.LINE_USER_ID:
            warnings.append("⚠️  LINE_CHANNEL_ACCESS_TOKEN 或 LINE_USER_ID 未設定，Line 通知將無法發送")
        if not cls.TELEGRAM_BOT_TOKEN or not cls.TELEGRAM_CHAT_ID:
            warnings.append("⚠️  TELEGRAM 設定不完整，Telegram 通知將無法發送")
        return warnings
