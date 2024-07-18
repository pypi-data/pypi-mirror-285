import pystac.item
from typing import Any
import geojson
import re

class Item(pystac.item.Item):

    def get_value(self):
        value = 1 #Parte en 1
        value *= (100-self.properties["eo:cloud_cover"])/100 #Se disminuye de acuerdo al % de nubes
        value *= (100-self.properties["s2:degraded_msi_data_percentage"])/100
        return value

    def to_gpd_dict(self) -> dict[str, Any]:
        result = {}
        result.update(self.properties)
        result["value"] = self.get_value()
        result["bbox"] = self.bbox
        result["thumbnail_href"] = self.assets["thumbnail"].href
        result["geometry"] = geojson.Polygon(self.geometry["coordinates"])
        try:
            result["orbit"] = re.search(r"R\d{3}",self.properties["s2:product_uri"]).group()
        except Exception:
            result["orbit"] = "None"
            result["value"] = 0
        return result