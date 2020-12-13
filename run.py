from apscheduler.schedulers.blocking import BlockingScheduler
from bot import bot_channel_updater

sched = BlockingScheduler()


@sched.scheduled_job('interval', hours=3)
def timed_job():
    bot_channel_updater.update()


sched.start()
