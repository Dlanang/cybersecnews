import os
import requests
from dotenv import load_dotenv
from logging_config import logger

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_embed(embed):
    data = {"embeds": [embed]}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
        response.raise_for_status()
        logger.info("Embed berhasil dikirim ke Discord!")
    except Exception as e:
        logger.error(f"Error mengirim embed ke Discord: {e}")
