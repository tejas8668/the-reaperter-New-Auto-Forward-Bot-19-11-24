import logging
import asyncio
import re
import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot import channelforward
from config import Config
from pyrogram import Client

client = Client("my_bot")

logger = logging.getLogger(__name__)

# Initialize message store for Group A
group_a_message_store = []

# Define the shortener function
def shortener_func(link):
    # Replace this with your actual shortener function
    return link

@channelforward.on_message(filters.channel)
async def forward(client, message):
    try:
        # Function to process messages for a specific group
        async def process_group(source_channels, destination_channels, group_name):
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
                footer = "\n**❗Watch Terabox Video Link Without Ads❗️**\nhttps://t.me/TeraBox_Stream_Link_Bot\n\nSouth Hindi Movies\nhttps://t.me/+yN4HIeD6QP5hNmQ1\n\nHollyWood Adult Movies\nhttps://t.me/+kxAp1WCn6ggzZTFl"
                # Generate the caption for multiple video links
                caption = ""
                for i, link in enumerate(shortened_links, start=1):
                    caption += f"**Video {i} -** [Click Here]({link})\n\n"

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
                            InlineKeyboardButton("18+", url="https://t.me/+0fTvALJF4epiMDI9")
                        ]
                    ]
                )

                # Store the message in the Group A message store
                store_message(message, full_caption, reply_markup)

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
            await process_group(Config.CHANNELS["group_A"]["sources"], Config.CHANNELS["group_A"]["destinations"], "Group A")
        elif message.chat.id in map(int, Config.CHANNELS["group_B"]["sources"]):
            await process_group(Config.CHANNELS["group_B"]["sources"], Config.CHANNELS["group_B"]["destinations"], "Group B")
        elif message.chat.id in map(int, Config.CHANNELS["group_C"]["sources"]):
            await process_group(Config.CHANNELS["group_C"]["sources"], Config.CHANNELS["group_C"]["destinations"], "Group C")
        elif message.chat.id in map(int, Config.CHANNELS["group_D"]["sources"]):
            await process_group(Config.CHANNELS["group_D"]["sources"], Config.CHANNELS["group_D"]["destinations"], "Group D")

    except Exception as e:
        logger.exception(e)

def store_message(message, caption, reply_markup):
    global group_a_message_store
    if len(group_a_message_store) >= 100:
        group_a_message_store.pop(0)  # Remove the oldest message
    group_a_message_store.append((message, caption, reply_markup))

async def send_stored_messages(client):
    global group_a_message_store
    while True:
        if group_a_message_store:
            for _ in range(min(4, len(group_a_message_store))):
                message, caption, reply_markup = group_a_message_store.pop(0)
                for destination in Config.CHANNELS["group_A"]["destinations"]:
                    if destination:
                        try:
                            if message.photo:
                                await client.send_photo(int(destination), message.photo.file_id, caption=caption.strip(), reply_markup=reply_markup)
                            elif message.video:
                                await client.send_video(int(destination), message.video.file_id, caption=caption.strip(), reply_markup=reply_markup)
                            elif message.document:
                                await client.send_document(int(destination), message.document.file_id, caption=caption.strip(), reply_markup=reply_markup)
                            else:
                                await client.send_message(int(destination), text=caption.strip(), reply_markup=reply_markup)
                        except ValueError as ve:
                            logger.error(f"Failed to process destination '{destination}' for Group A: {ve}")
        await asyncio.sleep(3600)  # Wait for 1 hour

# Start the task to send stored messages
client.loop.create_task(send_stored_messages(client))
