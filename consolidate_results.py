#!/usr/bin/env python3
import csv
import os
from pathlib import Path

def consolidate_bing_results():
    """Consolidate all Bing search results into one master file"""
    
    # Find all CSV files
    csv_files = list(Path('.').glob('bing_easyapply_*.csv'))
    
    all_results = []
    unique_urls = set()
    
    for csv_file in csv_files:
        print(f"Processing {csv_file}...")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                file_results = 0
                for row in reader:
                    url = row.get('URL', '')
                    if url and url not in unique_urls:
                        unique_urls.add(url)
                        all_results.append(row)
                        file_results += 1
                
                print(f"  Found {file_results} unique results")
                
        except Exception as e:
            print(f"  Error reading {csv_file}: {e}")
    
    # Sort results by domain for better organization
    all_results.sort(key=lambda x: (x.get('domain', ''), x.get('URL', '')))
    
    # Write consolidated file
    output_file = 'bing_easyapply_CONSOLIDATED.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        if all_results:
            fieldnames = all_results[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
    
    print(f"\n=== CONSOLIDATION COMPLETE ===")
    print(f"Total unique URLs found: {len(all_results)}")
    print(f"Consolidated file: {output_file}")
    
    # Print summary by domain
    domains = {}
    for result in all_results:
        domain = result.get('domain', 'unknown')
        if domain not in domains:
            domains[domain] = []
        domains[domain].append(result.get('URL', ''))
    
    print(f"\n=== DOMAIN BREAKDOWN ===")
    for domain, urls in sorted(domains.items()):
        print(f"{domain}: {len(urls)} URLs")
        for url in urls:
            print(f"  - {url}")
    
    return all_results

if __name__ == '__main__':
    results = consolidate_bing_results()
