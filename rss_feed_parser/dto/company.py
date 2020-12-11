from dataclasses import dataclass
from typing import List


@dataclass
class Company(object):
    stock_index: str
    name: str


@dataclass
class Companies(object):
    """
    docstring
    """
    companies: List[Company]
