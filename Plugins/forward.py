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
    api_key = 'YOUR_API_KEY'  # Replace with your GPLinks API key
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
        # Iterate through each group
        for group_name, channels in Config.CHANNELS.items():
            # Check if the message is from one of the source channels in the group
            if message.chat.id in map(int, channels['sources']):
                # Extract Terabox links using regex to handle various formats
                text = message.caption or message.text or ""
                terabox_links = re.findall(r'https://1024terabox.com/s/\S+', text)

                # Shorten Terabox links
                shortened_links = [shorten_url(link) for link in terabox_links]

                # Format the caption with shortened Terabox links labeled as Video 1, Video 2, etc.
                caption = ""
                for i, link in enumerate(shortened_links, start=1):
                    caption += f"Video {i} - {link}\n\n"

                # Prepare the tasks for sending messages
                tasks = []
                if message.photo:
                    for destination in channels['destinations']:
                        tasks.append(client.send_photo(int(destination), message.photo.file_id, caption=caption.strip()))
                elif message.video:
                    for destination in channels['destinations']:
                        tasks.append(client.send_video(int(destination), message.video.file_id, caption=caption.strip()))
                elif message.document:
                    for destination in channels['destinations']:
                        tasks.append(client.send_document(int(destination), message.document.file_id, caption=caption.strip()))
                else:
                    # Send text message with only shortened Terabox links
                    for destination in channels['destinations']:
                        tasks.append(client.send_message(int(destination), text=caption.strip()))

                # Run all tasks concurrently for faster processing
                await asyncio.gather(*tasks)

                logger.info(f"Forwarded a modified message with media and shortened Terabox links from {group_name}")
                await asyncio.sleep(1)
    except Exception as e:
        logger.exception(e)
