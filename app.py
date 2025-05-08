"""
# Scrape news headlines and links
- Uses `requests`, `BeautifulSoup`, and `urljoin` for scraping and link handling.

## Args:
    - source (str): Default to `'bbc'`.
    Currently supports those sources: `'bbc'`, `'cnn'`, `'fox'`, `'cbs'`
    - max_items (int, optional): Maximum number of items to return
## Example:
> `scrape_news('fox')`
"""

# ## Returns:
#     - list: List of dictionaries containing 'headline' and 'link'
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

source = "bbc"      
max_items = None

# Configuration for different news sources

DEFAULT_MAX_ITEMS = 10
SOURCES_CONFIG = {
    'bbc': {
        'url': 'https://www.bbc.com/news',
        'headline_selector': '[data-testid="card-headline"]',
        'link_selector': 'a[data-testid="internal-link"]',
        'base_url': 'https://www.bbc.com',
        'link_filter': lambda href: href and href.startswith('/news'),
        'max_items': DEFAULT_MAX_ITEMS
    },
    'cnn': {
        'url': 'https://www.cnn.com',
        'headline_selector': '.container__headline',
        'link_selector': 'a.container__link',
        'base_url': 'https://www.cnn.com',
        'link_filter': lambda href: href and not href.startswith('#'),
        'max_items': DEFAULT_MAX_ITEMS
    },
    'fox': {
        'url': 'https://www.foxnews.com',
        'headline_selector': ' h3.title a',
        'link_selector': 'a[href*="/politics/"], a[href*="/us/"], a[href*="/world/"], a[href*="/opinion/"], a[href*="/entertainment/"]',
        'base_url': 'https://www.foxnews.com',
        'link_filter': lambda href: href and (
            href.startswith('/') or 
            href.startswith('https://www.foxnews.com')
        ),
        'max_items': DEFAULT_MAX_ITEMS
    },
    'cbs': {
        'url': 'https://www.cbsnews.com',
        'headline_selector': 'h4.item__hed',
        'link_selector': 'a.item__anchor, a[href*="/news/"], a[href*="/politics/"], a[href*="/world/"]',
        'base_url': 'https://www.cbsnews.com',
        'link_filter': lambda href: href and (
            href.startswith('/') or 
            href.startswith('https://www.cbsnews.com')
        ),
        'max_items': DEFAULT_MAX_ITEMS
    },
    'wsj': {
        'url': 'https://www.wsj.com',
        'headline_selector': '   a',
        'link_selector': 'a.e1sf124z12 css-1rznr30-CardLink',
        'base_url': 'https://www.wsj.com',
        'link_filter': lambda href: href and (
            href.startswith('/') or 
            href.startswith('https://www.wsj.com')
        ),
        'max_items': DEFAULT_MAX_ITEMS
    },
}

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


source = source.lower()
if source not in SOURCES_CONFIG:
    raise ValueError(f"Unsupported news source. Try one of: {', '.join(SOURCES_CONFIG.keys())}")

config = SOURCES_CONFIG[source]
max_items = max_items or config.get('max_items', 15)

try:
    # Fetch the webpage
    response = requests.get(
        config['url'],
        headers=DEFAULT_HEADERS,
        timeout=10
    )
    response.raise_for_status()
    
    # Parse HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract headlines and links
    headlines = []
    seen_urls = set()

    # Find all headline elements
    for element in soup.select(config['headline_selector']):
        # Find the closest parent link or the element itself if it's a link
        link_element = element if element.name == 'a' else element.find_parent('a')
        if not link_element:
            continue
      
        headline_text = element.get_text().strip()
        href = link_element.get('href', '')
        # Skip if no headline text or invalid link
        if not headline_text or not config['link_filter'](href):
            continue
            
        # Build full URL
        full_url = urljoin(config['base_url'], href) if href else None
        
        # Skip duplicates
        if full_url and full_url not in seen_urls:
            seen_urls.add(full_url)
            headlines.append({
                'headline': headline_text,
                'link': full_url
            })
            
            # Stop when we have enough items
            if len(headlines) >= max_items:
                break
            
    """Print the scraped headlines in a formatted way"""
    print(f"\nLatest {source.upper()} News Headlines:")
    for i, item in enumerate(headlines, 1):
        print(f"{i}. {item['headline']}")
        link = world.content.utilities.make_clickable_ansi_link(item['link'],"Link")
        print(f"{link}: {item['link']}\n")
    
except requests.exceptions.RequestException as e:
    raise RuntimeError(f"Failed to fetch news: {str(e)}")
except Exception as e:
    raise RuntimeError(f"An error occurred while scraping: {str(e)}")

print()