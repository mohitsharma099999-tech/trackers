import re
import requests
from .base import BaseTracker


class AmazonTracker(BaseTracker):
    def _resolve_url(self, url):
        """Follow redirects (e.g. amzn.in/d/xxx) to get the real product URL."""
        try:
            resp = requests.head(
                url, headers=self.headers, allow_redirects=True, timeout=15
            )
            return resp.url
        except requests.RequestException:
            # Fall back to the original URL if head fails
            return url

    def get_price(self, url):
        url = self._resolve_url(url)
        soup = self.fetch_page(url)

        price_selectors = [
            'span.a-price-whole',
            'span#priceblock_ourprice',
            'span#priceblock_dealprice',
            'span.a-offscreen',
            'span.priceToPay',
            'span.apexPriceToPay span.a-offscreen',
            'span#corePrice_feature_div span.a-offscreen',
        ]

        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                # Remove currency symbols, commas, spaces
                cleaned = re.sub(r'[^\d.]', '', price_text.replace(',', ''))
                # Take only the first number (guards against "1234.5678")
                match = re.search(r'\d+\.?\d{0,2}', cleaned)
                if match:
                    return float(match.group())

        raise Exception("Could not find price on page (Amazon may have blocked the request)")

    def get_title(self, url):
        url = self._resolve_url(url)
        soup = self.fetch_page(url)

        for selector in ('#productTitle', 'span#title', 'h1#title'):
            el = soup.select_one(selector)
            if el:
                return el.get_text(strip=True)

        return "Unknown Product"