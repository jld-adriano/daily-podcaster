import trafilatura
import requests

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    The results is not directly readable, better to be summarized by LLM before consume
    by the user.

    Some common website to crawl information from:
    MLB scores: https://www.mlb.com/scores/YYYY-MM-DD
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            raise ValueError(f"Failed to fetch content from {url}")
        
        text = trafilatura.extract(downloaded)
        if text is None:
            raise ValueError(f"Failed to extract content from {url}")
        
        return text
    except requests.RequestException as e:
        raise ValueError(f"Error fetching content from {url}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing content from {url}: {str(e)}")
