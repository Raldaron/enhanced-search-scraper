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
            'url': 'h2 a', 
            'title': 'h2', 
            'text': 'p', 
            'links': 'ol#b_results > li.b_algo', 
            'next': 'div#b_content nav[role="navigation"] a.sb_pagN'
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
        '''Returns the URL of search results items.'''
        url = super(Bing, self)._get_url(tag, 'href')
        resp = url  # Default fallback to original URL

        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # Check if 'u' parameter exists in the query
            if "u" in query_params and len(query_params["u"]) > 0:
                encoded_url = query_params["u"][0]
                
                # Remove 'a1' prefix if present
                if encoded_url.startswith('a1'):
                    encoded_url = encoded_url[2:]
                
                # fix base64 padding
                encoded_url += (len(encoded_url) % 4) * "="

                decoded_bytes = base64.b64decode(encoded_url)
                resp = decoded_bytes.decode('utf-8')
            else:
                # If no 'u' parameter, the URL might be direct
                resp = url
                
        except Exception as e:
            print(f"Error decoding Base64 string: {e}, falling back to original URL")
            resp = url  # Fallback to original URL

        return resp
