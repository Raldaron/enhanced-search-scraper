#!/usr/bin/env python3
"""Run multiple Bing search strategies and save results.

This script creates a fresh ``ImprovedBingScraper`` instance for each query and
saves the results to timestamped CSV files. A progress file allows resuming from
an interrupted run.
"""

import os
import time
from datetime import datetime

from improved_bing_scraper import ImprovedBingScraper


# List of queries covering several search approaches
SEARCH_STRATEGIES = [
    "site:easyapply.co",
    "easyapply.co",
    '"easyapply.co"',
    "inurl:easyapply.co",
    "url:easyapply.co",
    "easyapply.co jobs",
    "easyapply.co careers",
    "easyapply.co hiring",
    "easyapply.co application",
    '"easy apply" jobs',
    "easy apply careers",
    "filetype:html site:easyapply.co",
]

PROGRESS_FILE = "strategy_progress.txt"


def load_progress():
    """Return the index of the last completed strategy."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                idx = int(f.read().strip())
                return idx
        except Exception:
            return 0
    return 0


def save_progress(index):
    """Save the last completed strategy index."""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write(str(index))


def main():
    """Run comprehensive Bing search using multiple query strategies."""
    start_index = load_progress()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for i, query in enumerate(SEARCH_STRATEGIES[start_index:], start=start_index + 1):
        print("\n" + "=" * 60)
        print(f"STRATEGY {i}/{len(SEARCH_STRATEGIES)}: {query}")
        print("=" * 60)

        scraper = ImprovedBingScraper()
        try:
            results = scraper.search_bing(query, max_pages=7, delay_range=(3, 6))
            csv_name = f"bing_strategy_{i:02d}_{timestamp}.csv"
            scraper.save_to_csv(csv_name)
            print(f"Strategy {i} completed: {len(results)} results saved")
            save_progress(i)
        except KeyboardInterrupt:
            print("\nRun interrupted by user. Progress saved.")
            save_progress(i - 1)
            return
        except Exception as e:
            print(f"Error in strategy {i}: {e}")
            save_progress(i - 1)
            continue

        if i < len(SEARCH_STRATEGIES):
            time.sleep(10)

    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
    print("\nAll strategies completed!")


if __name__ == "__main__":
    main()

