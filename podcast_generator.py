import os
import requests
from config import Config
from web_scraper import get_website_text_content
from anthropic_chat_completion.chat_request import send_chat_request

def search_articles(query):
    print('=' * 50)
    print('SEARCHING ARTICLES')
    print('=' * 50)
    print(f"Searching articles for: {query}")
    url = "https://api.exa.ai/search"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": Config.EXA_API_KEY
    }
    payload = {
        "query": query,
        "num_results": 5,
        "start_published_date": "2023-01-01"
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Full Exa API response:")
    print(response.json())
    print('=' * 50)
    return response.json()['results']

def summarize_content(content):
    prompt = f"Summarize the following content into a short podcast script:\n\n{content}"
    return send_chat_request(prompt)

def generate_podcast(interests):
    print('=' * 50)
    print('GENERATING PODCAST')
    print('=' * 50)
    content = ""
    for interest in interests:
        print(f"Processing interest: {interest}")
        articles = search_articles(interest)
        for article in articles[:2]:  # Limit to 2 articles per interest
            print('=' * 50)
            print('CRAWLING ARTICLE')
            print('=' * 50)
            print(f"Crawling article: {article['url']}")
            article_content = get_website_text_content(article['url'])
            print("Full article content:")
            print(article_content)
            content += f"{article_content}\n\n"

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

    return {
        "transcript": script
    }
