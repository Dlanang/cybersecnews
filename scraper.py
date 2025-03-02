# scraper.py
import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# BaseScraper: Template Method Pattern dengan peningkatan anti-bot
class BaseScraper(ABC):
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        # Menggunakan user agent modern
        self.session.headers.update({
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/90.0.4430.93 Safari/537.36")
        })
        # Konfigurasi retries untuk error (misal: 429, 500)
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def fetch(self):
        """Mengambil konten HTML dari URL dengan delay acak untuk menghindari deteksi bot."""
        try:
            time.sleep(random.uniform(0.5, 1.5))  # Delay acak
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            logger.info(f"Berhasil mengambil data dari {self.url}")
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {self.url}: {e}")
            return None

    @abstractmethod
    def parse(self, html_content):
        """Mengubah HTML menjadi data yang diinginkan."""
        pass

    def scrape(self):
        """Metode template yang menggabungkan fetch dan parse."""
        html = self.fetch()
        if html:
            result = self.parse(html)
            if not result:
                # Jika parsing tidak menemukan data, log pesan fallback
                logger.warning(f"Tidak ditemukan data yang valid di {self.url}. "
                               "Jika terjadi masalah dengan user agent, coba buka: "
                               f"view-source:{self.url} untuk melihat HTML mentah.")
            return result
        else:
            return None

# RedditScraper: Untuk scraping thread dari subreddit cybersecurity
class RedditScraper(BaseScraper):
    def parse(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        threads = []
        # Misal: ambil semua judul thread yang diasumsikan berada di tag <h3> dengan indexing
        for idx, h3 in enumerate(soup.find_all('h3'), start=1):
            threads.append(f"{idx}. {h3.get_text(strip=True)}")
        return threads

# HackerNewsScraper: Untuk scraping artikel dari The Hacker News
class HackerNewsScraper(BaseScraper):
    def parse(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        # Asumsi: tiap artikel berada di div dengan kelas 'body-post'
        # dan judul terdapat di tag <h2> dengan kelas 'home-title'
        for article in soup.find_all('div', class_='body-post'):
            title_elem = article.find('h2', class_='home-title')
            if title_elem:
                title = title_elem.get_text(strip=True)
                link_elem = article.find('a')
                link = link_elem['href'] if link_elem and link_elem.has_attr('href') else None

                # Ekstrak snippet dari artikel (misal: div dengan kelas 'home-desc')
                desc_elem = article.find('div', class_='home-desc')
                snippet = ""
                if desc_elem:
                    snippet = desc_elem.get_text(strip=True)
                    # Batasi snippet hingga 150 karakter
                    if len(snippet) > 150:
                        snippet = snippet[:150] + "..."

                # Coba ambil gambar dari tag <img>
                img_elem = article.find('img')
                image = img_elem['src'] if img_elem and img_elem.has_attr('src') else None

                articles.append({
                    'title': title,
                    'link': link,
                    'image': image,
                    'snippet': snippet
                })
        return articles

# Factory Pattern untuk pembuatan scraper berdasarkan kategori situs
class ScraperFactory:
    @staticmethod
    def get_scraper(site):
        if site == 'reddit':
            return RedditScraper("https://www.reddit.com/r/cybersecurity/")
        elif site == 'hackernews_vulnerability':
            return HackerNewsScraper("https://thehackernews.com/search/label/Vulnerability")
        elif site == 'hackernews_attack':
            return HackerNewsScraper("https://thehackernews.com/search/label/Cyber%20Attack")
        else:
            raise ValueError("Unsupported site for scraping")
