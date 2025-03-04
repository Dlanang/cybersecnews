import os
import time
import random
import requests
import re
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from datetime import datetime
from logging_config import logger
import cloudscraper  
import cfscrape  
from dotenv import load_dotenv

load_dotenv()

def get_severity(cvss):
    """Mengembalikan tingkat severity berdasarkan nilai CVSS (CVSS3.1)."""
    try:
        score = float(cvss)
        if score < 4.0:
            return "low"
        elif score < 7.0:
            return "medium"
        elif score < 9.0:
            return "high"
        else:
            return "critical"
    except Exception as e:
        logger.error(f"Error converting CVSS score: {e}")
        return "empty"

# BaseScraper dengan fallback ke cloudscraper dan cfscrape
class BaseScraper(ABC):
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"
        ]
        self.session.headers.update({
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Upgrade-Insecure-Requests": "1",
            "DNT": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate"
        })
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[429,500,502,503,504])
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        proxies_env = os.getenv("PROXIES", "")
        if proxies_env:
            self.proxies = [proxy.strip() for proxy in proxies_env.split(",") if proxy.strip()]
        else:
            self.proxies = []

    def _get_proxies(self):
        if self.proxies:
            proxy = random.choice(self.proxies)
            return {"http": proxy, "https": proxy}
        return None

    def fetch(self):
        try:
            time.sleep(random.uniform(0.5, 1.5))
            proxies = self._get_proxies()
            response = self.session.get(self.url, timeout=10, proxies=proxies)
            if response.status_code == 200:
                logger.info(f"Data berhasil diambil dengan requests dari {self.url}")
                return response.text
            else:
                logger.info(f"Requests returned status {response.status_code}. Fallback ke cloudscraper...")
                cscraper = cloudscraper.create_scraper()
                cscraper.headers.update({
                    "User-Agent": random.choice(self.user_agents),
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.google.com/",
                    "Upgrade-Insecure-Requests": "1",
                    "DNT": "1"
                })
                time.sleep(random.uniform(1,2))
                response = cscraper.get(self.url, timeout=10, proxies=self._get_proxies())
                if response.status_code == 200:
                    logger.info(f"Data berhasil diambil dengan cloudscraper dari {self.url}")
                    return response.text
                else:
                    logger.info(f"Cloudscraper returned status {response.status_code}. Fallback ke cfscrape...")
                    scraper_cfs = cfscrape.create_scraper()
                    time.sleep(random.uniform(1,2))
                    response = scraper_cfs.get(self.url, timeout=10, proxies=self._get_proxies())
                    if response.status_code == 200:
                        logger.info(f"Data berhasil diambil dengan cfscrape dari {self.url}")
                        return response.text
                    else:
                        error_detail = {
                            "error": f"Gagal mengambil data dari {self.url}",
                            "status_code": response.status_code,
                            "fallback": "cfscrape",
                            "response": response.text[:200]
                        }
                        logger.error(json.dumps(error_detail))
                        return json.dumps(error_detail)
        except Exception as e:
            error_detail = {"error": str(e), "url": self.url}
            logger.error(json.dumps(error_detail))
            return json.dumps(error_detail)
    
    @abstractmethod
    def parse(self, html_content):
        pass

    def scrape(self):
        html = self.fetch()
        if html:
            try:
                data = json.loads(html)
                if "error" in data:
                    logger.error(f"Error selama scraping: {data['error']}")
                    return data
            except json.JSONDecodeError:
                pass
            result = self.parse(html)
            if not result:
                logger.warning(f"Tidak ada data valid di {self.url}. Coba cek dengan view-source:{self.url}")
            return result
        else:
            return None

# HackerNewsScraper: Mengambil artikel dari The Hacker News dengan informasi penulis
class HackerNewsScraper(BaseScraper):
    def parse(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        # Coba ambil data JSON-LD jika tersedia
        scripts = soup.find_all('script', type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string)
                items = []
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    items = [data]
                for item in items:
                    if item.get("@type") in ["NewsArticle", "Article"]:
                        title = item.get("headline") or item.get("name")
                        snippet = item.get("description", "")
                        link = item.get("url")
                        author = item.get("author", {}).get("name", "Unknown")
                        articles.append({
                            "title": title,
                            "link": link,
                            "image": item.get("image"),
                            "snippet": snippet if len(snippet) <= 150 else snippet[:150] + "...",
                            "author": author
                        })
                if articles:
                    return articles
            except Exception as e:
                logger.error(f"Error parsing JSON-LD in HackerNewsScraper: {e}")
                continue

        # Fallback: Parsing HTML konvensional
        for article in soup.find_all('div', class_='body-post'):
            title_elem = article.find('h2', class_='home-title')
            if title_elem:
                title = title_elem.get_text(strip=True)
                link_elem = article.find('a')
                link = link_elem['href'] if link_elem and link_elem.has_attr('href') else None
                desc_elem = article.find('div', class_='home-desc')
                snippet = desc_elem.get_text(strip=True) if desc_elem else ""
                if len(snippet) > 150:
                    snippet = snippet[:150] + "..."
                author_elem = article.find('span', class_='author')
                author = author_elem.get_text(strip=True) if author_elem else "Unknown"
                articles.append({
                    "title": title,
                    "link": link,
                    "image": None,
                    "snippet": snippet,
                    "author": author
                })
        return articles

# OpenCVEScraper: Mengambil data dari API OpenCVE dan menyaring berdasarkan tingkat CVSS (opsional)
class OpenCVEScraper:
    BASE_URL = "https://app.opencve.io/api/cve"
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.auth = (os.getenv("OPEN_CVE_USERNAME"), os.getenv("OPEN_CVE_PASSWORD"))
        self.headers = {"Accept": "application/json"}
        # Ambil variabel CVSS_LEVEL dan pisahkan jika ada koma
        cvss_level = os.getenv("CVSS_LEVEL", "").lower()
        if cvss_level:
            self.cvss_levels = [level.strip() for level in cvss_level.split(",")]
        else:
            self.cvss_levels = []
    
    def fetch(self):
        url = self.BASE_URL
        try:
            response = requests.get(url, headers=self.headers, auth=self.auth, timeout=10)
            response.raise_for_status()
            logger.info(f"Berhasil mengambil data CVE dari {url}")
            return response.json()
        except Exception as e:
            logger.error(f"Error mengambil data dari OpenCVE API: {e}")
            return None

    def parse(self, data):
        if not data:
            return []
        parsed_cves = []
        for cve in data:
            cve_id = cve.get("id")
            description = cve.get("summary", "Deskripsi tidak tersedia.")
            cvss = cve.get("cvss", None)
            if cvss is None or cvss == "N/A":
                continue
            severity = get_severity(cvss)
            # Jika filter sudah diatur, periksa apakah severity masuk dalam daftar yang diizinkan
            if self.cvss_levels and severity not in self.cvss_levels:
                continue
            link = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
            parsed_cves.append({
                "title": cve_id,
                "link": link,
                "image": None,
                "snippet": description if len(description) <= 150 else description[:150] + "...",
                "cve": [cve_id],
                "cvss": cvss,
                "author": "OpenCVE"
            })
        return parsed_cves

    def scrape(self):
        raw_data = self.fetch()
        return self.parse(raw_data)


class ScraperFactory:
    @staticmethod
    def get_scraper(site):
        if site == 'hackernews_vulnerability':
            return HackerNewsScraper("https://thehackernews.com/search/label/Vulnerability")
        elif site == 'hackernews_attack':
            return HackerNewsScraper("https://thehackernews.com/search/label/Cyber%20Attack")
        elif site == 'opencve':
            return OpenCVEScraper()
        else:
            raise ValueError("Unsupported site for scraping")
