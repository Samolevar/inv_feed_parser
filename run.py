import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from bot import bot_channel_updater

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=1)
def timed_job():
    logger.info("Update news")
    bot_channel_updater.update()


sched.start()
