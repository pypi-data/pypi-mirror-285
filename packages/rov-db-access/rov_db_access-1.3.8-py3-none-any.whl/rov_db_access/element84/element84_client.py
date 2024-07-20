import logging
from typing import Dict, Any
from pystac_client import Client, ItemSearch

from rov_db_access.element84.query import QueryGenerator

logger = logging.getLogger(__name__)


BANDS = {
    "AOT": "aot",
    "B01": "coastal",
    "B02": "blue",
    "B03": "green",
    "B04": "red",
    "B05": "rededge1",
    "B06": "rededge2",
    "B07": "rededge3",
    "B08": "nir",
    "B11": "swir16",
    "B12": "swir22",
    "SCL": "scl",
    "WVP": "wvp",
    "TCI": "visual",
}


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Element84Client(metaclass=SingletonMeta):
    """
    Gets assets from Element84 api

    """
    api_url = "https://earth-search.aws.element84.com/v1"
    client = Client.open(api_url)

    collection = "sentinel-2-l2a"

    def search(self, query_generator:QueryGenerator, query_info:Dict[str, Any]) -> ItemSearch:
        """
        Search items from Element84 using the query and provided data.

        Args:
            query_generator (QueryGenerator): Query generator to filter values.
            query_info (Dict[str, Any]): Information to query with.

        Returns:
            _type_: _description_
        """
        search = self.client.search(
            collections=[self.collection], **query_generator(query_info)
        )
        items = search.item_collection()
        logger.info("Found %i items", len(items))
        return items
