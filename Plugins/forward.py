import logging
import asyncio
import re
from pyrogram import filters
from bot import channelforward
from config import Config

logger = logging.getLogger(__name__)

@channelforward.on_message(filters.channel)
async def forward(client, message):
    try:
        for id in Config.CHANNEL:
            from_channel, to_channel = id.split(":")
            if message.chat.id == int(from_channel):
                # Extract Terabox links using regex to handle various formats
                text = message.text or ""
                terabox_links = re.findall(r'https://1024terabox.com/s/\S+', text)

                # Format the caption with Terabox links only
                caption = "\n".join(terabox_links)

                # Send media thumbnail with formatted caption
                if message.photo:
                    await client.send_photo(int(to_channel), message.photo.file_id, caption=caption.strip())
                elif message.video:
                    await client.send_video(int(to_channel), message.video.file_id, caption=caption.strip())
                elif message.document:
                    await client.send_document(int(to_channel), message.document.file_id, caption=caption.strip())
                else:
                    # Send text message with only Terabox links
                    await client.send_message(int(to_channel), text=caption.strip())

                logger.info(f"Forwarded a modified message with media and Terabox links from {from_channel} to {to_channel}")
                await asyncio.sleep(1)
    except Exception as e:
        logger.exception(e)
