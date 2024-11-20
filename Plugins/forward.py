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
                    terabox_links = [word for word in message.text.split() if "terabox" in word]

                # Skip the message if no Terabox links are found
                if not terabox_links:
                    logger.info(f"Skipped message from {from_channel} as no Terabox links were found")
                    continue

                # Format the caption with Terabox links only
                caption = ""
                for i, link in enumerate(terabox_links, start=1):
                    caption += f"Video {i} - {link}\n"

                # Send media thumbnail with formatted caption
                if message.photo:
                    photo_file = message.photo.file_id
                    await client.send_photo(int(to_channel), photo=photo_file, caption=caption.strip())
                elif message.video:
                    video_file = message.video.file_id
                    await client.send_video(int(to_channel), video=video_file, caption=caption.strip())
                elif message.document:
                    document_file = message.document.file_id
                    await client.send_document(int(to_channel), document=document_file, caption=caption.strip())
                else:
                    # Edit text message
                    modified_text = f"{message.text}\n\n{caption.strip()}"
                    await client.send_message(int(to_channel), text=modified_text)

                logger.info(f"Forwarded a modified message with media and Terabox links from {from_channel} to {to_channel}")
                await asyncio.sleep(1)
    except Exception as e:
        logger.exception(e)
