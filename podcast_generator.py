import os
import requests
from config import Config
from web_scraper import get_website_text_content
from anthropic_chat_completion.chat_request import send_chat_request

def generate_queries(user_description: str, num_queries: int = 3) -> list:
    prompt = f"Based on the following user description, generate {num_queries} search queries for finding relevant articles:\n\n{user_description}"
    response = send_chat_request(prompt)
    queries = [query.strip() for query in response.split('\n') if query.strip()]
    return queries[:num_queries]

def search_articles(query: str, num_results: int = 5):
    print('=' * 50)
    print(f'SEARCHING ARTICLES FOR: {query}')
    print('=' * 50)
    url = "https://api.exa.ai/search"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": Config.EXA_API_KEY
    }
    payload = {
        "query": query,
        "num_results": num_results,
        "start_published_date": "2023-01-01"
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Full Exa API response:")
    print(response.json())
    print('=' * 50)
    return response.json().get('results', [])

def filter_relevant_links(articles: list, user_description: str) -> list:
    if not articles:
        return []
    prompt = f"Given the user description: '{user_description}', filter and rank the following articles by relevance. Return only the URLs of the top 3 most relevant articles:\n\n"
    for article in articles:
        prompt += f"Title: {article.get('title', 'No title')}\nURL: {article.get('url', 'No URL')}\nSnippet: {article.get('snippet', 'No snippet available')}\n\n"
    
    response = send_chat_request(prompt)
    relevant_urls = [url.strip() for url in response.split('\n') if url.strip().startswith('http')]
    return relevant_urls[:3]

def summarize_content(content: str) -> str:
    if not content.strip():
        return "We apologize, but we couldn't find any relevant content for today's podcast. Please check back tomorrow for new updates!"
    prompt = f"Summarize the following content into a short podcast script:\n\n{content}"
    return send_chat_request(prompt)

def text_to_speech(text: str) -> str:
    print('=' * 50)
    print('AUDIO GENERATION PLACEHOLDER')
    print('=' * 50)
    return "Audio would be generated here in a full implementation."

def generate_podcast(user_description: str):
    print('=' * 50)
    print('GENERATING PODCAST')
    print('=' * 50)
    
    queries = generate_queries(user_description)
    print("Generated queries:")
    for query in queries:
        print(f"- {query}")
    
    all_articles = []
    for query in queries:
        articles = search_articles(query)
        all_articles.extend(articles)
    
    relevant_urls = filter_relevant_links(all_articles, user_description)
    print("\nRelevant URLs:")
    for url in relevant_urls:
        print(f"- {url}")
    
    content = ""
    for url in relevant_urls:
        print('=' * 50)
        print(f'CRAWLING ARTICLE: {url}')
        print('=' * 50)
        try:
            article_content = get_website_text_content(url)
            print("Full article content:")
            print(article_content[:500] + "...") # Print first 500 characters
            content += f"{article_content}\n\n"
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")

    print('=' * 50)
    print('SUMMARIZING CONTENT')
    print('=' * 50)
    script = summarize_content(content)
    print("Full summarized content:")
    print(script)

    print('=' * 50)
    print('FINAL PODCAST SCRIPT')
    print('=' * 50)
    print(script)

    audio_message = text_to_speech(script)

    return {
        "transcript": script,
        "audio_message": audio_message
    }
