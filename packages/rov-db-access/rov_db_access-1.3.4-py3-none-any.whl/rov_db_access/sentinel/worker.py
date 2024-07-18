import re
from datetime import datetime
from typing import TypedDict

from rov_sent_api.sentinel_api import SentinelApi
from sqlalchemy.orm import Session
from sqlalchemy import select

from rov_db_access.config.db_utils import init_db_engine
from rov_db_access.sentinel.models import Tiles
from rov_db_access.config.settings import Settings
from rov_db_access.utils.utils import wkbelement_to_wkt

settings = Settings()

SentinelSearchDict = TypedDict("SentinelSearchDict", {
    "tile": str,
    "init_date": str,
    "end_date": str,
    "cloud": int
})
SentinelSearchByGeomDict = TypedDict("SentinelSearchByGeomDict", {
    "polygon": str,
    "init_date": str,
    "end_date": str,
    "cloud": int
})
SentinelImageDict = TypedDict("SentinelImageDict", {
    "uuid": str,
    "tile": str,
    "date": str,
    "cloud": float,
    "footprint": str
})


def is_valid_uuid(input_string):
    pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    return bool(re.match(pattern, input_string))

# def get_presigned_url_s3_by_key(s3_key):
#         if s3_key is None:
#             return None
#
#         s3 = boto3.client("s3", aws_access_key_id=settings.aws_key,
#                           aws_secret_access_key=settings.aws_secret,
#                           config=Config(signature_version='s3v4', region_name='us-east-2'))
#         try:
#             url = s3.generate_presigned_url(
#                 'get_object',
#                 Params={'Bucket': settings.sentinel_s3_bucket,
#                         'Key': f"{s3_key}"},
#                 ExpiresIn=60
#             )
#             return url
#         except ClientError as e:
#             return None


class SentinelSearchWorker:

    def __init__(self) -> None:

        self.products = None

        self.engine = init_db_engine(
            settings.db_rov_sentinel_user,
            settings.db_rov_sentinel_password,
            settings.db_rov_sentinel_host,
            settings.db_rov_sentinel_port,
            settings.db_rov_sentinel_database
        )

    def get_products_by_tile(self, query: SentinelSearchDict):
        query["init_date"] = datetime.strptime(query["init_date"], "%d/%m/%Y")
        query["end_date"] = datetime.strptime(query["end_date"], "%d/%m/%Y")
        tile = query.pop("tile")
        init_date = query.pop("init_date")
        end_date = query.pop("end_date")
        cloud = query.pop("cloud")

        sen_api = SentinelApi(settings.sentinel_user, settings.sentinel_password)
        self.products = sen_api.find(
            sen_api.ProductType.S2MSI2A,
            tile=tile,
            init_date=init_date,
            end_date=end_date,
            cloud_cover=cloud
        )
        print("Sentinel query results count : ", len(self.products))

        l2_products = {}

        for product in self.products:
            l2_products[product["id"]] = product

        results = []
        for uuid, product in l2_products.items():
            try:
                online = sen_api.sentinel.is_online(uuid)
            except:
                online = False

            results.append({
                "title": product["title"],
                "date": product["date"].strftime("%d/%m/%Y"),
                "tile": product["tileId"],
                "cloud": product["cloudCover"],
                "uuid": product["id"],
                "footprint": product["footprint"],
                "online": online,
                "quicklook": product["Quicklook"]
            })
        return results

    def get_geom_tiles(self):
        result_tiles = []
        with Session(self.engine) as session:
            query = select(Tiles).where(Tiles.required).order_by(Tiles.name)
            for tile in session.scalars(query):
                geom_wkt = wkbelement_to_wkt(tile.geom)
                result_tiles.append({
                    "id": tile.id,
                    "name": tile.name,
                    "geom": geom_wkt
                })
            return result_tiles

    def get_products_by_geom(self, query: SentinelSearchByGeomDict):
        polygon = query.pop("polygon")
        query["init_date"] = datetime.strptime(query["init_date"], "%d/%m/%Y")
        query["end_date"] = datetime.strptime(query["end_date"], "%d/%m/%Y")
        init_date = query.pop("init_date")
        end_date = query.pop("end_date")
        cloud = query.pop("cloud")
        sen_api = SentinelApi(settings.sentinel_user, settings.sentinel_password)
        print("Sentinel query by geom input polygont: ", polygon)
        self.products = sen_api.findGeom(
            productType=SentinelApi.ProductType.S2MSI2A,
            polygon=polygon,
            init_date=init_date,
            end_date=end_date,
            cloud_cover=cloud
        )
        print("Sentinel query by geom results count: ", len(self.products))

        l2_products = {}

        for product in self.products:
            l2_products[product["id"]] = product

        results = []
        for uuid, product in l2_products.items():
            results.append({
                "title": product["title"],
                "date": product["date"].strftime("%d/%m/%Y"),
                "tile": product["tileId"],
                "cloud": product["cloudCover"],
                "uuid": product["id"],
                "footprint": product["footprint"],
                "quicklook": product["Quicklook"]
            })
        return results

    def get_tile(self, name: str):
        with Session(self.engine) as session:
            query = select(Tiles).where(Tiles.name == name)
            tile = session.scalar(query)
            geom_wkt = wkbelement_to_wkt(tile.geom)
            return {
                "id": tile.id,
                "name": tile.name,
                "geom": geom_wkt,
                "required": tile.required
            }
