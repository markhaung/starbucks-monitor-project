"""
Tavily Search API 搜集模組
使用 Tavily 搜集 Starbucks 相關即時新聞
"""
import requests
from datetime import datetime


def fetch_tavily_news(keywords, api_key, max_results=20):
    """
    使用 Tavily API 搜集新聞

    Args:
        keywords: 搜尋關鍵字列表
        api_key: Tavily API Key
        max_results: 最多回傳幾篇

    Returns:
        統一格式的文章列表
    """
    if not api_key:
        print("  ⚠️  TAVILY_API_KEY 未設定，跳過 Tavily 搜集")
        return []

    all_articles = []
    seen_urls = set()

    for keyword in keywords:
        print(f"  🔎 Tavily 搜尋: {keyword}")
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": api_key,
                "query": keyword + " news",
                "search_depth": "basic",
                "include_news": True,
                "max_results": max_results,
            }

            resp = requests.post(url, json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            results = data.get("results", [])
            for item in results:
                article_url = item.get("url", "")
                if article_url in seen_urls:
                    continue
                seen_urls.add(article_url)

                # 取得發布日期
                published = item.get("published_date", "")
                if published:
                    try:
                        dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                        published = dt.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        published = published[:16]

                # 提取來源
                source = item.get("source")
                if not source:
                    # 如果沒有來源名稱，從網址擷取主網域
                    from urllib.parse import urlparse
                    try:
                        source = urlparse(article_url).netloc.replace("www.", "")
                    except:
                        source = "網路新聞"

                all_articles.append({
                    "title": item.get("title", ""),
                    "link": article_url,
                    "source": source,
                    "published_date": published,
                    "snippet": item.get("content", "")[:300],
                    "keyword": keyword,
                })

            print(f"    ✅ '{keyword}' 搜集到 {len(results)} 筆")

        except requests.exceptions.Timeout:
            print(f"  ⚠️  Tavily 搜尋 '{keyword}' 逾時，跳過")
        except Exception as e:
            print(f"  ⚠️  Tavily 搜尋 '{keyword}' 失敗: {e}")

    print(f"  📰 Tavily 共搜集到 {len(all_articles)} 篇文章")
    return all_articles
