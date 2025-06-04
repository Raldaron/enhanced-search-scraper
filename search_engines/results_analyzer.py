import json
from collections import defaultdict
from typing import List, Dict, Any
from urllib.parse import urlparse, urlunparse

from rapidfuzz import fuzz
import pandas as pd


class ResultsAnalyzer:
    """Analyze and deduplicate search results from multiple strategies."""

    def __init__(self) -> None:
        """Initialize analyzer with tracking for URLs, domains, and quality metrics."""
        self.seen_urls = set()
        self.seen_domain_paths = {}

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Return URL without query parameters for deduplication."""
        parsed = urlparse(url)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

    @staticmethod
    def _quality_score(result: Dict[str, Any]) -> float:
        """Compute a rough quality score based on description length, page rank and redirects."""
        description = result.get('description') or result.get('text') or ''
        page = int(result.get('page', result.get('page_found', 1)))
        url = result.get('url') or result.get('link', '')
        score = len(description)
        score += max(0, 50 - (page - 1) * 5)
        if 'bing.com' in url and 'http' in urlparse(url).netloc:
            score -= 5
        return score

    def _select_preferred(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Return the result with the higher quality score."""
        return new if self._quality_score(new) > self._quality_score(existing) else existing

    def deduplicate_results(self, results_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and sort results by quality."""
        deduped: List[Dict[str, Any]] = []
        titles = []
        for result in results_list:
            url = result.get('url') or result.get('link')
            if not url:
                continue
            if url in self.seen_urls:
                continue
            domain_path = self._normalize_url(url)
            fuzzy_match = None
            for t in titles:
                if fuzz.ratio(t.lower(), (result.get('title') or '').lower()) > 90:
                    fuzzy_match = t
                    break
            if fuzzy_match:
                idx = titles.index(fuzzy_match)
                deduped[idx] = self._select_preferred(deduped[idx], result)
                self.seen_urls.add(url)
                continue
            if domain_path in self.seen_domain_paths:
                idx = self.seen_domain_paths[domain_path]
                deduped[idx] = self._select_preferred(deduped[idx], result)
                self.seen_urls.add(url)
                continue
            self.seen_urls.add(url)
            self.seen_domain_paths[domain_path] = len(deduped)
            titles.append(result.get('title', ''))
            deduped.append(result)
        deduped.sort(key=self._quality_score, reverse=True)
        return deduped

    def analyze_coverage(self, results_by_strategy: Dict[str, List[Dict[str, Any]]], output_path: str = 'analysis_report.json') -> Dict[str, Any]:
        """Analyze which search strategies found the most unique results."""
        strategy_counts = {}
        all_urls = set()
        domain_counts = defaultdict(int)

        for strategy, results in results_by_strategy.items():
            urls = {r.get('url') or r.get('link') for r in results if r.get('url') or r.get('link')}
            strategy_counts[strategy] = len(urls)
            all_urls.update(urls)
            for url in urls:
                domain_counts[urlparse(url).netloc] += 1

        ranking = sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True)
        recommended = [s for s, _ in ranking[:2]] if len(ranking) >= 2 else [s for s, _ in ranking]

        analysis = {
            'unique_urls_per_strategy': strategy_counts,
            'strategy_ranking': ranking,
            'domain_distribution': dict(sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)),
            'recommended_strategies': recommended,
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        return analysis
