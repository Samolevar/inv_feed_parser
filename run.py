import logging
import os

import psycopg2

from apscheduler.schedulers.blocking import BlockingScheduler
from bot import bot_channel_updater

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
sched = BlockingScheduler()


DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()


def create_db_if_needed():
    cur.execute(f"select * from information_schema.tables where table_name=articles")
    if not bool(cur.rowcount):
        cur.execute("CREATE TABLE articles (link VARCHAR(255) PRIMARY KEY, date DATETIME, article VARBINARY(max));")

    cur.execute(f"select * from information_schema.tables where table_name=companies")
    if not bool(cur.rowcount):
        cur.execute("CREATE TABLE companies (id serial PRIMARY KEY, stock_index VARCHAR(255), name VARCHAR(255));")


@sched.scheduled_job('interval', hours=3)
def timed_job():
    logger.info("Update news")
    try:
        cur.execute("TRUNCATE TABLE articles")
        bot_channel_updater.update(cur)
    except Exception as e:
        logger.exception(e)


create_db_if_needed()
sched.start()
