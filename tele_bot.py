import logging
from core.ai import chat
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes, 
    MessageHandler,
    CommandHandler, 
    filters
)
from core.db import set_redis, get_redis_value
from utils.format import split_into_sentences, wait_response
import os
import dotenv

dotenv.load_dotenv("ops/.env")

token = os.getenv('TELEGRAM_BOT_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="Hey, I am Kalpana, an AI bot created by TinkerHub Foundation for kerala startup mission. I will answer questions about various women startup schemes by KSUM and govt of India :) For more information go to https://bit.ly/KSUMWomenBooklet!")

async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id
    wait = wait_response()
    await context.bot.send_message(chat_id=chat_id, text=wait)
    history = get_redis_value(chat_id)
    if not history:
        history = []
        set_redis(chat_id, history, expire=600)
    response, history = chat(text, messages=history)
    set_redis(chat_id, history)
    texts = split_into_sentences(response)
    for text in texts:
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            pass

if __name__ == '__main__':
    application = ApplicationBuilder().token(token).read_timeout(30).write_timeout(30).build()
    start_handler = CommandHandler('start', start)
    response_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), respond)
    application.add_handler(response_handler)
    application.add_handler(start_handler)
    application.run_polling()