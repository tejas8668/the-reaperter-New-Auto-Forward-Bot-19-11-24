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
FORWARD_INTERVAL = 120  # Default: 1 hour (in seconds)

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Message handle karne ka function
def handle_message(update, context):
    if update.channel_post:
        message = update.channel_post.text
        message_queue.append(message)

# Message forward karne ka function
def forward_messages(context):
    if message_queue:
        for _ in range(min(FORWARD_MESSAGES, len(message_queue))):
            message = message_queue.popleft()
            context.bot.send_message(chat_id=DESTINATION_CHANNEL_ID, text=message)

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

    dispatcher.add_handler(MessageHandler(Filters.text & Filters.chat(SOURCE_CHANNEL_ID), handle_message))
    dispatcher.add_handler(CommandHandler('setinterval', set_interval))

    # Job queue me function schedule karna
    job_queue = updater.job_queue
    job_queue.run_repeating(forward_messages, interval=FORWARD_INTERVAL, first=0)

    # Bot ko start karne ka function
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
