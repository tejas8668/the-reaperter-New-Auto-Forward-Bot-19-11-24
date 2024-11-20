import logging
import asyncio
import re
import requests
from pyrogram import filters
from bot import channelforward
from config import Config

logger = logging.getLogger(__name__)

# Function to shorten URLs using GPLinks
def shorten_url(url):
    api_url = 'https://gplinks.in/api'
    api_key = '89e6e36b347f3db3f187dda37290c5927e99c18a'  # Replace with your GPLinks API key
    params = {
        'api': api_key,
        'url': url
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            return data['shortenedUrl']
    logger.error(f"Failed to shorten URL: {url}")
    return url

@channelforward.on_message(filters.channel)
async def forward(client, message):
    try:
        for id in Config.CHANNEL:
            from_channel, to_channel = id.split(":")
            if message.chat.id == int(from_channel):
                # Extract Terabox links using regex to handle various formats
                text = message.caption or message.text or ""
                terabox_links = re.findall(r'https://1024terabox.com/s/\S+', text)

                # Shorten Terabox links
                shortened_links = [shorten_url(link) for link in terabox_links]

                # Format the caption with shortened Terabox links labeled as Video 1, Video 2, etc.
                caption = ""
                for i, link in enumerate(shortened_links, start=1):
                    caption += f"Video {i} - {link}\n\n"

                # Send media thumbnail with formatted caption
                if message.photo:
                    await client.send_photo(int(to_channel), message.photo.file_id, caption=caption.strip())
                elif message.video:
                    await client.send_video(int(to_channel), message.video.file_id, caption=caption.strip())
                elif message.document:
                    await client.send_document(int(to_channel), message.document.file_id, caption=caption.strip())
                else:
                    # Send text message with only shortened Terabox links
                    await client.send_message(int(to_channel), text=caption.strip())

                logger.info(f"Forwarded a modified message with media and shortened Terabox links from {from_channel} to {to_channel}")
                await asyncio.sleep(1)
    except Exception as e:
        logger.exception(e)
