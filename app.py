from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
import re
import time
import logging
import os
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

app = FastAPI(title="TikTok Collection Scraper", version="1.0.0")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, consider restricting to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CollectionRequest(BaseModel):
    url: str


class CollectionResponse(BaseModel):
    collection_name: str
    owner: str
    posts: List[str]


def extract_collection_data(url: str) -> dict:
    """
    Scrapes TikTok collection page to extract collection name, owner, and post URLs.
    """
    logger.info("Initializing Playwright...")
    with sync_playwright() as p:
        logger.info("Playwright context manager started")
        # Launch browser in headless mode
        logger.info("Launching Chromium browser...")
        browser = p.chromium.launch(headless=True)
        logger.info("Browser launched successfully")
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        logger.info("New page created")
        
        try:
            # Navigate to the collection URL
            logger.info(f"Navigating to: {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)  # Allow time for dynamic content to load
            
            # Extract owner from URL (most reliable method)
            owner = ""
            url_match = re.search(r'@([^/]+)', url)
            if url_match:
                owner = url_match.group(1)
            else:
                raise ValueError("Could not extract owner from collection URL")
            
            # Extract collection name
            collection_name = ""
            try:
                # Try multiple selectors for collection name
                name_selectors = [
                    'h1[data-e2e="collection-name"]',
                    'h1[data-e2e="collection-title"]',
                    '[data-e2e="collection-name"]',
                    '[data-e2e="collection-title"]',
                    'h1',
                    '.collection-title',
                    '[class*="collection"][class*="title"]'
                ]
                
                for selector in name_selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            text = element.inner_text().strip()
                            if text and len(text) > 0:
                                collection_name = text
                                break
                    except:
                        continue
                
                # If still not found, try getting from page title or URL
                if not collection_name:
                    title = page.title()
                    if title and 'TikTok' not in title:
                        collection_name = title
            except Exception as e:
                logger.warning(f"Error extracting collection name: {e}")
            
            if not collection_name:
                collection_name = "Untitled Collection"
            
            # Extract post URLs - scroll to load all content
            post_urls = []
            seen_urls = set()
            last_height = 0
            scroll_attempts = 0
            max_scrolls = 10
            
            try:
                # Scroll and collect URLs
                while scroll_attempts < max_scrolls:
                    # Find all video links on current page
                    links = page.query_selector_all('a[href*="/video/"]')
                    
                    for link in links:
                        try:
                            href = link.get_attribute('href')
                            if href:
                                # Normalize URL
                                if href.startswith('/'):
                                    full_url = f"https://www.tiktok.com{href}"
                                elif href.startswith('http'):
                                    full_url = href
                                else:
                                    continue
                                
                                # Clean up URL (remove query parameters that aren't video ID)
                                if '/video/' in full_url:
                                    # Extract clean URL (username/video/id)
                                    url_parts = full_url.split('/video/')
                                    if len(url_parts) == 2:
                                        video_id = url_parts[1].split('?')[0].split('#')[0]
                                        clean_url = f"https://www.tiktok.com/@{owner}/video/{video_id}"
                                    else:
                                        clean_url = full_url.split('?')[0].split('#')[0]
                                    
                                    if clean_url not in seen_urls:
                                        seen_urls.add(clean_url)
                                        post_urls.append(clean_url)
                        except Exception as e:
                            continue
                    
                    # Scroll down
                    current_height = page.evaluate("document.body.scrollHeight")
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2)
                    
                    # Check if we've reached the bottom
                    new_height = page.evaluate("document.body.scrollHeight")
                    if new_height == last_height:
                        scroll_attempts += 1
                    else:
                        scroll_attempts = 0
                    last_height = new_height
                
                # Also try alternative selectors for collection items
                if not post_urls:
                    items = page.query_selector_all('[data-e2e*="video"], [data-e2e*="item"]')
                    for item in items:
                        try:
                            link = item.query_selector('a')
                            if link:
                                href = link.get_attribute('href')
                                if href and '/video/' in href:
                                    if href.startswith('/'):
                                        full_url = f"https://www.tiktok.com{href}"
                                    else:
                                        full_url = href
                                    clean_url = full_url.split('?')[0].split('#')[0]
                                    if clean_url not in seen_urls:
                                        seen_urls.add(clean_url)
                                        post_urls.append(clean_url)
                        except:
                            continue
                
            except Exception as e:
                logger.error(f"Error extracting post URLs: {e}")
            
            browser.close()
            
            return {
                "collection_name": collection_name,
                "owner": owner,
                "posts": post_urls
            }
            
        except Exception as e:
            browser.close()
            raise Exception(f"Error scraping TikTok collection: {str(e)}")


@app.get("/")
def read_root():
    return {"message": "TikTok Collection Scraper API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring and keep-alive pings"""
    return {"status": "healthy", "service": "TikTok Collection Scraper API"}


@app.post("/scrape-collection", response_model=CollectionResponse)
def scrape_collection(request: CollectionRequest):
    """
    Scrapes a TikTok collection URL and returns collection name, owner, and post URLs.
    """
    url = request.url
    logger.info(f"Received scrape request for URL: {url}")
    
    # Validate URL
    if not url.startswith('https://www.tiktok.com/@'):
        logger.warning(f"Invalid URL format: {url}")
        raise HTTPException(status_code=400, detail="Invalid TikTok collection URL format")
    
    if '/collection/' not in url:
        logger.warning(f"URL is not a collection: {url}")
        raise HTTPException(status_code=400, detail="URL must be a TikTok collection URL")
    
    try:
        logger.info(f"Starting to extract collection data from: {url}")
        data = extract_collection_data(url)
        logger.info(f"Successfully extracted data: {len(data.get('posts', []))} posts found")
        return CollectionResponse(**data)
    except ValueError as e:
        logger.error(f"ValueError during scraping: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Exception during scraping: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to scrape collection: {str(e)}")


@app.get("/scrape-collection")
def scrape_collection_get(url: str):
    """
    GET endpoint version for scraping TikTok collections.
    Usage: /scrape-collection?url=<tiktok_collection_url>
    """
    if not url.startswith('https://www.tiktok.com/@'):
        raise HTTPException(status_code=400, detail="Invalid TikTok collection URL format")
    
    if '/collection/' not in url:
        raise HTTPException(status_code=400, detail="URL must be a TikTok collection URL")
    
    try:
        data = extract_collection_data(url)
        return CollectionResponse(**data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scrape collection: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

