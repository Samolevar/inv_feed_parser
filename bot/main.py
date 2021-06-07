import os
import pickle
import time
import logging
from datetime import datetime

import pandas as pd
import psycopg2
import telebot
from telebot import util, types

from bot import bot_channel_updater
from helpers.db.tables import create_tables_if_needed
from model import data_grabber
from rss_feed_parser.dto.company import Company
import helpers.settings as settings

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(settings.token)

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
add = types.KeyboardButton('/add')
lst = types.KeyboardButton('/list')
rmv = types.KeyboardButton('/remove')
trn = types.KeyboardButton('/train')
markup.row(add, lst, rmv, trn)

conn = psycopg2.connect(settings.database_url, sslmode='require')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hi, I am an invest feed parser bot. I can send you news according to your"
                                      "list of stocks. You can work with me using buttons below", reply_markup=markup)


@bot.message_handler(commands=['list'])
def get_list(message):
    logger.info("Returning list of companies to user")
    bot.send_message(message.chat.id, f"List of companies, which news you are track")
    try:
        with conn.cursor() as cur:
            cur.execute("select * from companies;")
            companies = [Company(*cmp) for cmp in cur]
    except Exception as exp:
        logger.exception(exp)
    finally:
        conn.close()
    comps = '\n'.join([f"{cmp.stock_index} - {cmp.name}" for cmp in companies])
    divided_text = util.split_string(comps, 3000)
    for text in divided_text:
        bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(commands=['add'])
def add_to_list(message):
    bot.send_message(message.chat.id, "If you want to add new company to list, send me pair "
                                      "StockIndex:FullNameOfCompany", reply_markup=markup)


@bot.message_handler(commands=['train'])
def send_train_data(message):
    bot.send_message(message.chat.id, "Sending current state of train data to disk", reply_markup=markup)
    logger.info("Grab data")
    dct_list = []
    try:
        with conn.cursor() as cur:
            data_grabber.prepare_train_table(conn)
            cur.execute("select * from train")
            for record in cur:
                logger.info(f"Parse {record}")
                item = pickle.loads(record[4])
                dct_list.append({"link": record[0], "stock_index": record[1],
                                 "company_name": record[2], "date": record[3], "article": item})
    except Exception as exp:
        conn.rollback()
        logger.exception(exp)
    finally:
        conn.close()
    df = pd.DataFrame(dct_list)
    date = datetime.strftime(datetime.now(), "%d.%m.%Y-%H.%M.%S")
    df.to_csv(f'{date}.csv', encoding='utf-8', index=False)
    data_grabber.send_to_disk(f'{date}.csv')
    os.remove(f'{date}.csv')


@bot.message_handler(commands=['remove'])
def delete_from_list(message):
    bot.send_message(message.chat.id, "If you want to delete company from list, send me command "
                                      "delete/StockIndex", reply_markup=markup)


@bot.message_handler(func=lambda message: 'delete/' in message.text)
def actual_remove_from_list(message):
    _, index = message.text.split('/')
    logger.info(f"Removing company with stock index {index} from list of companies")
    try:
        with conn.cursor() as cur:
            cur.execute(f"delete from companies where stock_index='{index}';")
    except Exception as exp:
        conn.rollback()
        logger.exception(exp)
    finally:
        conn.close()


@bot.message_handler(func=lambda message: ':' in message.text)
def actual_add_to_list(message):
    index, name = message.text.split(':')
    logger.info(f"Adding company {name} with stock index {index} to list of companies")
    try:
        with conn.cursor() as cur:
            cur.execute("insert into companies (stock_index, name) values (%s, %s)", (index, name))
            bot_channel_updater.update_for_one_company(conn, Company(stock_index=index, name=name))
    except psycopg2.errors.UniqueViolation:
        bot.send_message(message.chat.id, "Company already exists", reply_markup=markup)
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    create_tables_if_needed(conn, settings.channel_name)
    while True:
        try:
            logger.info('Polling bot')
            bot.polling(none_stop=True)
        except Exception as e:
            logger.exception(e)
            time.sleep(15)
