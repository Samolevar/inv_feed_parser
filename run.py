import logging
import os
import pickle
from datetime import datetime
import pandas as pd

import psycopg2
import helpers.settings as settings
from apscheduler.job import Job

from apscheduler.schedulers.blocking import BlockingScheduler
from bot import bot_channel_updater
from helpers.db.tables import create_tables_if_needed
from model import data_grabber

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
sched = BlockingScheduler()

conn = psycopg2.connect(settings.database_url, sslmode='require')


@sched.scheduled_job('interval', hours=3, id="update")
def timed_job():
    logger.info("Update news")
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE articles")
            bot_channel_updater.update(conn)
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.exception(e)
    finally:
        conn.close()


@sched.scheduled_job('interval', hours=23, id="train")
def timed_job():
    logger.info("Grab data")
    try:
        # if isinstance(sched.get_job("update"), Job):
        #     sched.pause_job("train")
        #     sleep(30)
        #     sched.resume_job("train")
        with conn.cursor() as cur:
            date = datetime.strftime(datetime.now(), "%d.%m.%Y-%H.%M.%S")
            dct_list = []
            cur.execute("select * from train")
            for record in cur:
                logger.info(f"Parse {record}")
                item = pickle.loads(record[4])
                dct_list.append({"link": record[0], "stock_index": record[1],
                                 "company_name": record[2], "date": record[3], "article": item})
            df = pd.DataFrame(dct_list)
            df.to_csv(f'{date}.csv', encoding='utf-8', index=False)
            data_grabber.send_to_disk(f'{date}.csv')
            os.remove(f'{date}.csv')
    except Exception as e:
        conn.rollback()
        logger.exception(e)
    finally:
        conn.close()


create_tables_if_needed(conn, settings.channel_name)
sched.start()
