import datetime
from dataclasses import dataclass

from rss_feed_parser.dto.company import Company


@dataclass(order=True)
class FinanceArticle(object):
    description: str
    link: str
    date: datetime
    title: str
    company: Company
