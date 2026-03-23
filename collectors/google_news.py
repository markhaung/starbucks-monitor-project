"""
Google News RSS 搜集模組
使用 Google News RSS feed 搜集 Starbucks 相關新聞
"""
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote
import time
import re


def fetch_google_news(keywords: list, max_results: int = 20) -> list:
    """
    從 Google News RSS 搜集新聞

    Args:
        keywords: 搜尋關鍵字列表
        max_results: 每個關鍵字最多回傳幾篇

    Returns:
        統一格式的文章列表
    """
    all_articles = []
    seen_links = set()

    for keyword in keywords:
        encoded_keyword = quote(keyword)
        rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"

        try:
            print(f"  🔎 搜尋關鍵字: {keyword}")
            # 先用 requests 抓取（有 timeout），再交給 feedparser 解析
            resp = requests.get(rss_url, timeout=10)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)

            for entry in feed.entries[:max_results]:
                link = entry.get("link", "")

                # 去重
                if link in seen_links:
                    continue
                seen_links.add(link)

                # 解析發布日期
                published = ""
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6]).strftime(
                        "%Y-%m-%d %H:%M"
                    )

                # 清除 HTML 標籤
                title = _clean_html(entry.get("title", ""))
                snippet = _clean_html(entry.get("summary", ""))

                # 提取來源
                source = entry.get("source", {}).get("title", "未知來源")

                all_articles.append(
                    {
                        "title": title,
                        "link": link,
                        "source": source,
                        "published_date": published,
                        "snippet": snippet,
                        "keyword": keyword,
                    }
                )

            print(f"    ✅ '{keyword}' 搜集到 {len(feed.entries)} 筆")
            # 禮貌性延遲，避免被封鎖
            time.sleep(1)

        except requests.exceptions.Timeout:
            print(f"  ⚠️  搜集 '{keyword}' 逾時（10秒），跳過")
        except Exception as e:
            print(f"  ⚠️  搜集 '{keyword}' 時發生錯誤: {e}")

    print(f"  📰 Google News 共搜集到 {len(all_articles)} 篇文章")
    return all_articles


def _clean_html(text: str) -> str:
    """移除 HTML 標籤"""
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(strip=True)
