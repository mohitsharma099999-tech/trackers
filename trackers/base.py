from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup


class BaseTracker(ABC):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def fetch_page(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch page: {e}")

    @abstractmethod
    def get_price(self, url):
        pass

    @abstractmethod
    def get_title(self, url):
        pass
