import sys
from rss_feed_parser.base.base_parser import Parser
import pickle
from rss_feed_parser.dto.company import Company

sys.setrecursionlimit(10000)


def get_companies(cur):
    cur.execute("select * from companies;")
    return [Company(*record) for record in cur]


def update_yahoo_news(cur, conn):
    for company in get_companies(cur):
        yahoo_parser = Parser(url=f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={company.stock_index}",
                              company=company)
        for article in yahoo_parser.get_yahoo_articles():
            cur.execute(f"insert into articles (link, date, article) values (%s, %s, %s)", (article.link,
                                                                                            article.date,
                                                                                            pickle.dumps(article)))
            conn.commit()
