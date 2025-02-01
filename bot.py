'''
import os
from dotenv import load_dotenv
import time
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram.error import NetworkError, Conflict
from collections import deque
import logging

# Environment variable load karen
load_dotenv()

# Bot token yahan environment variable se lein
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Source aur destination channel ID yahan daalein
SOURCE_CHANNEL_ID = -1002487065354  # Source channel ID
DESTINATION_CHANNEL_ID = -1002464896968  # Destination channel ID

# Max stored messages aur number of messages to forward
MAX_MESSAGES = 10
FORWARD_MESSAGES = 2

# Deque to store messages
message_queue = deque(maxlen=MAX_MESSAGES)
FORWARD_INTERVAL = 60  # Default: 2 minutes (in seconds)
last_forwarded_index = 0  # Keep track of the last forwarded message index

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Message handle karne ka function
def handle_message(update, context):
    global last_forwarded_index
    if update.channel_post:
        message_data = {
            'text': update.channel_post.caption or update.channel_post.text,
            'media': update.channel_post.photo[-1].file_id if update.channel_post.photo else None
        }
        # Add new message to the end and remove oldest messages if the max size is exceeded
        if len(message_queue) == MAX_MESSAGES:
            message_queue.popleft()  # Remove the oldest message
            last_forwarded_index -= 1  # Adjust the last forwarded index
        message_queue.append(message_data)
        # Reset forwarding if we are at the end of the queue
        if last_forwarded_index >= len(message_queue):
            last_forwarded_index = 0

# Message forward karne ka function
def forward_messages(context):
    global last_forwarded_index
    try:
        if message_queue:
            for _ in range(FORWARD_MESSAGES):
                if last_forwarded_index < len(message_queue):
                    message_data = message_queue[last_forwarded_index]
                    if message_data['media']:
                        context.bot.send_photo(chat_id=DESTINATION_CHANNEL_ID, photo=message_data['media'], caption=message_data['text'])
                    else:
                        context.bot.send_message(chat_id=DESTINATION_CHANNEL_ID, text=message_data['text'])
                    last_forwarded_index += 1
                else:
                    break
            # Schedule the next forward cycle only once the current forwarding completes
            context.job_queue.run_once(forward_messages, when=FORWARD_INTERVAL)
            if last_forwarded_index >= len(message_queue):
                last_forwarded_index = 0  # Reset the index to start from the beginning again
    except NetworkError:
        logger.error('NetworkError: Unable to send messages due to network issues. Retrying...')
        context.job_queue.run_once(forward_messages, when=FORWARD_INTERVAL)

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
        context.job_queue.run_once(forward_messages, when=FORWARD_INTERVAL)
        update.message.reply_text(f'Interval set to {context.args[0]} minutes.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /setinterval <minutes>')

# Scheduler set karne ka function
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.chat(SOURCE_CHANNEL_ID), handle_message))
    dispatcher.add_handler(CommandHandler('setinterval', set_interval))
    dispatcher.add_error_handler(error_handler)  # Add error handler

    # Job queue me function schedule karna
    job_queue = updater.job_queue
    job_queue.run_repeating(forward_messages, interval=FORWARD_INTERVAL, first=0)

    # Bot ko start karne ka function
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()




'''
import os
from dotenv import load_dotenv
import time
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from collections import deque
import logging

# Environment variable load karen
load_dotenv()

# Bot token yahan environment variable se lein
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Source aur destination channel ID yahan daalein
SOURCE_CHANNEL_ID = -1002487065354  # Source channel ID
DESTINATION_CHANNEL_ID = -1002464896968  # Destination channel ID

# Max stored messages aur number of messages to forward
MAX_MESSAGES = 10
FORWARD_MESSAGES = 2

# Deque to store messages
message_queue = deque(maxlen=MAX_MESSAGES)
FORWARD_INTERVAL = 120  # Default: 2 minutes (in seconds)

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Message handle karne ka function
def handle_message(update, context):
    if update.channel_post:
        message_data = {
            'text': update.channel_post.caption or update.channel_post.text,
            'media': update.channel_post.photo[-1].file_id if update.channel_post.photo else None
        }
        message_queue.append(message_data)

# Message forward karne ka function
def forward_messages(context):
    if message_queue:
        for _ in range(min(FORWARD_MESSAGES, len(message_queue))):
            message_data = message_queue.popleft()
            if message_data['media']:
                context.bot.send_photo(chat_id=DESTINATION_CHANNEL_ID, photo=message_data['media'], caption=message_data['text'])
            else:
                context.bot.send_message(chat_id=DESTINATION_CHANNEL_ID, text=message_data['text'])

# Time update karne ka function
def set_interval(update, context):
    global FORWARD_INTERVAL
    try:
        new_interval = int(context.args[0]) * 60  # Minutes to seconds conversion
        FORWARD_INTERVAL = new_interval
        context.job_queue.run_repeating(forward_messages, interval=FORWARD_INTERVAL, first=0)
        update.message.reply_text(f'Interval set to {context.args[0]} minutes.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /setinterval <minutes>')

# Scheduler set karne ka function
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.chat(SOURCE_CHANNEL_ID), handle_message))
    dispatcher.add_handler(CommandHandler('setinterval', set_interval))

    # Job queue me function schedule karna
    job_queue = updater.job_queue
    job_queue.run_repeating(forward_messages, interval=FORWARD_INTERVAL, first=0)

    # Bot ko start karne ka function
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
