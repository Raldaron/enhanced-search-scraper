# AGENTS.md

## Project Overview

This is a **Bing web scraping project** focused on extracting comprehensive search results with maximum coverage and reliability. The primary goal is to build a robust, anti-detection scraping system that can handle Bing's various HTML structures, pagination schemes, and bot prevention measures.

## Agent Empowerment & Permissions

**You have FULL AUTHORITY to:**

✅ **Modify any and all code files** - refactor, rewrite, or completely restructure as needed  
✅ **Create new files and modules** - add utilities, classes, configs, or entirely new approaches  
✅ **Install any Python packages** - add dependencies to requirements.txt without asking  
✅ **Implement aggressive optimizations** - performance, reliability, or coverage improvements  
✅ **Experiment with different approaches** - try multiple scraping strategies simultaneously  
✅ **Add comprehensive logging and debugging** - we want to understand what's happening  
✅ **Implement any anti-detection measures** - rotate headers, proxies, delays, sessions  
✅ **Create test files and validation scripts** - ensure everything works properly  
✅ **Optimize for maximum data extraction** - prioritize getting ALL available results  
✅ **Add parallel processing capabilities** - speed up scraping with threading/async  
✅ **Implement robust error handling** - retry logic, fallbacks, graceful degradation  

## Project Philosophy

**"Better to ask for forgiveness than permission"** - This project prioritizes:

1. **Maximum Result Coverage** - Extract every possible search result from Bing
2. **Robustness Over Elegance** - Multiple fallbacks and redundancy are preferred
3. **Anti-Detection First** - Always assume we need to avoid bot detection
4. **Data Quality** - Clean, deduplicated, structured results
5. **Maintainability** - Code should be readable and extensible
6. **Performance** - Fast execution without sacrificing reliability

## Technical Context

### Web Scraping Domain Knowledge
- **Bing frequently changes HTML structure** - Always use multiple CSS selector fallbacks
- **Rate limiting is common** - Implement smart delays and request throttling
- **URLs are often encoded** - Handle base64, redirects, and click tracking
- **Pagination can be tricky** - Detect end-of-results conditions properly
- **Headers matter** - Rotate User-Agents and mimic real browser behavior

### Current Challenges
- Not extracting all available results from search pages
- Missing results due to HTML structure changes
- Potential bot detection issues
- Need better pagination handling
- URL decoding problems with Bing's various encoding schemes

## Codebase Structure

```
/
├── engine.py              # Base SearchEngine class (modify freely)
├── bing.py               # Main Bing scraper class (enhance heavily)
├── improved_scraper.py   # Enhanced version with anti-detection
├── config.py            # Configuration settings (expand as needed)
├── utils/               # Create this - utility functions
├── tests/               # Create this - validation and testing
├── results/             # Create this - output data storage
└── requirements.txt     # Add any packages needed
```

## Coding Standards & Preferences

### Code Style
- **Python 3.8+** compatibility
- **Type hints encouraged** but not required
- **Comprehensive docstrings** for all public methods
- **Descriptive variable names** - clarity over brevity
- **Error handling everywhere** - assume things will break

### Libraries & Tools
**Preferred Stack:**
- `requests` or `httpx` for HTTP requests
- `BeautifulSoup4` for HTML parsing
- `pandas` for data manipulation
- `concurrent.futures` for parallel processing
- `fake-useragent` or custom UA rotation
- `time` and `random` for delays
- `logging` for comprehensive debugging

**You may add any additional libraries that improve:**
- Anti-detection capabilities
- Performance and speed
- Data quality and validation
- Error handling and recovery
- Testing and monitoring

### Architecture Preferences
- **Modular design** - separate concerns into different files
- **Configurable everything** - use config files/environment variables
- **Multiple strategies** - implement various approaches and compare results
- **Robust error handling** - retry logic, exponential backoff, graceful failures
- **Comprehensive logging** - we want to see what's happening under the hood

## Specific Instructions

### Anti-Detection Priorities
1. **Rotate everything** - User-Agents, headers, IP addresses (if proxy available)
2. **Random delays** - Between requests, between pages, between strategies
3. **Session management** - Maintain cookies and connection state properly
4. **Request variation** - Vary request patterns to look human
5. **Error camouflage** - Handle CAPTCHAs and rate limits gracefully

### Data Extraction Goals
- **Extract ALL result types** - web results, news, images, local results
- **Handle all URL formats** - direct links, redirects, encoded URLs
- **Capture complete metadata** - titles, descriptions, domains, rankings
- **Implement deduplication** - Remove duplicate results across strategies
- **Structure output** - Clean CSV/JSON with consistent schema

### Performance Targets
- **Concurrent requests** where safe (multiple search strategies)
- **Efficient pagination** - Stop when no more results available
- **Memory management** - Handle large result sets without crashes
- **Speed optimization** - Fast enough for practical use cases

## Testing & Validation

**You should create tests that verify:**
- All CSS selectors find results on current Bing pages
- URL decoding handles all Bing encoding formats
- Pagination works across multiple pages
- Anti-detection measures are effective
- Results are properly deduplicated
- Output format is clean and consistent

## Development Workflow

1. **Analyze current code** - Understand existing limitations
2. **Research Bing's current HTML** - Check what selectors work now
3. **Implement enhancements incrementally** - Test each improvement
4. **Create comprehensive test suite** - Validate everything works
5. **Optimize for production use** - Performance and reliability
6. **Document changes** - Update this file as you learn more

## Success Metrics

**We'll know this is working when:**
- Consistently extracting 2-5x more results per search
- Zero failures due to HTML structure changes
- Clean, properly formatted output data
- Fast execution even with anti-detection measures
- Robust error handling prevents crashes
- Easy to extend with new search strategies

## Final Notes

**This is a learning project and production tool.** Don't hold back on implementing sophisticated solutions. If you think something will improve result coverage, reliability, or performance - just do it. We can always iterate and improve.

**When in doubt, err on the side of being too thorough rather than too minimal.** This scraper should be industrial-strength and handle whatever Bing throws at it.

**Feel free to completely restructure** this codebase if you have a better architectural approach. The only requirement is that it extracts more comprehensive Bing search results than the current implementation.

---

*Last updated: June 2025 - Update this file as the project evolves*
