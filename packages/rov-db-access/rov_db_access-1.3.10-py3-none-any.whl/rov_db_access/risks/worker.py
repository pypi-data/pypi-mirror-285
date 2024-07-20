from typing import TypedDict, List

from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session, Bundle
from sqlalchemy import select, func
from rov_db_access.config.db_utils import init_db_engine
from rov_db_access.config.settings import Settings
from shapely import wkb
from pyproj import Transformer

from rov_db_access.utils.utils import wkbelement_to_wkt
from rov_db_access.geodata.models import FloodHazard, TsunamiHazard, RMHazard, VolcanicHazard, VolcanicHazardPyroclast, WildfireHazard
from rov_db_access.risks.models import UserResultsHistory

settings = Settings()

CalculateRiskDict = TypedDict("CalculateRiskDict", {"lat": float, "lng": float, "radius": int, "layers": List[str]})
Risks = [FloodHazard, TsunamiHazard, RMHazard, VolcanicHazard, VolcanicHazardPyroclast, WildfireHazard]


class RisksWorker:

    def __init__(self) -> None:

        self.engine = init_db_engine(
            settings.db_rov_proxy_user,
            settings.db_rov_proxy_password,
            settings.db_rov_proxy_host,
            settings.db_rov_proxy_port,
            settings.db_rov_geodata_database
        )

    def calculate_risk(self, data: CalculateRiskDict):
        lat = data.get("lat")
        lng = data.get("lng")
        radius = data.get("radius")
        layers = data.get("layers")
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:32719")
        e, n = transformer.transform(lat, lng)

        point_wkt_32719 = WKTElement('POINT({0} {1})'.format(e, n), srid=32719)
        point_32719_geom = to_shape(point_wkt_32719)
        circle_32719_geom = point_32719_geom.buffer(radius)
        circle_32719_wkb = wkb.dumps(circle_32719_geom, hex=True, srid=32719)
        circle_32719_area = circle_32719_geom.area

        with Session(self.engine) as session:
            result = {}
            for layer in layers:
                result[layer] = []
                risk_classes = list(filter(lambda x: x.__tablename__ == layer, Risks))
                if len(risk_classes) < 1:
                    break
                risk_class = risk_classes[0]

                risk_query = (
                    select(
                        Bundle(
                            "risk",
                            risk_class.id,
                            risk_class.risk_weight,
                            func.ST_Transform(risk_class.geom, 4326)
                        ),
                        Bundle(
                            "data",
                            func.ST_Transform(
                                func.ST_Intersection(circle_32719_wkb, func.ST_Transform(risk_class.geom, 32719)),
                                4326
                            ),
                            func.ST_Area(
                                func.ST_Intersection(circle_32719_wkb, func.ST_Transform(risk_class.geom, 32719))
                            ),
                            func.ST_Distance(
                                point_wkt_32719,
                                func.ST_Transform(risk_class.geom, 32719)
                            )
                        )
                    )
                    .where(func.ST_Intersects(circle_32719_wkb, func.ST_Transform(risk_class.geom, 32719)))
                )

                risk_result = session.execute(risk_query)
                for row in risk_result:
                    print(f"layer: {layer}, risk id {row.risk.id}")
                    percentage = round(100 * row.data.ST_Area / circle_32719_area, 2)
                    weight = row.risk.risk_weight
                    score = weight * (row.data.ST_Area / circle_32719_area) + (1-weight)/(row.data.ST_Distance + 1)
                    print(f"layer: {layer}, distance: {row.data.ST_Distance}, area: {row.data.ST_Area}, score: {score}")
                    result[layer].append({
                        "id": row.risk.id,
                        "risk_weight": row.risk.risk_weight,
                        "geom": wkbelement_to_wkt(row.risk.ST_Transform),
                        "intersection": wkbelement_to_wkt(row.data.ST_Transform),
                        "area_intersected": row.data.ST_Area,
                        "distance": row.data.ST_Distance,
                        "percentage_covered": percentage,
                        "score": score
                    })
            return result


class GisRisksWorker:

    def __init__(self) -> None:
        self.engine = init_db_engine(
            settings.db_rov_proxy_user,
            settings.db_rov_proxy_password,
            settings.db_rov_proxy_host,
            settings.db_rov_proxy_port,
            settings.db_rov_gis_database
        )

    def register_user_result(self, user_id: int, lat: float, lng: float, data: str, name: str, address: str):
        location = WKTElement(f'POINT({lng} {lat})', srid=4326)
        with Session(self.engine) as session:
            user_results_history = UserResultsHistory(user_id=user_id, location=location, data=data, name=name, address=address)
            session.add(user_results_history)
            session.commit()
            return {"id": user_results_history.id, "location": f'POINT({lng} {lat})', "name": user_results_history.name, "address": user_results_history.address}

    def get_user_results(self, user_id: int):
        with Session(self.engine) as session:
            user_results_history = session.query(UserResultsHistory).filter(UserResultsHistory.user_id == user_id).all()
            results = []
            for result in user_results_history:
                results.append({
                    "id": result.id,
                    "name": result.name,
                    "address": result.address,
                    "location": wkbelement_to_wkt(result.location),
                    "data": result.data,
                    "created_at": result.created_at,
                    "saved": result.saved
                })
            return results

    def save_analysis(self, user_id: int, analysis_id: int, saved: bool):
        with Session(self.engine) as session:
            user_results_history = session.query(UserResultsHistory).filter(UserResultsHistory.user_id == user_id).filter(UserResultsHistory.id == analysis_id).first()
            user_results_history.saved = saved
            session.commit()
            return {
                "id": user_results_history.id,
                "name": user_results_history.name,
                "saved": user_results_history.saved
            }
