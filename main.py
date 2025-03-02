# main.py
import os
import time
import logging
from dotenv import load_dotenv
from scraper import ScraperFactory
from discord_webhook import send_embed

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
CUSTOM_IMAGE_URL = os.getenv("CUSTOM_IMAGE_URL")

# Signature
SIGNATURE = "Made with (love) from N4THE4N+P7312=0x000"

def main():
    embeds = []

    # --- Embed untuk Reddit Threads ---
    reddit_scraper = ScraperFactory.get_scraper('reddit')
    reddit_threads = reddit_scraper.scrape()
    if reddit_threads:
        reddit_description = "\n".join(reddit_threads)
    else:
        reddit_description = "Tidak ada data atau terjadi error saat mengambil data dari Reddit."
    
    embed_reddit = {
        "title": "Cybersecurity Threads dari Reddit",
        "description": reddit_description,
        "color": 3447003,
        "footer": {"text": SIGNATURE}
    }
    embeds.append(embed_reddit)

    # --- Embed untuk Hacker News: Vulnerability Articles ---
    hackernews_vuln_scraper = ScraperFactory.get_scraper('hackernews_vulnerability')
    hackernews_vuln_articles = hackernews_vuln_scraper.scrape()
    if hackernews_vuln_articles:
        for article in hackernews_vuln_articles:
            title = article.get('title', 'No Title')
            link = article.get('link', '#')
            image = article.get('image') if article.get('image') else CUSTOM_IMAGE_URL
            snippet = article.get('snippet', '')
            embed_article = {
                "title": title,         # Judul klikable
                "url": link,
                "description": snippet, # Cuplikan isi artikel
                "color": 15158332,
                "image": {"url": image},
                "footer": {"text": SIGNATURE}
            }
            embeds.append(embed_article)
    else:
        embed_error_vuln = {
            "title": "Artikel Vulnerability dari The Hacker News",
            "description": "Tidak ada data atau terjadi error saat mengambil data.",
            "color": 15158332,
            "footer": {"text": SIGNATURE}
        }
        embeds.append(embed_error_vuln)

    # --- Embed untuk Hacker News: Cyber Attack Articles ---
    hackernews_attack_scraper = ScraperFactory.get_scraper('hackernews_attack')
    hackernews_attack_articles = hackernews_attack_scraper.scrape()
    if hackernews_attack_articles:
        for article in hackernews_attack_articles:
            title = article.get('title', 'No Title')
            link = article.get('link', '#')
            image = article.get('image') if article.get('image') else CUSTOM_IMAGE_URL
            snippet = article.get('snippet', '')
            embed_article = {
                "title": title,
                "url": link,
                "description": snippet,
                "color": 15158332,
                "image": {"url": image},
                "footer": {"text": SIGNATURE}
            }
            embeds.append(embed_article)
    else:
        embed_error_attack = {
            "title": "Artikel Cyber Attack dari The Hacker News",
            "description": "Tidak ada data atau terjadi error saat mengambil data.",
            "color": 15158332,
            "footer": {"text": SIGNATURE}
        }
        embeds.append(embed_error_attack)

    # Mengirim embed ke Discord satu per satu dengan delay untuk menghindari spam
    for embed in embeds:
        send_embed([embed])  # Kirim embed dalam bentuk list dengan satu elemen
        logger.info("Embed dikirim, menunggu 2 detik sebelum mengirim embed berikutnya...")
        time.sleep(2)  # Delay 2 detik antar pengiriman

if __name__ == "__main__":
    main()