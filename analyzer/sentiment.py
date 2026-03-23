"""
LLM 情感分析模組
優先使用 Google Gemini，備用 OpenAI
"""
import json
import requests


def analyze_articles(articles, gemini_api_key="", gemini_model="gemini-1.5-flash",
                     openai_api_key="", openai_model="gpt-4o-mini"):
    """
    使用 LLM 對文章進行批次情感分析

    Args:
        articles: 文章列表
        gemini_api_key: Google Gemini API Key（優先）
        gemini_model: Gemini 模型名稱
        openai_api_key: OpenAI API Key（備用）
        openai_model: OpenAI 模型名稱

    Returns:
        分析結果字典
    """
    if not articles:
        print("  ⚠️  沒有文章需要分析")
        return _empty_result()

    # 優先使用 Gemini
    if gemini_api_key:
        print("  🤖 使用 Google Gemini 進行情感分析...")
        return _analyze_with_gemini(articles, gemini_api_key, gemini_model)

    # 備用 OpenAI
    if openai_api_key:
        print("  🤖 使用 OpenAI 進行情感分析...")
        return _analyze_with_openai(articles, openai_api_key, openai_model)

    # 都沒有 API Key
    print("  ⚠️  未設定任何 LLM API Key，使用模擬分析結果")
    return _mock_analysis(articles)


def _build_prompt(articles):
    """組合分析 prompt"""
    articles_text = ""
    for i, article in enumerate(articles[:30], 1):
        articles_text += "\n[{}] 標題: {}\n".format(i, article['title'])
        articles_text += "    來源: {}\n".format(article['source'])
        articles_text += "    摘要: {}\n".format(article['snippet'][:200])

    prompt = """你是一位品牌輿情分析專家。以下是今日搜集到的 Starbucks（星巴克）相關新聞文章。
請分析每篇文章的情感傾向，並提供整體摘要。

{}

請用以下 JSON 格式回覆（直接輸出 JSON，不要加任何說明文字或 markdown 標記）：
{{
    "overall_summary": "今日星巴克整體輿情摘要（2-3 句話，用繁體中文）",
    "positive_count": 正面文章數量,
    "negative_count": 負面文章數量,
    "neutral_count": 中立文章數量,
    "key_topics": ["關鍵議題1", "關鍵議題2", "關鍵議題3"],
    "risk_alert": "若有重要負面事件請說明，否則留空字串",
    "articles": [
        {{
            "index": 1,
            "sentiment": "正面",
            "score": 75,
            "brief": "一句話描述"
        }}
    ]
}}""".format(articles_text)
    return prompt


def _parse_result(result_text, articles):
    """解析 LLM 回傳的 JSON 並合併回文章資料"""
    # 清除可能的 markdown 標記
    text = result_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    result = json.loads(text)

    # 合併分析結果回文章
    article_analyses = {item["index"]: item for item in result.get("articles", [])}
    for i, article in enumerate(articles[:30], 1):
        analysis = article_analyses.get(i, {})
        article["sentiment"] = analysis.get("sentiment", "中立")
        article["sentiment_score"] = analysis.get("score", 50)
        article["analysis_brief"] = analysis.get("brief", "")

    for article in articles[30:]:
        article["sentiment"] = "中立"
        article["sentiment_score"] = 50
        article["analysis_brief"] = "（未分析）"

    print("  🔍 分析完成: 正面 {} / 負面 {} / 中立 {}".format(
        result.get("positive_count", 0),
        result.get("negative_count", 0),
        result.get("neutral_count", 0),
    ))

    return {
        "overall_summary": result.get("overall_summary", ""),
        "positive_count": result.get("positive_count", 0),
        "negative_count": result.get("negative_count", 0),
        "neutral_count": result.get("neutral_count", 0),
        "key_topics": result.get("key_topics", []),
        "risk_alert": result.get("risk_alert", ""),
        "articles": articles,
    }


def _analyze_with_gemini(articles, api_key, model):
    """使用 Google Gemini API 分析"""
    import time
    prompt = _build_prompt(articles)
    url = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}".format(
        model, api_key
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3},
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, json=payload, timeout=60)

            # 429 = 請求太頻繁，等待後重試
            if resp.status_code == 429:
                wait = 15 * (attempt + 1)
                print("  ⏳ Gemini API 請求過於頻繁，等待 {} 秒後重試（第 {}/{} 次）...".format(
                    wait, attempt + 1, max_retries))
                time.sleep(wait)
                continue

            resp.raise_for_status()
            data = resp.json()

            result_text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )

            return _parse_result(result_text, articles)

        except requests.exceptions.Timeout:
            print("  ⚠️  Gemini 請求逾時，重試中...")
        except Exception as e:
            if "429" not in str(e):
                print("  ⚠️  Gemini 分析失敗: {}".format(e))
                break

    print("  ⚠️  Gemini 多次重試仍失敗，改用模擬結果")
    return _mock_analysis(articles)


def _analyze_with_openai(articles, api_key, model):
    """使用 OpenAI API 分析"""
    import openai
    openai.api_key = api_key
    prompt = _build_prompt(articles)

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是品牌輿情分析專家，請直接以合法 JSON 格式回覆。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        result_text = response.choices[0].message.content
        return _parse_result(result_text, articles)

    except Exception as e:
        print("  ⚠️  OpenAI 分析失敗: {}".format(e))
        return _mock_analysis(articles)


def _mock_analysis(articles):
    """當 API 不可用時，提供模擬分析結果"""
    for article in articles:
        article["sentiment"] = "中立"
        article["sentiment_score"] = 50
        article["analysis_brief"] = "（API 未設定，模擬結果）"

    return {
        "overall_summary": "（API 未設定）今日共搜集到 {} 篇相關文章，尚未進行實際情感分析。".format(len(articles)),
        "positive_count": 0,
        "negative_count": 0,
        "neutral_count": len(articles),
        "key_topics": ["待分析"],
        "risk_alert": "",
        "articles": articles,
    }


def _empty_result():
    """空結果"""
    return {
        "overall_summary": "今日未搜集到相關文章。",
        "positive_count": 0,
        "negative_count": 0,
        "neutral_count": 0,
        "key_topics": [],
        "risk_alert": "",
        "articles": [],
    }
