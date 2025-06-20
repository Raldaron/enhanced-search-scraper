import base64
from urllib.parse import urlparse, parse_qs        

from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT


class Bing(SearchEngine):
    '''Searches bing.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Bing, self).__init__(proxy, timeout)
        self._base_url = u'https://www.bing.com'
        self.set_headers({'User-Agent':FAKE_USER_AGENT})

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            # Multiple fallbacks for robustness against Bing layout changes
            'links': 'li.b_algo, .b_algo, li.algo, .algo',
            'url': 'h2 a[href], h3 a[href], a[href]',
            'title': 'h2 a, h3 a, .b_title a',
            'text': '.b_caption p, .b_snippetBigText, .b_algoSlug, p',
            'next': 'a.sb_pagN, .sb_pagN, a[aria-label="Next page"]'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        self._get_page(self._base_url)
        url = u'{}/search?q={}&search=&form=QBLH'.format(self._base_url, self._query)
        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = None
        if next_page:
            url = (self._base_url + next_page) 
        return {'url':url, 'data':None}

    def _get_url(self, tag, item='href'):
        """Return the clean URL of a Bing search result item.

        Bing uses several redirection/encoding schemes.  This method attempts to
        decode them and fall back to the original value if decoding fails.
        """

        raw_url = super(Bing, self)._get_url(tag, 'href')
        url = raw_url

        try:
            # Bing sometimes returns relative links starting with '/'.
            if url.startswith('/'):
                url = self._base_url + url

            parsed = urlparse(url)

            # Handle Bing click-tracking links (e.g. https://www.bing.com/ck/a?)
            if parsed.netloc.endswith('bing.com') and parsed.path.startswith('/ck'):
                params = parse_qs(parsed.query)
                encoded = params.get('u') or params.get('r')
                if encoded:
                    url = encoded[0]

            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            # URLs can contain a base64 encoded 'u' parameter
            if 'u' in params and params['u']:
                encoded_url = params['u'][0]

                # remove "a1" prefix used by Bing for some links
                if encoded_url.startswith('a1'):
                    encoded_url = encoded_url[2:]

                # fix base64 padding when missing
                missing = len(encoded_url) % 4
                if missing:
                    encoded_url += '=' * (4 - missing)

                url = base64.b64decode(encoded_url).decode('utf-8')

        except Exception as exc:
            # In case of any decoding/parsing issue just return the original URL
            print(f"Error decoding Bing URL '{raw_url}': {exc}")
            url = raw_url

        return url
