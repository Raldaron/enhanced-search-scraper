# Enhanced Search Engines Scraper

A Python-based tool for scraping and consolidating results from multiple search engines, including Bing, DuckDuckGo, Yahoo, and more. Useful for research, data collection, and competitive analysis.

## Features
- Multi-engine scraping (Bing, DuckDuckGo, Yahoo, etc.)
- Incremental and comprehensive scraping modes
- CSV output for easy data analysis
- Modular engine support for easy extension

## Requirements
- Python 3.8+
- `requests`, `beautifulsoup4`, and other dependencies (see below)

## Setup
1. Clone this repository:
   ```powershell
   git clone https://github.com/Raldaron/enhanced-search-scraper.git
   cd enhanced-search-scraper
   ```
2. (Optional) Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage
Run a scraper script, for example:
```powershell
python comprehensive_scraper.py
```

Or for incremental scraping:
```powershell
python incremental_scraper.py
```

## Contributing
Pull requests and issues are welcome!

## License
MIT License
