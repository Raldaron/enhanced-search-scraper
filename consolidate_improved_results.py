#!/usr/bin/env python
"""
Consolidate all improved scraper results into a master CSV file
"""
import csv
import os
from collections import defaultdict
from urllib.parse import urlparse
import glob

def consolidate_improved_results():
    """Consolidate all improved scraper CSV files"""
    
    # Find all the improved strategy CSV files
    csv_files = glob.glob("improved_bing_strategy_*.csv")
    
    if not csv_files:
        print("No improved strategy CSV files found!")
        return
    
    print(f"Found {len(csv_files)} CSV files to consolidate:")
    for file in csv_files:
        print(f"  - {file}")
    
    all_results = []
    unique_urls = set()
    domain_counts = defaultdict(int)
    
    # Process each CSV file
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                file_results = []
                
                for row in reader:
                    url = row['url']
                    
                    # Only process easyapply.co URLs
                    if 'easyapply.co' in url and url not in unique_urls:
                        unique_urls.add(url)
                        
                        # Extract domain for counting
                        try:
                            parsed = urlparse(url)
                            domain = parsed.netloc
                            domain_counts[domain] += 1
                        except:
                            domain = 'unknown'
                        
                        # Add source file info
                        row['source_file'] = csv_file
                        all_results.append(row)
                        file_results.append(row)
                
                print(f"{csv_file}: {len(file_results)} easyapply.co URLs")
                
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
    
    # Sort results by domain
    all_results.sort(key=lambda x: urlparse(x['url']).netloc)
    
    # Save consolidated results
    output_file = "improved_bing_easyapply_CONSOLIDATED.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        if all_results:
            fieldnames = ['url', 'title', 'description', 'domain', 'page', 'source_file']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in all_results:
                writer.writerow(result)
    
    print(f"\n📊 CONSOLIDATION COMPLETE!")
    print(f"Total unique easyapply.co URLs found: {len(all_results)}")
    print(f"Results saved to: {output_file}")
    
    # Show domain breakdown
    print(f"\n🏢 DOMAIN BREAKDOWN:")
    sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
    
    for domain, count in sorted_domains:
        print(f"{domain}: {count} URL{'s' if count != 1 else ''}")
        
        # Show URLs for this domain
        domain_urls = [r['url'] for r in all_results if urlparse(r['url']).netloc == domain]
        for url in domain_urls[:5]:  # Show first 5 URLs
            print(f"  - {url}")
        if len(domain_urls) > 5:
            print(f"  ... and {len(domain_urls) - 5} more")
        print()
    
    return all_results

if __name__ == "__main__":
    results = consolidate_improved_results()
