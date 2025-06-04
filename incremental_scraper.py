# -*- encoding: utf-8 -*-
import argparse
import csv
import os
from pathlib import Path

try:
    from search_engines.engines import search_engines_dict
    from search_engines.multiple_search_engines import MultipleSearchEngines, AllSearchEngines
    from search_engines import config
    from search_engines import output as out
except ImportError as e:
    msg = '"{}"\nPlease install `search_engines` to resolve this error.'
    raise ImportError(msg.format(str(e)))


class IncrementalSearchEngine:
    def __init__(self, engine_class, proxy=None, timeout=None):
        self.engine = engine_class(proxy, timeout)
        self.csv_file = None
        self.csv_writer = None
        self.csv_path = None
        self.results_count = 0
        
    def setup_csv(self, filename):
        """Initialize CSV file with headers"""
        self.csv_path = filename
        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(filename)
        
        self.csv_file = open(filename, 'a', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)
        
        # Write headers if file is new
        if not file_exists:
            headers = ['query', 'engine', 'domain', 'URL', 'title', 'text']
            self.csv_writer.writerow(headers)
            self.csv_file.flush()
            print(f"Created CSV file: {filename}")
        else:
            print(f"Appending to existing CSV file: {filename}")
    
    def save_page_results(self, page_results, page_num):
        """Save results from current page to CSV"""
        if not self.csv_writer:
            return
            
        new_results = 0
        for result in page_results:
            row = [
                self.engine._query,
                self.engine.__class__.__name__,
                result['host'],
                result['link'],
                result['title'],
                result['text']
            ]
            self.csv_writer.writerow(row)
            new_results += 1
            self.results_count += 1
        
        # Flush to ensure data is written immediately
        self.csv_file.flush()
        
        if new_results > 0:
            print(f"Page {page_num}: Saved {new_results} new results (Total: {self.results_count})")
        else:
            print(f"Page {page_num}: No new results found")
    
    def search_incremental(self, query, pages, csv_filename):
        """Modified search that saves after each page"""
        from time import sleep
        from random import uniform as random_uniform
        from bs4 import BeautifulSoup
        from search_engines import utils
        from search_engines.results import SearchResults
        
        # Setup CSV file
        self.setup_csv(csv_filename)
        
        print(f'Searching {self.engine.__class__.__name__} incrementally')
        self.engine._query = utils.decode_bytes(query)
        self.engine.results = SearchResults()
        request = self.engine._first_page()

        for page in range(1, pages + 1):
            try:
                print(f"\nProcessing page {page}...")
                response = self.engine._get_page(request['url'], request['data'])
                
                if not self.engine._is_ok(response):
                    print(f"Failed to get page {page}, stopping search")
                    break
                    
                tags = BeautifulSoup(response.html, "html.parser")
                items = self.engine._filter_results(tags)
                
                # Store results before collecting them
                old_results_count = len(self.engine.results)
                self.engine._collect_results(items)
                new_results_count = len(self.engine.results)
                
                # Get only the new results from this page
                page_results = self.engine.results[old_results_count:new_results_count]
                
                # Save this page's results to CSV
                self.save_page_results(page_results, page)
                
                msg = 'page: {:<8} total links: {}'.format(page, len(self.engine.results))
                print(msg)
                
                request = self.engine._next_page(tags)
                if not request['url']:
                    print("No more pages available")
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
                break
        
        self.cleanup()
        return self.engine.results
    
    def cleanup(self):
        """Close CSV file"""
        if self.csv_file:
            self.csv_file.close()
            print(f"\nSearch completed. Results saved to: {self.csv_path}")
            print(f"Total results saved: {self.results_count}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-q', help='query (required)', required=True)
    ap.add_argument('-e', help='search engine - ' + ', '.join(search_engines_dict) + ' (default: "bing")', default='bing')
    ap.add_argument('-p', help='number of pages', default=200, type=int)
    ap.add_argument('-f', help='CSV filename', default='incremental_results.csv')
    ap.add_argument('-proxy', help='use proxy (protocol://ip:port)', default=config.PROXY)
    
    args = ap.parse_args()

    proxy = args.proxy
    timeout = config.TIMEOUT + (10 * bool(proxy))
    
    if args.e.lower() not in search_engines_dict:
        print('Please choose a search engine: ' + ', '.join(search_engines_dict))
        return
    
    engine_class = search_engines_dict[args.e.lower()]
    incremental_engine = IncrementalSearchEngine(engine_class, proxy, timeout)
    
    try:
        results = incremental_engine.search_incremental(args.q, args.p, args.f)
        print(f"\nFinal summary:")
        print(f"Total unique results found: {len(results)}")
        
    except Exception as e:
        print(f"Error during search: {e}")
        incremental_engine.cleanup()


if __name__ == '__main__':
    main()
