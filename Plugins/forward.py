import logging
import asyncio
import re
import requests
from pyrogram import filters
from bot import channelforward
from config import Config

logger = logging.getLogger(__name__)

# Function to shorten URLs using GPLinks
def shorten_url_gplinks(url):
    api_url = 'https://gplinks.in/api'
    api_key = '89e6e36b347f3db3f187dda37290c5927e99c18a'
    params = {
        'api': api_key,
        'url': url
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            logger.info(f"GPLinks shortened URL: {data['shortenedUrl']}")
            return data['shortenedUrl']
    logger.error(f"Failed to shorten URL with GPLinks: {url}")
    return url

# Function to shorten URLs using Adrinolinks
def shorten_url_adrinolinks(url):
    api_url = 'https://adrinolinks.in/api'
    api_key = '599ee2c148d46fe9061578db049f3cd32f528bf6'
    params = {
        'api': api_key,
        'url': url
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            logger.info(f"Adrinolinks shortened URL: {data['shortenedUrl']}")
            return data['shortenedUrl']
    logger.error(f"Failed to shorten URL with Adrinolinks: {url}")
    return url

# Function to shorten URLs using URLStox
def shorten_url_urlstox(url):
    api_url = 'https://urlstox.com/api'
    api_key = 'a9b9102d1c71b90ca824090cb869334f596774ac'
    params = {
        'api': api_key,
        'url': url
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            logger.info(f"URLStox shortened URL: {data['shortenedUrl']}")
            return data['shortenedUrl']
    logger.error(f"Failed to shorten URL with URLStox: {url}")
    return url

# Function to shorten URLs using NanoLinks
def shorten_url_nanolinks(url):
    api_url = 'https://nanolinks.in/api'
    api_key = 'a1207f2847c4499f4d83b03320656157f8b4a1be'
    params = {
        'api': api_key,
        'url': url
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            logger.info(f"NanoLinks shortened URL: {data['shortenedUrl']}")
            return data['shortenedUrl']
    logger.error(f"Failed to shorten URL with NanoLinks: {url}")
    return url

@channelforward.on_message(filters.channel)
async def forward(client, message):
    try:
        # Function to process messages for a specific group
        async def process_group(source_channels, destination_channels, shortener_func, group_name):
            logger.info(f"Processing message for {group_name}")
            if message.chat.id in map(int, source_channels):
                # Extract Terabox links using regex to handle various formats
                text = message.caption or message.text or ""
                logger.info(f"Message text for {group_name}: {text}")
                terabox_links = re.findall(r'https://1024terabox.com/s/\S+|https://terafileshare.com/s/\S+', text)
                logger.info(f"Found Terabox links for {group_name}: {terabox_links}")

                # Shorten Terabox links using the specified shortener function
                shortened_links = [shortener_func(link) for link in terabox_links]
                logger.info(f"Shortened links for {group_name}: {shortened_links}")

                # Format the caption with shortened Terabox links labeled as Video 1, Video 2, etc.
                caption = ""
                for i, link in enumerate(shortened_links, start=1):
                    caption += f"Video {i} - {link}\n\n"

                # Prepare the tasks for sending messages
                tasks = []
                if message.photo:
                    for destination in destination_channels:
                        if destination:
                            try:
                                tasks.append(client.send_photo(int(destination), message.photo.file_id, caption=caption.strip()))
                            except ValueError as ve:
                                logger.error(f"Failed to process destination '{destination}' for {group_name}: {ve}")
                elif message.video:
                    for destination in destination_channels:
                        if destination:
                            try:
                                tasks.append(client.send_video(int(destination), message.video.file_id, caption=caption.strip()))
                            except ValueError as ve:
                                logger.error(f"Failed to process destination '{destination}' for {group_name}: {ve}")
                elif message.document:
                    for destination in destination_channels:
                        if destination:
                            try:
                                tasks.append(client.send_document(int(destination), message.document.file_id, caption=caption.strip()))
                            except ValueError as ve:
                                logger.error(f"Failed to process destination '{destination}' for {group_name}: {ve}")
                else:
                    for destination in destination_channels:
                        if destination:
                            try:
                                tasks.append(client.send_message(int(destination), text=caption.strip()))
                            except ValueError as ve:
                                logger.error(f"Failed to process destination '{destination}' for {group_name}: {ve}")

                # Run all tasks concurrently for faster processing
                await asyncio.gather(*tasks)
                logger.info(f"Forwarded a modified message with media and shortened Terabox links to {group_name}")

        # Process each group individually with explicit handling and different shorteners
        if message.chat.id in map(int, Config.CHANNELS["group_A"]["sources"]):
            await process_group(Config.CHANNELS["group_A"]["sources"], Config.CHANNELS["group_A"]["destinations"], shorten_url_gplinks, "group_A")
        elif message.chat.id in map(int, Config.CHANNELS["group_B"]["sources"]):
            await process_group(Config.CHANNELS["group_B"]["sources"], Config.CHANNELS["group_B"]["destinations"], shorten_url_adrinolinks, "group_B")
        elif message.chat.id in map(int, Config.CHANNELS["group_C"]["sources"]):
            await process_group(Config.CHANNELS["group_C"]["sources"], Config.CHANNELS["group_C"]["destinations"], shorten_url_urlstox, "group_C")
        elif message.chat.id in map(int, Config.CHANNELS["group_D"]["sources"]):
            await process_group(Config.CHANNELS["group_D"]["sources"], Config.CHANNELS["group_D"]["destinations"], shorten_url_nanolinks, "group_D")

    except Exception as e:
        logger.exception(e)
