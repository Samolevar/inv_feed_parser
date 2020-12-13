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


def update():
    updater.update_yahoo_news()
    with open('../yahoo_result.pickle', 'rb') as result:
        for item in pickle.load(result):
            message_text = f"#{item.company.name} #{item.company.stock_index}\n" \
                           f"{util.split_string(item.description, 600)[0]}\n" \
                           f"{item.link}"
            bot.send_message(channel_name, message_text)


if __name__ == '__main__':
    update()
