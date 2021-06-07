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


def update(conn):
    with conn.cursor() as cur:
        try:
            updater.update_yahoo_news(conn)
            cur.execute("select * from articles;")
            for record in cur:
                logger.info(f"Parse {record}")
                item = pickle.loads(record[3])
                logger.info(f"Send message {item}")
                message_text = f"#{item.company.name} #{item.company.stock_index}\n" \
                               f"{util.split_string(item.description, 600)[0]}\n" \
                               f"{item.link}"
                bot.send_message(channel_name, message_text)
        except Exception as e:
            logger.exception(e)


def update_for_one_company(conn, company):
    updater.update_one_company_news(conn, company)
    try:
        with conn.cursor() as cur:
            cur.execute(f"select * from articles where stock_index='{company.stock_index}';")
            for record in cur:
                logger.info(f"Parse {record}")
                item = pickle.loads(record[3])
                logger.info(f"Send message {item}")
                message_text = f"#{item.company.name} #{item.company.stock_index}\n" \
                               f"{util.split_string(item.description, 600)[0]}\n" \
                               f"{item.link}"
                bot.send_message(channel_name, message_text)
    except Exception as e:
        logger.exception(e)
