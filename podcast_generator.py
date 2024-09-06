import logging
from datetime import date

import requests

from anthropic_chat_completion.chat_request import send_chat_request
from config import Config
from text_to_speech import text_to_speech
from web_scraper import get_website_text_content

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def generate_queries(user_description: str, num_queries: int = 3) -> list:
    prompt = f"Based on the following user description, generate {num_queries} search queries for finding relevant articles:\n\nUser description: {user_description}"
    response = send_chat_request(prompt)
    queries = [query.strip() for query in response.split("\n") if query.strip()]
    return queries[:num_queries]


def search_articles(query: str, num_results: int = 10):
    logging.info(f"SEARCHING ARTICLES FOR: {query}")
    url = "https://api.exa.ai/search"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": Config.EXA_API_KEY,
    }
    payload = {
        "query": query,
        "num_results": num_results,
        "start_published_date": date.today().strftime("%Y-%m-%d"),
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        results = response.json().get("results", [])
        logging.info(f"Received {len(results)} results from Exa API")
        return results
    except requests.RequestException as e:
        logging.error(f"Error searching articles: {str(e)}")
        return []


def filter_relevant_links(articles: list, user_description: str) -> list:
    if not articles:
        return []
    prompt = f"Given the user description: '{user_description}', filter and rank the following articles by relevance. Return only the IDs and URLs of the top 3 most relevant articles:\n\n"
    for article in articles:
        prompt += f"ID: {article.get('id', 'No ID')}\nURL: {article.get('url', 'No URL')}\nTitle: {article.get('title', 'No Title')}\n\n"

    response = send_chat_request(prompt)
    relevant_articles = []
    for line in response.split("\n"):
        if line.startswith("ID:"):
            article_id = line.split(": ")[1].strip()
            url_line = next(
                (l for l in response.split("\n") if l.startswith("URL:")), None
            )
            if url_line:
                url = url_line.split(": ")[1].strip()
                relevant_articles.append({"id": article_id, "url": url})
    return relevant_articles[:3]


def summarize_content(content: str, user_description: str) -> str:
    if not content.strip():
        return "We apologize, but we couldn't find any relevant content for today's podcast. Please try again with a different description of your interests!"
    prompt = f"Summarize the following content into a short podcast script, focusing on the interests described by the user. User description: {user_description}\n\nContent to summarize:\n\n{content}"
    return send_chat_request(prompt)


def generate_podcast(user_description: str, user_id: int):
    logging.info("GENERATING PODCAST")

    try:
        queries = generate_queries(user_description)
        logging.info("Generated queries:")
        for query in queries:
            logging.info(f"- {query}")

        all_articles = []
        for query in queries:
            articles = search_articles(query)
            all_articles.extend(articles)

        relevant_articles = filter_relevant_links(all_articles, user_description)
        logging.info("\nRelevant articles:")
        for article in relevant_articles:
            logging.info(f"- ID: {article['id']}")
            logging.info(f"  URL: {article['url']}")

        content = ""
        for article in relevant_articles:
            logging.info(f'CRAWLING ARTICLE: {article["url"]}')
            try:
                article_content = get_website_text_content(article["url"])
                logging.info(f"Article content preview: {article_content[:200]}...")
                content += f"{article_content}\n\n"
            except Exception as e:
                logging.error(f"Error crawling {article['url']}: {str(e)}")

        logging.info("SUMMARIZING CONTENT")
        script = summarize_content(content, user_description)

        logging.info("FINAL PODCAST SCRIPT:")
        logging.info(script)

        audio_url = text_to_speech(script)

        return {"transcript": script, "audio_url": audio_url, "user_id": user_id}
    except Exception as e:
        logging.error(f"Error generating podcast: {str(e)}")
        return {
            "transcript": "We encountered an error while generating your podcast. Please try again later.",
            "audio_url": "",
            "user_id": user_id,
        }
