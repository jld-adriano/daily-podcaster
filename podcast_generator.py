import os
import requests
from datetime import date, datetime, timedelta
from email import message_from_file
from config import Config
from web_scraper import get_website_text_content
from anthropic_chat_completion.chat_request import send_chat_request

# Simple cache to store API responses
cache = {}
CACHE_EXPIRY = timedelta(hours=1)

def process_emails():
    email_folder = 'emails'
    email_content = []
    if not os.path.exists(email_folder):
        print(f"Warning: {email_folder} directory not found.")
        return ""
    
    for filename in os.listdir(email_folder):
        if filename.endswith('.eml'):
            try:
                with open(os.path.join(email_folder, filename), 'r', encoding='utf-8') as f:
                    email = message_from_file(f)
                    subject = email['subject']
                    body = email.get_payload()
                    email_content.append(f"Subject: {subject}\nBody: {body}")
                    print(f"Successfully processed email: {filename}")
            except Exception as e:
                print(f"Error processing email {filename}: {str(e)}")
    
    if not email_content:
        print("No valid emails found in the directory.")
        return ""
    
    combined_content = '\n\n'.join(email_content)
    print(f"Processed {len(email_content)} emails. Content preview: {combined_content[:100]}...")
    return combined_content

def generate_queries(user_description: str, email_content: str, num_queries: int = 3) -> list:
    prompt = f"Based on the following user description and recent email content, generate {num_queries} search queries for finding relevant articles:\n\nUser description: {user_description}\n\nRecent email content:\n{email_content}"
    response = send_chat_request(prompt)
    queries = [query.strip() for query in response.split('\n') if query.strip()]
    return queries[:num_queries]

def search_articles(query: str, num_results: int = 5):
    print(f'SEARCHING ARTICLES FOR: {query}')
    cache_key = f"{query}_{num_results}_{date.today().isoformat()}"
    
    if cache_key in cache and datetime.now() - cache[cache_key]['timestamp'] < CACHE_EXPIRY:
        print("Using cached results")
        return cache[cache_key]['results']
    
    url = "https://api.exa.ai/search"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": Config.EXA_API_KEY
    }
    payload = {
        "query": query,
        "num_results": num_results,
        "start_published_date": date.today().strftime("%Y-%m-%d")
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        results = response.json().get('results', [])
        cache[cache_key] = {'results': results, 'timestamp': datetime.now()}
        return results
    except requests.RequestException as e:
        print(f"Error searching articles: {str(e)}")
        return []

def filter_relevant_links(articles: list, user_description: str) -> list:
    if not articles:
        return []
    prompt = f"Given the user description: '{user_description}', filter and rank the following articles by relevance. Return only the IDs and URLs of the top 3 most relevant articles:\n\n"
    for article in articles:
        prompt += f"ID: {article.get('id', 'No ID')}\nURL: {article.get('url', 'No URL')}\nTitle: {article.get('title', 'No Title')}\n\n"
    
    response = send_chat_request(prompt)
    relevant_articles = []
    for line in response.split('\n'):
        if line.startswith('ID:'):
            article_id = line.split(': ')[1].strip()
            url_line = next((l for l in response.split('\n') if l.startswith('URL:')), None)
            if url_line:
                url = url_line.split(': ')[1].strip()
                relevant_articles.append({'id': article_id, 'url': url})
    return relevant_articles[:3]

def summarize_content(content: str) -> str:
    if not content.strip():
        return "We apologize, but we couldn't find any relevant content for today's podcast. Please check back tomorrow for new updates!"
    prompt = f"Summarize the following content into a short podcast script, focusing on the latest tech gadgets and sports news. Make sure to include specific details and keep it engaging:\n\n{content}"
    return send_chat_request(prompt)

def text_to_speech(text: str) -> str:
    print('AUDIO GENERATION PLACEHOLDER')
    return "Audio would be generated here in a full implementation."

def generate_podcast(user_description: str):
    print('GENERATING PODCAST')
    
    try:
        email_content = process_emails()
        queries = generate_queries(user_description, email_content)
        print("Generated queries:")
        for query in queries:
            print(f"- {query}")
        
        all_articles = []
        for query in queries:
            articles = search_articles(query)
            all_articles.extend(articles)
        
        relevant_articles = filter_relevant_links(all_articles, user_description)
        print("\nRelevant articles:")
        for article in relevant_articles:
            print(f"- ID: {article['id']}")
            print(f"  URL: {article['url']}")
        
        content = ""
        for article in relevant_articles:
            print(f'CRAWLING ARTICLE: {article["url"]}')
            try:
                article_content = get_website_text_content(article['url'])
                print(f"Article content preview: {article_content[:200]}...")
                content += f"{article_content}\n\n"
            except Exception as e:
                print(f"Error crawling {article['url']}: {str(e)}")
        
        print('SUMMARIZING CONTENT')
        script = summarize_content(content)
        
        print("FINAL PODCAST SCRIPT:")
        print(script)

        audio_message = text_to_speech(script)

        return {
            "transcript": script,
            "audio_message": audio_message
        }
    except Exception as e:
        print(f"Error generating podcast: {str(e)}")
        return {
            "transcript": "We encountered an error while generating your podcast. Please try again later.",
            "audio_message": "Error generating audio."
        }
