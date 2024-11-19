import logging
import asyncio
from pyrogram import filters
from bot import channelforward
from config import Config

logger = logging.getLogger(__name__)

@channelforward.on_message(filters.channel)
async def forward(client, message):
    # Forwarding the messages to the channel
    try:
        for id in Config.CHANNEL:
            from_channel, to_channel = id.split(":")
            # Replace 'm' with 'message' to avoid the undefined variable error
            if message.chat.id == int(from_channel):
                func = message.copy if AS_COPY else message.forward
                await func(int(to_channel), as_copy=True)
                logger.info(f"Forwarded a message from {from_channel} to {to_channel}")
                await asyncio.sleep(1)
    except Exception as e:
        logger.exception(e)
