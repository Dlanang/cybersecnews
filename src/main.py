import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from scraper import ScraperFactory
from discord_webhook import send_embed
from logging_config import logger

load_dotenv()

SIGNATURE = "Made with ❤️ from N47AN+P37ER"
MAX_ARTICLES = 60
DELAY_BETWEEN_EMBEDS = 2

def update_json_storage(articles, filename):
    """
    Simpan seluruh artikel ke file JSON untuk monitoring.
    Duplicate check diabaikan sehingga setiap run, artikel yang didapatkan
    (misalnya 20 vulnerability teratas) akan selalu dikirim.
    """
    # Pastikan file JSON ada; jika tidak, buat dengan {} sebagai isinya.
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)
    
    with open(filename, "r") as f:
        data_storage = json.load(f)
    
    # Selalu gunakan seluruh data (tidak melakukan duplicate filtering)
    new_articles = articles
    
    # Update data_storage dengan data baru (overwrite jika sudah ada)
    for article in new_articles:
        data_storage[article["title"]] = {
            "description": article.get("snippet", ""),
            "cvss": article.get("cvss", ""),
            "link": article.get("link", ""),
            "author": article.get("author", "Unknown"),
            "date": article.get("updated_at", datetime.now().isoformat())
        }
    
    with open(filename, "w") as f:
        json.dump(data_storage, f, indent=2)
    logger.info(f"{len(new_articles)} artikel diperbarui ke {filename}.")
    return new_articles

def create_embed_cve(cve):
    embed = {
        "title": f"🚨 {cve['title']}",
        "url": cve["link"],
        "description": f"💡 {cve['snippet']}",
        "color": 15158332,
        "footer": {"text": SIGNATURE},
        "fields": [
            {"name": "CVSS Score", "value": f"📊 {cve.get('cvss', 'N/A')}", "inline": True}
        ]
    }
    return embed

def create_embed_hn(article):
    embed = {
        "title": f"📰 {article['title']}",
        "url": article["link"],
        "description": f"💡 {article['snippet']}",
        "color": 3447003,
        "footer": {"text": SIGNATURE},
        "fields": [
            {"name": "Author", "value": f"👤 {article.get('author', 'Unknown')}", "inline": True},
            {"name": "Sumber", "value": "🌐 thehackernews.com", "inline": True}
        ]
    }
    return embed

def process_and_send(scraper_key, embed_title, source_type):
    scraper = ScraperFactory.get_scraper(scraper_key)
    articles = scraper.scrape()
    
    if not articles:
        logger.info(f"Tidak ada data baru untuk {embed_title}.")
        return
    
    filename = "cve.json" if source_type == "cve" else "scraped_data.json"
    # Tidak melakukan duplicate filtering; kirim apa saja data yang didapat.
    new_articles = update_json_storage(articles[:MAX_ARTICLES], filename=filename)
    
    for i, article in enumerate(new_articles, start=1):
        if source_type == "cve":
            embed = create_embed_cve(article)
        else:
            embed = create_embed_hn(article)
        send_embed(embed)
        logger.info(f"Embed {i} dikirim untuk {embed_title}. Menunggu {DELAY_BETWEEN_EMBEDS} detik...")
        time.sleep(DELAY_BETWEEN_EMBEDS)

def main():
    process_and_send("opencve", "Berita CVE & CVSS Terbaru dari OpenCVE", source_type="cve")
    process_and_send("hackernews_vulnerability", "Artikel Vulnerability dari The Hacker News", source_type="hn")
    process_and_send("hackernews_attack", "Artikel Cyber Attack dari The Hacker News", source_type="hn")

if __name__ == "__main__":
    main()
