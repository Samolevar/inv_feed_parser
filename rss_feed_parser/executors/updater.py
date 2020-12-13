import sys
from rss_feed_parser.base.base_parser import Parser
import json
import pickle
from rss_feed_parser.dto.company import Company, Companies

sys.setrecursionlimit(10000)


def get_companies():
    with open('foreign_companies.json', 'r') as f:
        return [Company(**record) for record in Companies(**json.load(f)).companies]


def update_yahoo_news():
    with open('yahoo_result.pickle', 'wb') as res:
        current_articles = []
        for company in get_companies():
            yahoo_parser = Parser(url=f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={company.stock_index}",
                                  company=company)
            current_articles.extend(yahoo_parser.get_yahoo_articles())
        pickle.dump(current_articles, res)
