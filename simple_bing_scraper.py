#!/usr/bin/env python3
# Simple Bing scraper for easyapply.co using different search strategies

import argparse
import csv
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
import random

class SimpleBingScraper:
    def __init__(self, delay_range=(1, 3)):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay_range = delay_range
        self.results = []
        self.unique_urls = set()
        
    def search_bing(self, query, max_pages=50):
        """Search Bing and collect all results"""
        print(f"Searching Bing for: {query}")
        
        base_url = "https://www.bing.com/search"
        results_per_page = 10
        
        for page in range(0, max_pages):
            first_result = page * results_per_page + 1
            params = {
                'q': query,
                'first': first_result if page > 0 else None
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            try:
                print(f"\nPage {page + 1} - Starting from result {first_result}")
                response = self.session.get(base_url, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find search results
                results = soup.find_all('li', class_='b_algo')
                
                if not results:
                    print(f"No results found on page {page + 1}")
                    break
                
                page_results = []
                for result in results:
                    try:
                        # Extract title
                        title_elem = result.find('h2')
                        title = title_elem.get_text(strip=True) if title_elem else "No title"
                        
                        # Extract URL
                        link_elem = title_elem.find('a') if title_elem else None
                        url = link_elem.get('href') if link_elem else "No URL"
                          # Extract snippet
                        snippet_elem = result.find('p') or result.find('div', {'class': 'b_caption'})
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No snippet"
                        
                        # Filter for easyapply.co URLs
                        if url and 'easyapply.co' in str(url).lower():
                            if url not in self.unique_urls:
                                self.unique_urls.add(url)
                                result_data = {
                                    'title': title,
                                    'url': url,
                                    'snippet': snippet,
                                    'query': query,
                                    'page': page + 1
                                }
                                page_results.append(result_data)
                                self.results.append(result_data)
                    
                    except Exception as e:
                        print(f"Error parsing result: {e}")
                        continue
                
                print(f"Found {len(page_results)} new easyapply.co URLs on page {page + 1}")
                print(f"Total unique easyapply.co URLs so far: {len(self.results)}")
                
                # Check if we should continue
                if len(results) < results_per_page:
                    print("Reached end of results (fewer than 10 results on page)")
                    break
                
                # Delay between requests
                if page < max_pages - 1:
                    delay = random.uniform(*self.delay_range)
                    print(f"Waiting {delay:.1f} seconds...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"Error on page {page + 1}: {e}")
                break
        
        return self.results
    
    def save_to_csv(self, filename):
        """Save results to CSV"""
        if not self.results:
            print("No results to save")
            return
            
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'url', 'snippet', 'query', 'page']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
        
        print(f"\nSaved {len(self.results)} results to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Simple Bing scraper for easyapply.co')
    parser.add_argument('--query', default='easyapply.co', help='Search query')
    parser.add_argument('--pages', type=int, default=50, help='Maximum pages to scrape')
    parser.add_argument('--output', default='bing_easyapply_results.csv', help='Output CSV file')
    parser.add_argument('--delay', type=float, nargs=2, default=[1, 3], help='Delay range between requests')
    
    args = parser.parse_args()
    
    scraper = SimpleBingScraper(delay_range=args.delay)
    
    # Try multiple search strategies
    search_queries = [
        args.query,
        f'"{args.query}"',
        f'site:{args.query}',
        f'{args.query} jobs',
        f'{args.query} careers',
        f'inurl:{args.query}'
    ]
    
    all_results = []
    
    for i, query in enumerate(search_queries, 1):
        print(f"\n{'='*60}")
        print(f"SEARCH STRATEGY {i}/{len(search_queries)}: {query}")
        print(f"{'='*60}")
        
        scraper = SimpleBingScraper(delay_range=args.delay)
        results = scraper.search_bing(query, args.pages)
        
        if results:
            # Save intermediate results
            intermediate_file = f"{args.output.replace('.csv', '')}_{i:02d}_{query.replace(':', '_').replace(' ', '_').replace('"', '')}.csv"
            scraper.save_to_csv(intermediate_file)
            all_results.extend(results)
        
        # Wait between search strategies
        if i < len(search_queries):
            print(f"\nWaiting 30 seconds before next search strategy...")
            time.sleep(30)
    
    # Save combined results
    if all_results:
        # Remove duplicates based on URL
        unique_results = []
        seen_urls = set()
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        final_filename = f"{args.output.replace('.csv', '')}_combined.csv"
        with open(final_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'url', 'snippet', 'query', 'page']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unique_results)
        
        print(f"\n{'='*60}")
        print(f"FINAL RESULTS")
        print(f"{'='*60}")
        print(f"Total results collected: {len(all_results)}")
        print(f"Unique URLs: {len(unique_results)}")
        print(f"Combined results saved to: {final_filename}")

if __name__ == '__main__':
    main()
