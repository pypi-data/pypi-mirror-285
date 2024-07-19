from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List

class QueryGenerator(ABC):

    @abstractmethod
    def __call__(self, info) -> List:
        pass


class TileQuery(QueryGenerator):

    def __call__(self, info):
        tile = info["tile"]
        date_i = info["date_i"]
        date_f = info["date_f"]
        return {
            "datetime": f"{date_i}/{date_f}",
            "query": [
                f"mgrs:utm_zone={tile[-5:-3]}",
                f"mgrs:latitude_band={tile[-3:-2]}",
                f"mgrs:grid_square={tile[-2:]}",
                "eo:cloud_cover<1",
                "s2:nodata_pixel_percentage<80",
            ],
        }

class PolygonQuery(QueryGenerator):
    def __init__(self, window_delta:timedelta=timedelta(days=30), max_cloud_cover:int = 30):
        self.window_delta=window_delta
        self.max_cloud_cover = max_cloud_cover

    def __call__(self,info):
        date = info["date"]
        polygon = info["polygon"]
        date_format = "%Y-%m-%d"
        date_i = (datetime.strptime(date, date_format)-self.window_delta).strftime(date_format)
        date_f = (datetime.strptime(date, date_format)+self.window_delta).strftime(date_format)
        return {
            "datetime": f"{date_i}/{date_f}",
            "query": [
                f"eo:cloud_cover<{self.max_cloud_cover}",
            ],
            "intersects": polygon
        }



class TitleQuery(QueryGenerator):

    def __call__(self, info):
        title = info["title"]
        return {"query": [f"s2:product_uri={title}"]}

