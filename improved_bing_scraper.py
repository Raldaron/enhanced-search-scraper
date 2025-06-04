#!/usr/bin/env python
"""
Improved Bing scraper that addresses pagination and bot detection issues
"""
import csv
import os
import time
import random
import requests
import base64
from urllib.parse import quote_plus, urlparse, parse_qs
from bs4 import BeautifulSoup
from datetime import datetime

class ImprovedBingScraper:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.unique_urls = set()

        # List of realistic desktop user agents for Chrome, Firefox, Safari, and Edge
        self.user_agents = [
            # Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36 Edg/122.0",
            # macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:122.0) Gecko/20100101 Firefox/122.0",
            # Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
        ]

        # Initialize with a random header set
        self.update_headers()

    def update_headers(self):
        """Rotate User-Agent and other headers to avoid detection."""
        ua = random.choice(self.user_agents)

        # Determine Accept header based on browser
        if "Firefox" in ua:
            accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        elif "Safari" in ua and "Chrome" not in ua:
            accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        else:
            accept = (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7"
            )

        accept_languages = [
            "en-US,en;q=0.9",
            "en-GB,en;q=0.8",
            "en-US,en;q=0.8,en-GB;q=0.7",
            "en-US;q=0.7,en;q=0.3",
        ]

        headers = {
            "User-Agent": ua,
            "Accept": accept,
            "Accept-Language": random.choice(accept_languages),
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }

        if "Chrome" in ua or "Edg" in ua:
            platform = (
                '"Windows"' if "Windows" in ua else '"macOS"' if "Macintosh" in ua else '"Linux"'
            )
            if "Edg" in ua:
                headers["sec-ch-ua"] = '"Not.A/Brand";v="8", "Chromium";v="122", "Microsoft Edge";v="122"'
            else:
                headers["sec-ch-ua"] = '"Not_A Brand";v="8", "Chromium";v="122", "Google Chrome";v="122"'
            headers["sec-ch-ua-mobile"] = "?0"
            headers["sec-ch-ua-platform"] = platform

        self.session.headers.clear()
        self.session.headers.update(headers)

    def get_random_delay(self, min_delay=2, max_delay=5):
        """Generate random delay between requests with slight variance"""
        return random.uniform(min_delay, max_delay) + random.random() * 0.5
        
    def search_bing(self, query, max_pages=10, delay_range=(2, 5)):
        """Search Bing with proper pagination handling"""
        print(f"Starting Bing search for: '{query}'")
        
        base_url = "https://www.bing.com/search"
        encoded_query = quote_plus(query)
        
        for page in range(max_pages):
            # Calculate the offset for this page (Bing uses 'first' parameter)
            offset = page * 10  # Bing shows 10 results per page by default
            
            # Build URL with proper pagination
            if page == 0:
                url = f"{base_url}?q={encoded_query}&FORM=QBRE"
            else:
                url = f"{base_url}?q={encoded_query}&first={offset}&FORM=PERE"
            
            print(f"\nPage {page + 1}: {url}")
            
            try:
                # Add some randomness to avoid detection
                time.sleep(self.get_random_delay(*delay_range))

                # Rotate headers for each request
                self.update_headers()

                # Make request
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                print(f"Response status: {response.status_code}")
                print(f"Response size: {len(response.text)} chars")
                
                # Parse results
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find search result items
                result_items = soup.select('li.b_algo')
                print(f"Found {len(result_items)} result items")
                
                if not result_items:
                    print("No more results found, ending search")
                    break
                
                page_results = []
                for item in result_items:
                    result = self.extract_result(item, page + 1)
                    if result and result['url'] not in self.unique_urls:
                        self.unique_urls.add(result['url'])
                        page_results.append(result)
                        self.results.append(result)
                
                print(f"Extracted {len(page_results)} new unique results")
                
                # Check if we found any easyapply.co results
                easyapply_results = [r for r in page_results if 'easyapply.co' in r['url']]
                if easyapply_results:
                    print(f"Found {len(easyapply_results)} easyapply.co results on this page!")
                    for result in easyapply_results:
                        print(f"  - {result['url']}")
                
                # Check if this looks like we've hit the end or are getting repeats
                if not page_results:
                    print("No new unique results on this page, stopping")
                    break
                    
                # Look for "Next" link to see if more pages are available
                next_link = soup.select_one('a.sb_pagN')
                if not next_link and page > 0:
                    print("No 'Next' button found, reached end of results")
                    break
                    
            except requests.RequestException as e:
                print(f"Request failed on page {page + 1}: {e}")
                break
            except Exception as e:
                print(f"Error processing page {page + 1}: {e}")
                import traceback
                traceback.print_exc()
                break
        
        return self.results
    
    def extract_result(self, item, page_num):
        """Extract search result data from a BeautifulSoup element with fallbacks."""
        try:
            link_element = None
            for selector in ['h2 a[href]', 'h3 a[href]', 'a[href]']:
                link_element = item.select_one(selector)
                if link_element and link_element.get('href'):
                    break

            if not link_element:
                return None

            url = link_element.get('href', '').strip()
            title = link_element.get_text(strip=True)

            if url.startswith('/'):
                url = 'https://www.bing.com' + url

            try:
                parsed = urlparse(url)
                query_params = parse_qs(parsed.query)
                if 'u' in query_params and query_params['u']:
                    encoded = query_params['u'][0]
                    if encoded.startswith('a1'):
                        encoded = encoded[2:]
                    encoded += '=' * (len(encoded) % 4)
                    url = base64.b64decode(encoded).decode('utf-8')
            except Exception as e:
                print(f"Error decoding Base64 URL '{url}': {e}")

            description = ''
            for selector in ['.b_caption p', '.b_snippetBigText', '.b_algoSlug', 'p']:
                desc_elem = item.select_one(selector)
                if desc_elem and desc_elem.get_text(strip=True):
                    description = desc_elem.get_text(strip=True)
                    break

            try:
                domain = urlparse(url).netloc
            except Exception:
                domain = ''

            return {
                'url': url,
                'title': title,
                'description': description,
                'domain': domain,
                'page': page_num
            }

        except Exception as e:
            print(f"Error extracting result: {e}")
            return None
    
    def save_to_csv(self, filename):
        """Save results to CSV file"""
        if not self.results:
            print("No results to save")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'title', 'description', 'domain', 'page']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)
        
        print(f"Saved {len(self.results)} results to {filename}")
        
        # Show summary
        easyapply_results = [r for r in self.results if 'easyapply.co' in r['url']]
        if easyapply_results:
            print(f"\nFound {len(easyapply_results)} easyapply.co results:")
            for result in easyapply_results:
                print(f"  - {result['url']}")
        else:
            print("No easyapply.co results found")

def main():
    """Run the improved scraper with multiple strategies"""
    scraper = ImprovedBingScraper()
    
    # Test different search strategies
    strategies = [
        "site:easyapply.co",
        "easyapply.co",
        '"easyapply.co"',
        "easyapply.co jobs",
        "easyapply.co careers",
        "inurl:easyapply.co",
        "easyapply.co hiring",
        "easyapply.co application"
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, query in enumerate(strategies, 1):
        print(f"\n{'='*60}")
        print(f"STRATEGY {i}: {query}")
        print(f"{'='*60}")
        
        # Reset for each strategy
        strategy_scraper = ImprovedBingScraper()
        
        try:
            results = strategy_scraper.search_bing(query, max_pages=5, delay_range=(3, 7))
            
            # Save results for this strategy
            filename = f"improved_bing_strategy_{i:02d}_{timestamp}.csv"
            strategy_scraper.save_to_csv(filename)
            
            print(f"\nStrategy {i} completed: {len(results)} total results")
            
        except KeyboardInterrupt:
            print("\nScraping interrupted by user")
            break
        except Exception as e:
            print(f"Error in strategy {i}: {e}")
            continue
    
    print("\nAll strategies completed!")

if __name__ == "__main__":
    main()
