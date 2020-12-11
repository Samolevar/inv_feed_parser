from datetime import datetime, timedelta
from typing import List
import pytz

from rss_feed_parser.dto.company import Company
from rss_feed_parser.dto.site_articles.Yahoo import FinanceArticle
from dataclasses import dataclass

from bs4 import BeautifulSoup
from urllib.request import urlopen
utc = pytz.UTC


@dataclass
class Parser(object):
    url: str
    company: Company

    @property
    def __rss_feed(self):
        return urlopen(self.url)

    @property
    def _soup(self):
        return BeautifulSoup(self.__rss_feed, 'xml')

    @property
    def __all_items(self):
        return self._soup.findAll('item')

    def get_yahoo_articles(self) -> List[FinanceArticle]:
        articles = []
        for item in self.__all_items:
            date = datetime.strptime(item.pubDate.string, '%a, %d %b %Y %H:%M:%S %z')
            if date.replace(tzinfo=utc) >= (datetime.now() - timedelta(hours=3)).replace(tzinfo=utc):
                articles.append(FinanceArticle(description=item.description.string,
                                               link=item.link.string,
                                               date=date,
                                               title=item.title.string,
                                               company=self.company))
        return sorted(articles, key=lambda x: x.date)
