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
    cur.execute("CREATE TABLE IF NOT EXISTS articles "
                "(link VARCHAR(255) PRIMARY KEY, date timestamp without time zone, article bytea);")
    cur.execute("CREATE TABLE IF NOT EXISTS companies "
                "(stock_index VARCHAR(255) PRIMARY KEY, name VARCHAR(255));")
    conn.commit()


@sched.scheduled_job('interval', hours=3)
def timed_job():
    logger.info("Update news")
    try:
        cur.execute("TRUNCATE TABLE articles")
        bot_channel_updater.update(cur, conn)
        conn.commit()
    except Exception as e:
        logger.exception(e)


create_db_if_needed()
sched.start()
