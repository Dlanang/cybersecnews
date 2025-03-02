# discord_webhook.py
import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

logger = logging.getLogger(__name__)

def send_embed(embeds):
    """Mengirim pesan embed ke Discord dengan batas maksimal 10 embed."""
    if len(embeds) > 10:
        logger.warning("Terlalu banyak embed. Hanya 10 embed pertama yang akan dikirim.")
        embeds = embeds[:10]
    
    data = {"embeds": embeds}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
        response.raise_for_status()
        logger.info("Pesan embed berhasil dikirim ke Discord!")
    except Exception as e:
        logger.error(f"Error sending embed to Discord: {e}")
