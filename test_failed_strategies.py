#!/usr/bin/env python3
"""
Test the previously failed search strategies with the fixed Bing library
"""
import csv
import os
import time
from datetime import datetime

try:
    from search_engines import Bing
except ImportError as e:
    print(f"Error importing search_engines: {e}")
    exit(1)

def test_search_strategy(query, strategy_num, max_pages=5):
    """Test a single search strategy"""
    print(f"\n=== Strategy {strategy_num}: Testing '{query}' ===")
    
    csv_filename = f"bing_easyapply_{strategy_num:02d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        # Initialize Bing search engine
        engine = Bing()
        results = []
        unique_urls = set()
        
        # Setup CSV file
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            headers = ['query', 'engine', 'domain', 'URL', 'title', 'text', 'page_found']
            csv_writer.writerow(headers)
            
            print(f"Searching for: {query}")
            
            for page_num in range(1, max_pages + 1):
                print(f"  Searching page {page_num}...")
                
                try:
                    # Search current page
                    page_results = engine.search(query, pages=1)
                    
                    if not page_results:
                        print(f"  No results found on page {page_num}")
                        break
                    
                    page_count = 0
                    for result in page_results:
                        url = result.get('link', '')
                        if url and url not in unique_urls and 'easyapply.co' in url.lower():
                            unique_urls.add(url)
                            row = [
                                query,
                                'Bing',
                                result.get('host', ''),
                                url,
                                result.get('title', ''),
                                result.get('text', ''),
                                page_num
                            ]
                            csv_writer.writerow(row)
                            page_count += 1
                            results.append(result)
                    
                    print(f"  Found {page_count} new easyapply.co URLs on page {page_num}")
                    
                    if page_count == 0 and page_num > 1:
                        print(f"  No new results, stopping search")
                        break
                        
                    # Add delay between pages
                    if page_num < max_pages:
                        time.sleep(2)
                        
                except Exception as e:
                    print(f"  Error on page {page_num}: {e}")
                    break
        
        print(f"Strategy {strategy_num} completed: {len(unique_urls)} unique URLs found")
        if unique_urls:
            print("URLs found:")
            for url in sorted(unique_urls):
                print(f"  - {url}")
        print(f"Results saved to: {csv_filename}")
        
        return len(unique_urls), csv_filename
        
    except Exception as e:
        print(f"Strategy {strategy_num} failed: {e}")
        return 0, csv_filename

def main():
    """Test the previously failed strategies"""
    print("Testing previously failed search strategies with fixed Bing library")
    print("=" * 60)
    
    # These are the strategies that failed before due to Base64 decoding errors
    failed_strategies = [
        (3, "site:easyapply.co jobs"),
        (4, "site:easyapply.co hiring"),  
        (6, "site:easyapply.co apply"),
        (7, "site:easyapply.co employment")
    ]
    
    total_found = 0
    csv_files = []
    
    for strategy_num, query in failed_strategies:
        found, csv_file = test_search_strategy(query, strategy_num, max_pages=10)
        total_found += found
        if found > 0:
            csv_files.append(csv_file)
        
        # Delay between strategies to be respectful
        time.sleep(3)
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: Found {total_found} total unique URLs across all failed strategies")
    if csv_files:
        print(f"CSV files created: {len(csv_files)}")
        for csv_file in csv_files:
            print(f"  - {csv_file}")
    else:
        print("No results found in any strategy")

if __name__ == "__main__":
    main()
