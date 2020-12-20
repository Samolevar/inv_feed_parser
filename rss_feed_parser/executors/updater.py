import logging
import sys

import psycopg2

from rss_feed_parser.base.base_parser import Parser
import pickle
from rss_feed_parser.dto.company import Company

sys.setrecursionlimit(10000)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_companies(cur):
    logger.info("Get all companies to pull")
    cur.execute("select * from companies;")
    return [Company(*record) for record in cur]


def update_yahoo_news(cur, conn):
    for company in get_companies(cur):
        yahoo_parser = Parser(url=f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={company.stock_index}",
                              company=company)
        news = yahoo_parser.get_yahoo_articles()
        logger.info(f"For {company.name} founded - {len(news)}")
        for article in news:
            try:
                cur.execute(f"insert into articles (link, stock_index, date, article) values (%s,  %s, %s, %s)",
                            (article.link, article.company.stock_index, article.date, pickle.dumps(article)))
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                continue
            conn.commit()


def update_one_company_news(cur, conn, company):
    yahoo_parser = Parser(url=f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={company.stock_index}",
                          company=company)
    news = yahoo_parser.get_yahoo_articles()
    logger.info(f"For {company.name} founded - {len(news)}")
    for article in news:
        try:
            cur.execute(f"insert into articles (link, stock_index, date, article) values (%s, %s, %s, %s)",
                        (article.link, article.company.stock_index, article.date, pickle.dumps(article)))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            continue
        conn.commit()
