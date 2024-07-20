from typing import TypedDict, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, create_engine

from rov_db_access.config.db_utils import init_db_engine
from rov_db_access.config.settings import Settings

from rov_db_access.ine.models import BuildingsNico, BuildingsPost

settings = Settings()

CountDifferenceDict = TypedDict("CountDifferenceDict", {"bbox": List[float], "layer_t1": str, "layer_t2": str})


class IneWorker:

    def __init__(self) -> None:

        self.engine = init_db_engine(
            settings.db_rov_proxy_user,
            settings.db_rov_proxy_pass,
            settings.db_rov_proxy_host,
            settings.db_rov_proxy_port,
            settings.db_rov_ine_database
        )


    def count_difference(self, data: CountDifferenceDict):
        bbox = data.get("bbox")
        layer_t1 = data.get("layer_t1")
        layer_t2 = data.get("layer_t2")
        result = {
            layer_t1: 0,
            layer_t2: 0
        }
        if len(bbox) != 4:
            return result

        # transformer = Transformer.from_crs("EPSG:4326", "EPSG:32719")
        # e1, n1 = transformer.transform(bbox[0], bbox[1])
        # e2, n2 = transformer.transform(bbox[2], bbox[3])

        with Session(self.engine) as session:
            pre_query = (
                select(
                    func.count()
                )
                .where(
                    func.ST_Intersects(
                        # func.ST_MakeEnvelope(e1, n1, e2, n2, 32719),
                        func.ST_Transform(func.ST_MakeEnvelope(bbox[0], bbox[1], bbox[2], bbox[3], 4326), 32719),
                        BuildingsNico.geom
                    )
                )
            )
            pre_count = session.scalar(pre_query)
            print("Pre count: ", pre_count)
            result[layer_t1] = pre_count

            post_query = (
                select(
                    func.count()
                )
                .where(
                    func.ST_Intersects(
                        # func.ST_MakeEnvelope(e1, n1, e2, n2, 32719),
                        func.ST_Transform(func.ST_MakeEnvelope(bbox[0], bbox[1],bbox[2], bbox[3],4326), 32719),
                        func.ST_Transform(BuildingsPost.geom, 32719)
                    )
                )
            )
            post_count = session.scalar(post_query)
            print("Post count: ", post_count)
            result[layer_t2] = post_count

            return result
