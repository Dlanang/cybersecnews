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

def is_article_already_sent(article_id, data_storage):
    return article_id in data_storage

def update_json_storage(articles):
    data_file = "scraped_data.json"
    if os.path.exists(data_file):
        with open(data_file, "r") as f:
            data_storage = json.load(f)
    else:
        data_storage = {}
    
    new_articles = [article for article in articles if not is_article_already_sent(article["title"], data_storage)]
    for article in new_articles:
        data_storage[article["title"]] = {
            "description": article["snippet"],
            "cvss": article.get("cvss", ""),
            "link": article["link"],
            "author": article.get("author", "Unknown"),
            "date": datetime.now().isoformat()
        }
    
    with open(data_file, "w") as f:
        json.dump(data_storage, f, indent=2)
    logger.info(f"{len(new_articles)} artikel baru ditambahkan.")
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
    
    new_articles = update_json_storage(articles[:MAX_ARTICLES])
    if not new_articles:
        logger.info(f"Semua artikel untuk {embed_title} sudah pernah dikirim.")
        return
    
    for i, article in enumerate(new_articles, start=1):
        if source_type == "cve":
            embed = create_embed_cve(article)
        else:
            embed = create_embed_hn(article)
        send_embed(embed)
        logger.info(f"Embed {i} dikirim untuk {embed_title}. Menunggu {DELAY_BETWEEN_EMBEDS} detik...")
        time.sleep(DELAY_BETWEEN_EMBEDS)

def main():
    # Data CVE dari OpenCVE
    process_and_send("opencve", "Berita CVE & CVSS Terbaru dari OpenCVE", source_type="cve")
    # Artikel dari HackerNews Vulnerability
    process_and_send("hackernews_vulnerability", "Artikel Vulnerability dari The Hacker News", source_type="hn")
    # Artikel dari HackerNews Cyber Attack
    process_and_send("hackernews_attack", "Artikel Cyber Attack dari The Hacker News", source_type="hn")

if __name__ == "__main__":
    main()
