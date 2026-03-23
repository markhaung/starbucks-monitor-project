"""
NewsAPI 搜集模組（可選）
使用 NewsAPI 搜集 Starbucks 相關新聞
需要 NEWS_API_KEY 才能使用
"""
import requests
from datetime import datetime, timedelta


def fetch_news_api(
    keywords: list, api_key: str, max_results: int = 20
) -> list:
    """
    從 NewsAPI 搜集新聞

    Args:
        keywords: 搜尋關鍵字列表
        api_key: NewsAPI 金鑰
        max_results: 最多回傳幾篇

    Returns:
        統一格式的文章列表
    """
    if not api_key:
        print("  ⚠️  NEWS_API_KEY 未設定，跳過 NewsAPI 搜集")
        return []

    all_articles = []
    seen_urls = set()

    # 搜尋過去 24 小時的新聞
    from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    query = " OR ".join(keywords)

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date,
        "sortBy": "publishedAt",
        "pageSize": max_results,
        "language": "en",
        "apiKey": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "ok":
            print(f"  ⚠️  NewsAPI 回傳錯誤: {data.get('message', '未知錯誤')}")
            return []

        for article in data.get("articles", []):
            article_url = article.get("url", "")
            if article_url in seen_urls:
                continue
            seen_urls.add(article_url)

            # 解析發布日期
            published = ""
            pub_at = article.get("publishedAt", "")
            if pub_at:
                try:
                    dt = datetime.fromisoformat(pub_at.replace("Z", "+00:00"))
                    published = dt.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    published = pub_at[:16]

            all_articles.append(
                {
                    "title": article.get("title", ""),
                    "link": article_url,
                    "source": article.get("source", {}).get("name", "未知來源"),
                    "published_date": published,
                    "snippet": article.get("description", "") or "",
                    "keyword": query,
                }
            )

        print(f"  📰 NewsAPI 共搜集到 {len(all_articles)} 篇文章")

    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  NewsAPI 請求失敗: {e}")

    return all_articles
