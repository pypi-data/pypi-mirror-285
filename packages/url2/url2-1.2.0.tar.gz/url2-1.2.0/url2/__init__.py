import json
import re
from lxml import etree
from autoscraper import AutoScraper
from curl_cffi import requests


class url2:
    """
    A class to handle HTTP requests and response parsing using curl_cffi.
    """

    def __init__(self, url, headers=None, encode=None, verify=True, redirect=True, form_data=None, impersonate="chrome120"):
        self.url = url
        self.headers = headers or {'User-Agent': 'Mozilla/5.0'}
        self.encode = encode
        self.verify = verify
        self.redirect = redirect
        self.form_data = form_data
        self._response = None
        self.impersonate = impersonate

    @property
    def html(self) -> str:
        """
        Fetch the URL content and return it as HTML text.
        """
        if self.form_data is None:
            response = requests.get(self.url, headers=self.headers, verify=self.verify,
                                    allow_redirects=self.redirect, impersonate=self.impersonate)
        else:
            response = requests.post(self.url, data=self.form_data, headers=self.headers,
                                     verify=self.verify, allow_redirects=self.redirect, impersonate=self.impersonate)

        if self.encode:
            response.encoding = self.encode
        else:
            response.encoding = response.default_encoding

        self._response = response
        return response.text

    @property
    def json(self) -> dict:
        """Return the parsed JSON content."""
        return json.loads(self.html)

    @property
    def xpath(self) -> etree.HTML:
        """Return the parsed HTML as an lxml etree object with xpath support."""
        return etree.HTML(self.html).xpath

    @staticmethod
    def headers_handle(headers: str) -> dict:
        """
        Convert a header string to a dictionary.
        """
        headers = headers.lstrip('\n')
        pattern = r'^(.*?):\s*(.*?)$'
        dict_str = '{' + ','.join(re.sub(pattern, r'\'\1\':\'\2\'', line)
                                  for line in headers.splitlines()) + '}'
        return eval(dict_str)

    def build(self, wanted_dict, model_name=None):
        """
        Build an AutoScraper model with the given wanted_dict.
        """
        scraper = AutoScraper()
        result = scraper.build(html=self.html, wanted_dict=wanted_dict)
        if model_name:
            scraper.save(model_name)
        return result

    def build_load(self, url, model_name='1'):
        """
        Load a saved AutoScraper model and get the result for the given URL.
        """
        scraper = AutoScraper()
        scraper.load(model_name)
        response = requests.get(url)
        response.encoding = response.default_encoding
        html = response.text
        return scraper.get_result_similar(url, html=html, group_by_alias=True)


if __name__ == '__main__':
    #   headers= {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none", }
    url = 'https://api.openloot.com/v2/market/listings/BT0_Hourglass_Rare/items?onSale=true&page=1&pageSize=48&sort=price%3Aasc'
    data = url2(url, headers=headers)
    print(data.html)
    print(data._response.url)
