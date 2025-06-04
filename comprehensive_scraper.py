# Enhanced scraper with multiple search strategies
import argparse
import csv
import os
import time
from pathlib import Path

try:
    from search_engines.engines import search_engines_dict
    from search_engines import config
    from search_engines import output as out
except ImportError as e:
    msg = '"{}"\nPlease install `search_engines` to resolve this error.'
    raise ImportError(msg.format(str(e)))


class EnhancedSearchEngine:
    def __init__(self, engine_class, proxy=None, timeout=None):
        self.engine = engine_class(proxy, timeout)
        self.csv_file = None
        self.csv_writer = None
        self.csv_path = None
        self.results_count = 0
        self.unique_urls = set()
        
    def setup_csv(self, filename):
        """Initialize CSV file with headers"""
        self.csv_path = filename
        file_exists = os.path.exists(filename)
        
        self.csv_file = open(filename, 'a', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)
        
        if not file_exists:
            headers = ['search_query', 'engine', 'domain', 'URL', 'title', 'text', 'page_found']
            self.csv_writer.writerow(headers)
            self.csv_file.flush()
            print(f"Created CSV file: {filename}")
        else:
            print(f"Appending to existing CSV file: {filename}")
    
    def save_page_results(self, page_results, page_num, query):
        """Save results from current page to CSV"""
        if not self.csv_writer:
            return
            
        new_results = 0
        for result in page_results:
            # Check if this URL is truly unique
            url = result['link']
            if url not in self.unique_urls:
                self.unique_urls.add(url)
                row = [
                    query,
                    self.engine.__class__.__name__,
                    result['host'],
                    result['link'],
                    result['title'],
                    result['text'],
                    page_num
                ]
                self.csv_writer.writerow(row)
                new_results += 1
                self.results_count += 1
        
        self.csv_file.flush()
        
        if new_results > 0:
            print(f"Page {page_num}: Saved {new_results} new unique results (Total unique: {self.results_count})")
        else:
            print(f"Page {page_num}: No new unique results found")
    
    def search_with_strategy(self, query, pages, csv_filename):
        """Enhanced search with better debugging"""
        from time import sleep
        from random import uniform as random_uniform
        from bs4 import BeautifulSoup
        from search_engines import utils
        from search_engines.results import SearchResults
        
        self.setup_csv(csv_filename)
        
        print(f'Searching {self.engine.__class__.__name__} for: "{query}"')
        self.engine._query = utils.decode_bytes(query)
        self.engine.results = SearchResults()
        
        try:
            request = self.engine._first_page()
            print(f"Starting URL: {request['url']}")
        except Exception as e:
            print(f"Error getting first page: {e}")
            return self.engine.results

        successful_pages = 0
        for page in range(1, pages + 1):
            try:
                print(f"\n--- Processing page {page} ---")
                print(f"Request URL: {request['url']}")
                
                response = self.engine._get_page(request['url'], request['data'])
                
                if not self.engine._is_ok(response):
                    print(f"Failed to get page {page} (HTTP status issue), stopping search")
                    break
                
                print(f"Response received, length: {len(response.html)} chars")
                
                tags = BeautifulSoup(response.html, "html.parser")
                items = self.engine._filter_results(tags)
                print(f"Found {len(items)} result items on page")
                
                # Store results before collecting them
                old_results_count = len(self.engine.results)
                self.engine._collect_results(items)
                new_results_count = len(self.engine.results)
                
                # Get only the new results from this page
                page_results = self.engine.results[old_results_count:new_results_count]
                print(f"Added {len(page_results)} results to collection")
                
                # Save this page's results to CSV
                self.save_page_results(page_results, page, query)
                
                successful_pages += 1
                
                # Get next page URL
                request = self.engine._next_page(tags)
                print(f"Next page URL: {request['url'] if request['url'] else 'None (end of results)'}")
                
                if not request['url']:
                    print("No more pages available - reached end of results")
                    break
                    
                if page < pages:
                    delay = random_uniform(*self.engine._delay)
                    print(f"Waiting {delay:.1f} seconds before next page...")
                    sleep(delay)
                    
            except KeyboardInterrupt:
                print("\nSearch interrupted by user")
                break
            except Exception as e:
                print(f"Error on page {page}: {e}")
                import traceback
                traceback.print_exc()
                break
        
        print(f"\nProcessed {successful_pages} pages successfully")
        self.cleanup()
        return self.engine.results
    
    def cleanup(self):
        """Close CSV file"""
        if self.csv_file:
            self.csv_file.close()
            print(f"Results saved to: {self.csv_path}")
            print(f"Total unique results saved: {self.results_count}")


def run_multiple_searches(engine_name, base_filename):
    """Run multiple search variations to get more comprehensive results"""
    
    search_queries = [
        "site:easyapply.co",
        "site:*.easyapply.co",
        '"easyapply.co"',
        "easyapply.co",
        "easyapply.co jobs",
        "easyapply.co careers",
        "easyapply.co application",
        "easyapply.co apply",
        "easyapply.co hiring",
        "inurl:easyapply.co"
    ]
    
    proxy = config.PROXY
    timeout = config.TIMEOUT + (10 * bool(proxy))
    engine_class = search_engines_dict[engine_name.lower()]
    
    for i, query in enumerate(search_queries, 1):
        print(f"\n{'='*60}")
        print(f"SEARCH STRATEGY {i}/{len(search_queries)}: {query}")
        print(f"{'='*60}")
        
        # Create filename with query identifier  
        safe_query = query.replace('"', '').replace(':', '_').replace('*', 'wildcard').replace(' ', '_')
        filename = f"{base_filename}_{i:02d}_{safe_query}.csv"
        
        engine = EnhancedSearchEngine(engine_class, proxy, timeout)
        
        try:
            results = engine.search_with_strategy(query, 50, filename)  # 50 pages per query
            print(f"Strategy {i} completed: {len(results)} total results")
            
            # Wait between different search strategies
            if i < len(search_queries):
                wait_time = 30  # 30 seconds between different search terms
                print(f"Waiting {wait_time} seconds before next search strategy...")
                time.sleep(wait_time)
                
        except Exception as e:
            print(f"Error in search strategy {i}: {e}")
            engine.cleanup()
            continue


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-e', help='search engine - ' + ', '.join(search_engines_dict) + ' (default: "bing")', default='bing')
    ap.add_argument('-f', help='base filename for CSV files', default='easyapply_comprehensive')
    
    args = ap.parse_args()
    
    if args.e.lower() not in search_engines_dict:
        print('Please choose a search engine: ' + ', '.join(search_engines_dict))
        return
    
    print("Starting comprehensive EasyApply.co search...")
    print(f"Engine: {args.e}")
    print(f"Base filename: {args.f}")
    
    run_multiple_searches(args.e, args.f)
    
    print("\n" + "="*60)
    print("COMPREHENSIVE SEARCH COMPLETED")
    print("="*60)
    print("Check the generated CSV files for results from different search strategies.")


if __name__ == '__main__':
    main()
