import logging
import os
import yadisk

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

ya_token = os.environ['ya_tkn']


def send_to_disk(file):
    y = yadisk.YaDisk(token=ya_token)
    logger.info(f"Upload file {file}")
    y.upload(file, f'/inv_feed_bot_train/{file}')
