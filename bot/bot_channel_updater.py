import logging
import os
import pickle

import telebot
from telebot import util

from rss_feed_parser.executors import updater

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

TOKEN = str(os.environ['Token'])
channel_name = str(os.environ['Channel'])
bot = telebot.TeleBot(TOKEN)


def update(cur):
    try:
        updater.update_yahoo_news(cur)
        cur.execute("select * from articles;")
        for record in cur:
            for item in pickle.load(record[2]):
                message_text = f"#{item.company.name} #{item.company.stock_index}\n" \
                               f"{util.split_string(item.description, 600)[0]}\n" \
                               f"{item.link}"
                bot.send_message(channel_name, message_text)
    except Exception as e:
        logger.exception(e)
