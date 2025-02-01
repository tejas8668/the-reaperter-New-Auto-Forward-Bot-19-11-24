import os
from dotenv import load_dotenv
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram.error import NetworkError, Conflict
from collections import deque
import logging

# Environment variable load karen
load_dotenv()

# Bot token yahan environment variable se lein
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Source aur destination channel ID yahan daalein
SOURCE_CHANNEL_ID_A = -1002487065354  # Source channel ID A
DESTINATION_CHANNEL_ID_A = -1002464896968  # Destination channel ID A

SOURCE_CHANNEL_ID_B = -1002487065355  # Source channel ID B
DESTINATION_CHANNEL_ID_B = -1002464896969  # Destination channel ID B

# Max stored messages aur number of messages to forward
MAX_MESSAGES = 10
FORWARD_MESSAGES = 2

# Deque to store messages
message_queue_A = deque(maxlen=MAX_MESSAGES)
message_queue_B = deque(maxlen=MAX_MESSAGES)

# Last forwarded index
last_forwarded_index_A = 0
last_forwarded_index_B = 0

# FORWARD_INTERVAL
FORWARD_INTERVAL = 120  # Default: 120 seconds (2 minutes)

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Message handle karne ka function A
def handle_message_A(update, context):
    global last_forwarded_index_A
    if update.channel_post:
        message_data = {
            'text': update.channel_post.caption or update.channel_post.text,
            'media': update.channel_post.photo[-1].file_id if update.channel_post.photo else None
        }
        # Add new message to the end and remove oldest messages if the max size is exceeded
        if len(message_queue_A) == MAX_MESSAGES:
            message_queue_A.popleft()  # Remove the oldest message
            last_forwarded_index_A -= 1  # Adjust the last forwarded index
        message_queue_A.append(message_data)
        # Reset forwarding if we are at the end of the queue
        if last_forwarded_index_A >= len(message_queue_A):
            last_forwarded_index_A = 0

# Message handle karne ka function B
def handle_message_B(update, context):
    global last_forwarded_index_B
    if update.channel_post:
        message_data = {
            'text': update.channel_post.caption or update.channel_post.text,
            'media': update.channel_post.photo[-1].file_id if update.channel_post.photo else None
        }
        # Add new message to the end and remove oldest messages if the max size is exceeded
        if len(message_queue_B) == MAX_MESSAGES:
            message_queue_B.popleft()  # Remove the oldest message
            last_forwarded_index_B -= 1  # Adjust the last forwarded index
        message_queue_B.append(message_data)
        # Reset forwarding if we are at the end of the queue
        if last_forwarded_index_B >= len(message_queue_B):
            last_forwarded_index_B = 0

# Message forward karne ka function A
def forward_messages_A(context):
    global last_forwarded_index_A
    try:
        if message_queue_A:
            forwarded_count = 0
            while forwarded_count < FORWARD_MESSAGES and last_forwarded_index_A < len(message_queue_A):
                message_data = message_queue_A[last_forwarded_index_A]
                if message_data['media']:
                    context.bot.send_photo(chat_id=DESTINATION_CHANNEL_ID_A, photo=message_data['media'], caption=message_data['text'])
                else:
                    context.bot.send_message(chat_id=DESTINATION_CHANNEL_ID_A, text=message_data['text'])
                last_forwarded_index_A += 1
                forwarded_count += 1
            # Reset the index to start from the beginning after all messages have been forwarded
            if last_forwarded_index_A >= len(message_queue_A):
                last_forwarded_index_A = 0  # Start from the beginning
            else:
                context.job_queue.run_once(forward_messages_A, when=FORWARD_INTERVAL)
        else:
            context.job_queue.run_once(forward_messages_A, when=FORWARD_INTERVAL)
    except NetworkError:
        logger.error('NetworkError: Unable to send messages due to network issues. Retrying...')
        context.job_queue.run_once(forward_messages_A, when=FORWARD_INTERVAL)

# Message forward karne ka function B
def forward_messages_B(context):
    global last_forwarded_index_B
    try:
        if message_queue_B:
            forwarded_count = 0
            while forwarded_count < FORWARD_MESSAGES and last_forwarded_index_B < len(message_queue_B):
                message_data = message_queue_B[last_forwarded_index_B]
                if message_data['media']:
                    context.bot.send_photo(chat_id=DESTINATION_CHANNEL_ID_B, photo=message_data['media'], caption=message_data['text'])
                else:
                    context.bot.send_message(chat_id=DESTINATION_CHANNEL_ID_B, text=message_data['text'])
                last_forwarded_index_B += 1
                forwarded_count += 1
            # Reset the index to start from the beginning after all messages have been forwarded
            if last_forwarded_index_B >= len(message_queue_B):
                last_forwarded_index_B = 0  # Start from the beginning
            else:
                context.job_queue.run_once(forward_messages_B, when=FORWARD_INTERVAL)
        else:
            context.job_queue.run_once(forward_messages_B, when=FORWARD_INTERVAL)
    except NetworkError:
        logger.error('NetworkError: Unable to send messages due to network issues. Retrying...')
        context.job_queue.run_once(forward_messages_B, when=FORWARD_INTERVAL)

# Error handle karne ka function
def error_handler(update, context):
    try:
        raise context.error
    except Conflict:
        logger.error('Conflict: Another instance of the bot is running.')
    except NetworkError:
        logger.error('NetworkError: Unable to send messages due to network issues.')

# Time update karne ka function
def set_interval(update, context):
    global FORWARD_INTERVAL
    try:
        new_interval = int(context.args[0]) * 60  # Minutes to seconds conversion
        FORWARD_INTERVAL = new_interval
        context.job_queue.run_once(forward_messages_A, when=FORWARD_INTERVAL)
        context.job_queue.run_once(forward_messages_B, when=FORWARD_INTERVAL)
        update.message.reply_text(f'Interval set to {context.args[0]} minutes.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /setinterval <minutes>')

# Scheduler set karne ka function
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.chat(SOURCE_CHANNEL_ID_A), handle_message_A))
    dispatcher.add_handler(MessageHandler(Filters.chat(SOURCE_CHANNEL_ID_B), handle_message_B))
    dispatcher.add_handler(CommandHandler('setinterval', set_interval))
    dispatcher.add_error_handler(error_handler)  # Add error handler

    # Job queue me function schedule karna
    job_queue = updater.job_queue
    job_queue.run_once(forward_messages_A, when=FORWARD_INTERVAL)
    job_queue.run_once(forward_messages_B, when=FORWARD_INTERVAL)

    # Bot ko start karne ka function
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
