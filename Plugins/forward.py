import logging
import asyncio
import re
import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
import requests

def shorten_url_adrinolinks(url):
    api_url = 'https://clickspay.in/api'
    api_key = '2be0849743f9dae76487a66551105da32b68165f'
    params = {
        'api': api_key,
        'url': url
    }
    # Yahan pe custom certificate bundle ka path specify karo
    response = requests.get(api_url, params=params, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            logger.info(f"Adrinolinks shortened URL: {data['shortenedUrl']}")
            return data['shortenedUrl']
    logger.error(f"Failed to shorten URL with Adrinolinks: {url}")
    return url


# Function to shorten URLs using URLStox
def shorten_url_urlstox(url):
    api_url = 'https://arolinks.com/api'
    api_key = '90bcb2590cca0a2b438a66e178f5e90fea2dc8b4'
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
    # Instead of shortening, just return the original URL
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
                terabox_links = re.findall(r'https://1024terabox.com/s/\S+|https://terafileshare.com/s/\S+|https://teraboxapp.com/s/\S+|https://terasharelink.com/s/\S+|https://teraboxlink.com/s/\S+', text)
                logger.info(f"Found Terabox links for {group_name}: {terabox_links}")

                # Skip message if no Terabox links are found
                if not terabox_links:
                    logger.info(f"No Terabox links found for {group_name}. Skipping message.")
                    return

                # Shorten Terabox links using the specified shortener function
                shortened_links = [shortener_func(link) for link in terabox_links]
                logger.info(f"Shortened links for {group_name}: {shortened_links}")

                # Format the caption with shortened Terabox links labeled as Video 1, Video 2, etc.
                header = "📥 **𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐋𝐢𝐧𝐤𝐬/👀𝐖𝐚𝐭𝐜𝐡 𝐎𝐧𝐥𝐢𝐧𝐞** 🚀\n\n"
                footer = "\n**❗Watch Terabox Video Link Without Ads❗️**\nhttps://t.me/TeraBox_Stream_Link_Bot\n\nSouth Hindi Movies\nhttps://t.me/+yN4HIeD6QP5hNmQ1"
                # Generate the caption for multiple video links
                caption = ""
                for i, link in enumerate(shortened_links, start=1):
                    caption += f"**Video {i} -** {link}\n\n"

                # Combine header, caption, and footer
                full_caption = f"{header}{caption}{footer}"
                    # Create an inline keyboard button for "How To Download"
                reply_markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("How To Download", url="https://t.me/how_to_download_0011")
                        ],[
                            InlineKeyboardButton("Join Group", url="https://t.me/a_movies_request_group")
                        ],[
                            InlineKeyboardButton("HollyWood Movies", url="https://t.me/+OXjXqutoKyI5ZTM1")
                        ],[
                            InlineKeyboardButton("18+", url="https://t.me/+-S4ZEZhKrSZlYWZl")
                        ]
                    ]
                )

                # Prepare the tasks for sending messages
                tasks = []
                if message.photo or message.video or message.document or message.text:
                    for destination in destination_channels:
                        if destination:
                            try:
                                if message.photo:
                                    tasks.append(client.send_photo(int(destination), message.photo.file_id, caption=full_caption.strip(), reply_markup=reply_markup))
                                elif message.video:
                                    tasks.append(client.send_video(int(destination), message.video.file_id, caption=full_caption.strip(), reply_markup=reply_markup))
                                elif message.document:
                                    tasks.append(client.send_document(int(destination), message.document.file_id, caption=full_caption.strip(), reply_markup=reply_markup))
                                else:
                                    tasks.append(client.send_message(int(destination), text=full_caption.strip(), reply_markup=reply_markup))
                            except ValueError as ve:
                                logger.error(f"Failed to process destination '{destination}' for {group_name}: {ve}")

                # Run all tasks concurrently for faster processing
                await asyncio.gather(*tasks)
                logger.info(f"Forwarded a modified message with media and shortened Terabox links to {group_name}")

        # Process each group individually with explicit handling and different shorteners
        if message.chat.id in map(int, Config.CHANNELS["group_A"]["sources"]):
            await process_group(Config.CHANNELS["group_A"]["sources"], Config.CHANNELS["group_A"]["destinations"], shorten_url_urlstox, "group_A")
        elif message.chat.id in map(int, Config.CHANNELS["group_B"]["sources"]):
            await process_group(Config.CHANNELS["group_B"]["sources"], Config.CHANNELS["group_B"]["destinations"], shorten_url_urlstox, "group_B")
        elif message.chat.id in map(int, Config.CHANNELS["group_C"]["sources"]):
            await process_group(Config.CHANNELS["group_C"]["sources"], Config.CHANNELS["group_C"]["destinations"], shorten_url_nanolinks, "group_C")
        elif message.chat.id in map(int, Config.CHANNELS["group_D"]["sources"]):
            await process_group(Config.CHANNELS["group_D"]["sources"], Config.CHANNELS["group_D"]["destinations"], shorten_url_urlstox, "group_D")

    except Exception as e:
        logger.exception(e)
