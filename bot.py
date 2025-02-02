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
SOURCE_CHANNEL_IDA = -1002487065354  # Source channel ID A
SOURCE_CHANNEL_IDB = -1002464896968  # Source channel ID B
DESTINATION_CHANNEL_IDA = -1002487065354  # Destination channel ID A
DESTINATION_CHANNEL_IDB = -1002464896968  # Destination channel ID B

# Max stored messages aur number of messages to forward
MAX_MESSAGES_A = 10
MAX_MESSAGES_B = 10
FORWARD_MESSAGES_A = 2
FORWARD_MESSAGES_B = 2

# Deque to store messages
message_queue_A = deque(maxlen=MAX_MESSAGES_A)
message_queue_B = deque(maxlen=MAX_MESSAGES_B)

# FORWARD_INTERVAL
FORWARD_INTERVAL_A = 120  # Default: 120 seconds (2 minutes)
FORWARD_INTERVAL_B = 120  # Default: 120 seconds (2 minutes)

# Last forwarded index
last_forwarded_index_A = 0
last_forwarded_index_B = 0

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
        if len(message_queue_A) == MAX_MESSAGES_A:
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
        if len(message_queue_B) == MAX_MESSAGES_B:
            message_queue_B.popleft()  # Remove the oldest message
            last_forwarded_index_B -= 1  # Adjust the last forwarded index
        message_queue_B.append(message_data)
        # Reset forwarding if we are at the end of the queue
        if last_forwarded_index_B >= len(message_queue_B):
            last_forwarded_index_B = 0

# Message forward karne ka function
# Message forward karne ka function A
def forward_messages_A(context):
    global last_forwarded_index_A
    try:
        if message_queue_A:
            forwarded_count = 0
            while forwarded_count < FORWARD_MESSAGES_A and last_forwarded_index_A < len(message_queue_A):
                message_data = message_queue_A[last_forwarded_index_A]
                if message_data['media']:
                    context.bot.send_photo(chat_id=DESTINATION_CHANNEL_IDA, photo=message_data['media'], caption=message_data['text'])
                else:
                    context.bot.send_message(chat_id=DESTINATION_CHANNEL_IDA, text=message_data['text'])
                last_forwarded_index_A += 1
                forwarded_count += 1
            # Reset the index to start from the beginning after all messages have been forwarded
            if last_forwarded_index_A >= len(message_queue_A):
                last_forwarded_index_A = 0  # Start from the beginning
                if not message_queue_A:  # Check if message_queue is empty
                    context.job_queue.run_once(forward_messages_A, when=FORWARD_INTERVAL_A)
                else:
                    context.job_queue.run_once(forward_messages_A, when=FORWARD_INTERVAL_A)
            else:
                context.job_queue.run_once(forward_messages_A, when=FORWARD_INTERVAL_A)
        else:
            context.job_queue.run_once(forward_messages_A, when=FORWARD_INTERVAL_A)
    except NetworkError:
        logger.error('NetworkError: Unable to send messages due to network issues. Retrying...')
        context.job_queue.run_once(forward_messages_A, when=FORWARD_INTERVAL_A)

# Message forward karne ka function B
def forward_messages_B(context):
    global last_forwarded_index_B
    try:
        if message_queue_B:
            forwarded_count = 0
            while forwarded_count < FORWARD_MESSAGES_B and last_forwarded_index_B < len(message_queue_B):
                message_data = message_queue_B[last_forwarded_index_B]
                if message_data['media']:
                    context.bot.send_photo(chat_id=DESTINATION_CHANNEL_IDB, photo=message_data['media'], caption=message_data['text'])
                else:
                    context.bot.send_message(chat_id=DESTINATION_CHANNEL_IDB, text=message_data['text'])
                last_forwarded_index_B += 1
                forwarded_count += 1
            # Reset the index to start from the beginning after all messages have been forwarded
            if last_forwarded_index_B >= len(message_queue_B):
                last_forwarded_index_B = 0  # Start from the beginning
                if not message_queue_B:  # Check if message_queue is empty
                    context.job_queue.run_once(forward_messages_B, when=FORWARD_INTERVAL_B)
                else:
                    context.job_queue.run_once(forward_messages_B, when=FORWARD_INTERVAL_B)
            else:
                context.job_queue.run_once(forward_messages_B, when=FORWARD_INTERVAL_B)
        else:
            context.job_queue.run_once(forward_messages_B, when=FORWARD_INTERVAL_B)
    except NetworkError:
        logger.error('NetworkError: Unable to send messages due to network issues. Retrying...')
        context.job_queue.run_once(forward_messages_B, when=FORWARD_INTERVAL_B)
        
# Error handle karne ka function
def error_handler(update, context):
    try:
        raise context.error
    except Conflict:
        logger.error('Conflict: Another instance of the bot is running.')
    except NetworkError:
        logger.error('NetworkError: Unable to send messages due to network issues.')

# Time update karne ka function A
def set_interval_A(update, context):
    global FORWARD_INTERVAL_A
    try:
        new_interval = int(context.args[0]) * 60  # Minutes to seconds conversion
        FORWARD_INTERVAL_A = new_interval
        context.job_queue.run_once(forward_messages_A, when=FORWARD_INTERVAL_A)
        update.message.reply_text(f'Interval set to {context.args[0]} minutes for channel A.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /setintervalA <minutes>')

# Time update karne ka function B
def set_interval_B(update, context):
    global FORWARD_INTERVAL_B
    try:
        new_interval = int(context.args[0]) * 60  # Minutes to seconds conversion
        FORWARD_INTERVAL_B = new_interval
        context.job_queue.run_once(forward_messages_B, when=FORWARD_INTERVAL_B)
        update.message.reply_text(f'Interval set to {context.args[0]} minutes for channel B.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /setintervalB <minutes>')

# Scheduler set karne ka function
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.chat(SOURCE_CHANNEL_IDA), handle_message_A))
    dispatcher.add_handler(MessageHandler(Filters.chat(SOURCE_CHANNEL_IDB), handle_message_B))
    dispatcher.add_handler(CommandHandler('setintervalA', set_interval_A))
    dispatcher.add_handler(CommandHandler('setintervalB', set_interval_B))
    dispatcher.add_error_handler(error_handler)  # Add error handler

    # Job queue me function schedule karna
    job_queue = updater.job_queue
    job_queue.run_once(forward_messages_A, when=FORWARD_INTERVAL_A)
    job_queue.run_once(forward_messages_B, when=FORWARD_INTERVAL_B)

    # Bot ko start karne ka function
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
