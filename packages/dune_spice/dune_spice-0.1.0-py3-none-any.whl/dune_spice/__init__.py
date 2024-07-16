"""Simple python client for exctracting data from the Dune Analytics API"""

from ._extract import query, async_query

__version__ = '0.1.0'

__all__ = ['query', 'async_query']
