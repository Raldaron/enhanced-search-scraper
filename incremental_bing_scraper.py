#!/usr/bin/env python3
import argparse
import csv
import os
import time

try:
    from search_engines.engines import search_engines_dict
    from search_engines import config
except ImportError as e:
    print(f"Error importing search_engines: {e}")
    print("Please ensure search_engines library is installed")
    exit(1)

class IncrementalBingScraper:
    def __init__(self):
        self.csv_file = None
        self.csv_writer = None
        self.results_count = 0
        self.unique_urls = set()
        
    def setup_csv(self, filename):
        """Initialize CSV file with headers"""
        file_exists = os.path.exists(filename)
        self.csv_file = open(filename, 'a', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)
        
        if not file_exists:
            headers = ['query', 'engine', 'domain', 'URL', 'title', 'text', 'page_found']
            self.csv_writer.writerow(headers)
            self.csv_file.flush()
            print(f"Created CSV file: {filename}")
        else:
            print(f"Appending to existing CSV file: {filename}")
    
    def save_results(self, results, query, page_num):
        """Save results to CSV immediately"""
        new_results = 0
        for result in results:
            url = result.get('link', '')
            if url and url not in self.unique_urls and 'easyapply.co' in url.lower():
                self.unique_urls.add(url)
                row = [
                    query,
                    'Bing',
                    result.get('host', ''),
                    url,
                    result.get('title', ''),
                    result.get('text', ''),
                    page_num
                ]
                self.csv_writer.writerow(row)
                new_results += 1
                self.results_count += 1
        
        self.csv_file.flush()
        return new_results
    
    def search_and_save(self, query, max_pages, csv_filename):
        """Search using the existing library but save incrementally"""
        self.setup_csv(csv_filename)
        
        # Get Bing engine
        bing_engine = search_engines_dict['bing'](config.PROXY, config.TIMEOUT)
        
        print(f"Searching Bing for: '{query}'")
        print(f"Max pages: {max_pages}")
        
        # Perform search for specified number of pages
        results = bing_engine.search(query, max_pages)
        
        # Save all results at once (since the library doesn't allow incremental access)
        total_new = 0
        for i, result in enumerate(results, 1):
            url = result.get('link', '')
            if url and url not in self.unique_urls and 'easyapply.co' in url.lower():
                self.unique_urls.add(url)
                # Estimate page number (10 results per page)
                estimated_page = ((i - 1) // 10) + 1
                row = [
                    query,
                    'Bing',
                    result.get('host', ''),
                    url,
                    result.get('title', ''),
                    result.get('text', ''),
                    estimated_page
                ]
                self.csv_writer.writerow(row)
                total_new += 1
                self.results_count += 1
                
                # Flush every 10 results
                if total_new % 10 == 0:
                    self.csv_file.flush()
                    print(f"Saved {total_new} easyapply.co results so far...")
        
        self.csv_file.flush()
        print(f"Total unique easyapply.co results saved: {self.results_count}")
        
        return self.results_count
    
    def cleanup(self):
        """Close CSV file"""
        if self.csv_file:
            self.csv_file.close()

def run_multiple_searches():
    """Run multiple search strategies"""
    search_queries = [
        "easyapply.co",
        "site:easyapply.co", 
        '"easyapply.co"',
        "easyapply.co jobs",
        "easyapply.co careers",
        "easyapply.co apply",
        "easyapply.co hiring",
        "inurl:easyapply.co",
        "site:*.easyapply.co"
    ]
    
    total_results = 0
    
    for i, query in enumerate(search_queries, 1):
        print(f"\n{'='*60}")
        print(f"SEARCH STRATEGY {i}/{len(search_queries)}: {query}")
        print(f"{'='*60}")
        
        # Create safe filename
        safe_query = query.replace('"', '').replace(':', '_').replace('*', 'wildcard').replace(' ', '_')
        filename = f"bing_easyapply_{i:02d}_{safe_query}.csv"
        
        scraper = IncrementalBingScraper()
        
        try:
            # Use different page counts for different queries
            if "site:" in query:
                max_pages = 50  # Site searches tend to have fewer unique results
            else:
                max_pages = 100  # Broader searches might have more
                
            results_count = scraper.search_and_save(query, max_pages, filename)
            total_results += results_count
            print(f"Strategy {i} completed: {results_count} easyapply.co results saved to {filename}")
            
        except Exception as e:
            print(f"Error in search strategy {i}: {e}")
        finally:
            scraper.cleanup()
        
        # Wait between different searches to be respectful
        if i < len(search_queries):
            wait_time = 10
            print(f"Waiting {wait_time} seconds before next search...")
            time.sleep(wait_time)
    
    print(f"\n{'='*60}")
    print(f"ALL SEARCHES COMPLETED")
    print(f"{'='*60}")
    print(f"Total easyapply.co results across all strategies: {total_results}")
    print("Check the individual CSV files for results from each search strategy.")

def main():
    parser = argparse.ArgumentParser(description='Incremental Bing scraper for easyapply.co')
    parser.add_argument('--query', help='Single search query')
    parser.add_argument('--pages', type=int, default=50, help='Maximum pages to scrape')
    parser.add_argument('--output', default='bing_easyapply.csv', help='Output CSV file')
    parser.add_argument('--all-strategies', action='store_true', help='Run all search strategies')
    
    args = parser.parse_args()
    
    if args.all_strategies:
        run_multiple_searches()
    elif args.query:
        scraper = IncrementalBingScraper()
        try:
            results_count = scraper.search_and_save(args.query, args.pages, args.output)
            print(f"\nCompleted: {results_count} easyapply.co results saved to {args.output}")
        finally:
            scraper.cleanup()
    else:
        print("Please specify either --query or --all-strategies")
        parser.print_help()

if __name__ == '__main__':
    main()
