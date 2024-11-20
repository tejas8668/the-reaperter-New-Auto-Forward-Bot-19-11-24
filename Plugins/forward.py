import logging
import asyncio
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
                # Extract Terabox links
                terabox_links = []
                if message.text:
                    terabox_links = [word for word in message.text.split() if "terabox.com" in word]

                # Skip the message if no Terabox links are found
                if not terabox_links:
                    logger.info(f"Skipped message from {from_channel} as no Terabox links were found")
                    continue

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
                    # Edit text message
                    await client.send_message(int(to_channel), text=caption.strip())

                logger.info(f"Forwarded a modified message with media and Terabox links from {from_channel} to {to_channel}")
                await asyncio.sleep(1)
    except Exception as e:
        logger.exception(e)
