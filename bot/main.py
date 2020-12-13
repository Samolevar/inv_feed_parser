import dataclasses
import json
import os
import time
import logging

import telebot
from telebot import util, types

from bot import bot_channel_updater
from rss_feed_parser.dto.company import Companies, Company

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

TOKEN = str(os.environ['Token'])
channel_name = str(os.environ['Channel'])
bot = telebot.TeleBot(TOKEN)

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
add = types.KeyboardButton('/add')
lst = types.KeyboardButton('/list')
rmv = types.KeyboardButton('/remove')
markup.row(add, lst, rmv)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hi, I am an invest feed parser bot. I can send you news according to your"
                                      "list of stocks. You can work with me using buttons below", reply_markup=markup)


@bot.message_handler(commands=['list'])
def get_list(message):
    logger.info("Returning list of companies to user")
    bot.send_message(message.chat.id, f"List of companies, which news you are track")
    with open('../foreign_companies.json', 'r') as f:
        companies = [Company(**cmp) for cmp in Companies(**json.load(f)).companies]
        comps = '\n'.join([f"{cmp.stock_index} - {cmp.name}" for cmp in companies])
        splitted_text = util.split_string(comps, 3000)
        for text in splitted_text:
            bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(commands=['add'])
def add_to_list(message):
    bot.send_message(message.chat.id, "If you want to add new company to list, send me pair "
                                      "StockIndex:FullNameOfCompany", reply_markup=markup)


@bot.message_handler(commands=['remove'])
def delete_from_list(message):
    bot.send_message(message.chat.id, "If you want to delete company from list, send me command"
                                      "delete/StockIndex", reply_markup=markup)


@bot.message_handler(func=lambda message: 'delete/' in message.text)
def actual_remove_from_list(message):
    _, index = message.text.split('/')
    logger.info(f"Removing company with stock index {index} from list of companies")
    companies = []
    with open('../foreign_companies.json', 'r') as f:
        companies.extend([Company(**company) for company in Companies(**json.load(f)).companies if
                          Company(**company).stock_index != index])
    with open('../foreign_companies.json', 'w') as f:
        output = dataclasses.asdict(Companies(companies=companies))
        json.dump(output, f)


@bot.message_handler(func=lambda message: ':' in message.text)
def actual_add_to_list(message):
    index, name = message.text.split(':')
    logger.info(f"Adding company {name} with stock index {index} to list of companies")
    comp = Company(stock_index=index, name=name)
    companies = []
    with open('../foreign_companies.json', 'r') as f:
        companies.extend(Companies(**json.load(f)).companies)
        if comp not in companies:
            companies.append(comp)
    with open('../foreign_companies.json', 'w') as f:
        output = dataclasses.asdict(Companies(companies=companies))
        json.dump(output, f)
    bot_channel_updater.update()


if __name__ == '__main__':
    while True:
        try:
            logger.info('Polling bot')
            bot.polling(none_stop=True)
        except Exception as e:
            logger.exception(e)
            time.sleep(15)
