import logging
import os
from datetime import datetime
from time import sleep

import psycopg2
from apscheduler.job import Job

from apscheduler.schedulers.blocking import BlockingScheduler
from bot import bot_channel_updater
from model import data_grabber

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
sched = BlockingScheduler()

channel_name = str(os.environ['Channel'])
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()


def create_db_if_needed():
    cur.execute("CREATE TABLE IF NOT EXISTS articles "
                "(link VARCHAR(255) PRIMARY KEY, stock_index VARCHAR(255), "
                "date timestamp without time zone, article bytea);")
    cur.execute("CREATE TABLE IF NOT EXISTS companies "
                "(stock_index VARCHAR(255) PRIMARY KEY, name VARCHAR(255));")
    cur.execute("CREATE TABLE IF NOT EXISTS channels "
                "(channel VARCHAR(255) PRIMARY KEY, name VARCHAR(255));")
    cur.execute("Create TABLE IF NOT EXISTS train "
                "(link VARCHAR(255) PRIMARY KEY, stock_index VARCHAR(255),"
                "company_name VARCHAR(255), date timestamp without time zone, article bytea);")
    try:
        cur.execute("insert into channels (channel, name) values (%s, %s)", (channel_name, "Polina"))
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
    conn.commit()


@sched.scheduled_job('interval', hours=3, id="update")
def timed_job():
    logger.info("Update news")
    try:
        cur.execute("TRUNCATE TABLE articles")
        bot_channel_updater.update(cur, conn)
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.exception(e)


@sched.scheduled_job('interval', hours=23, id="train")
def timed_job():
    logger.info("Grab data")
    try:
        # if isinstance(sched.get_job("update"), Job):
        #     sched.pause_job("train")
        #     sleep(30)
        #     sched.resume_job("train")
        train_data = "COPY train TO STDOUT WITH CSV HEADER"
        date = datetime.strftime(datetime.now(), "%d.%m.%Y-%H.%M.%S")
        with open(f'{date}.csv', 'w') as f:
            cur.copy_expert(train_data, f)
        cur.execute("TRUNCATE TABLE train")
        conn.close()
        data_grabber.send_to_disk(f'{date}.csv')
        os.remove(f'{date}.csv')
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.exception(e)


create_db_if_needed()
sched.start()
