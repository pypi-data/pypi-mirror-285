import logging
from datetime import datetime, timedelta
from typing import List
import geojson

import geopandas
import shapely
import numpy as np


from rov_db_access.element84.query import PolygonQuery
from rov_db_access.element84.item import Item
from rov_db_access.element84.element84_client import Element84Client


logger = logging.getLogger(__name__)

DEFAULT_WINDOW = timedelta(days=15) #Time delta, over and under t1 and t2 dates to consider
DEFAULT_ALPHA = 0.8 #Higher alfa, means higher quality but more segments
DEFAULT_MAX_CLOUD = 30


def get_items(date:datetime, polygon:geojson.Polygon, window:timedelta, max_cloud:int) -> geopandas.GeoDataFrame:
    """
    Use Element84 client to get all items matching the polygon query
    within the datetime+-window frame.

    Args:
        date (datetime): Central date to test
        polygon (geojson.Polygon): Polygon to match.
        window (timedelta): Time delta window to find items.

    Returns:
        geopandas.GeoDataFrame: Geodataframe with matching items properties.
    """
    logger.info("Getting items for date: %s", date)
    sc = Element84Client()
    query_gen = PolygonQuery(window_delta=window, max_cloud_cover=max_cloud)
    info = {
        "date": date.strftime("%Y-%m-%d"),
        "polygon": polygon

    }
    items = sc.search(query_gen, info)
    items_list = []
    for item in items:
        item.__class__ = Item
        items_list.append(
            item.to_gpd_dict()
        )
    return geopandas.GeoDataFrame(items_list)

def select_best_tile_orbit(df:geopandas.GeoDataFrame)->geopandas.GeoDataFrame:
    """
    Select best item for each tile-orbit pair.

    Args:
        df (geopandas.GeoDataFrame): GeoDataFrame from element84

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with only the best tile-orbit pair.
    """
    logger.debug("Selecting best tiles.")
    df = df.loc[df.reset_index().groupby(['grid:code','orbit'])['value'].idxmax()]
    logger.info("Found %i best tile-orbit", len(df))
    return df

def spatial_join_dates(df_t1:geopandas.GeoDataFrame, df_t2:geopandas.GeoDataFrame) -> geopandas.GeoDataFrame:
    """
    Join all posible intersecting item pairs from t1 and t2, filtering those with diferent tiles.
    Args:
        df_t1 (geopandas.GeoDataFrame): GeoDataframe containing info from t1
        df_t2 (geopandas.GeoDataFrame): GeoDataframe containing info from t2

    Returns:
        geopandas.GeoDataFrame: Joined GeoDataFrame, containing all possible item pairs.
    """
    logger.debug("Performing spatial join.")
    df = df_t1.sjoin(df_t2, how="inner", predicate='intersects')
    df = df.loc[df["grid:code_left"] == df["grid:code_right"]]
    df["total_value"] = df["value_left"] * df["value_right"]
    logger.info("Found %i item-pairs", len(df))
    return df


def calculate_coverage(df:geopandas.GeoDataFrame, polygon:shapely.Polygon) -> geopandas.GeoSeries:
    """
    Calculate coverage of the image pair, considering both the max item size and the polygon area.

    Args:
        df (geopandas.GeoDataFrame): GeoDataFrame containing the intersection area.
        polygon (shapely.Polygon): Polygon to intersect.

    Returns:
        geopandas.GeoSeries: Series containing the interesections.
    """
    logger.debug("Calculating coverage.")
    return df["intersection_area"]/np.min([float(df.geometry.area.max()), float(polygon.area)])


def calculate_quality(df:geopandas.GeoDataFrame, alpha:float) -> geopandas.GeoSeries:
    """
    Calculate quality based on a weighted average of coverage and total_value.

    Args:
        df (geopandas.GeoDataFrame): Joined GeoDataframe
        alpha (float): Value giving weight to quality vs coverage.
        Higher alphas will increase item quality over coverage.
    Returns:
        geopandas.GeoSeries: GeoSeries containing the quality.
    """
    logger.debug("Calculating quality.")
    return df["total_value"]*alpha + df["area_coverage"]*(1-alpha)



def get_runs(df:geopandas.GeoDataFrame, polygon:shapely.Polygon, alpha:float) -> List:
    """
    Get runs to cover all the polygon using the items pairs.

    Args:
        df (geopandas.GeoDataFrame): GeoDataFrame containing all item pairs.
        polygon (shapely.Polygon): Polygon to cover
        alpha (float): Value giving weight to quality vs coverage.
        Higher alphas will increase item quality over coverage.

    Returns:
        List: List of run inputs. #TODO Format to actual run inputs
    """
    logger.debug("Getting runs.")
    if polygon.area == 0:
        logger.info("Whole polygon coverage.")
        return []
    df["intersection"] = df.geometry.intersection(polygon)
    df["intersection_area"] = df["intersection"].area
    df = df.loc[df["intersection_area"]>0]
    if len(df)==0:
        logger.info("Not enough items to cover all polygon.")
        logger.warning("Area not covered: %s", polygon.area)
        return []
    df["area_coverage"] = calculate_coverage(df, polygon)
    df["quality"] = calculate_quality(df,alpha)
    df = df.sort_values("quality", ascending=False).reset_index(drop=True)
    candidate = df.iloc[0]
    mask = candidate["intersection"]
    polygon = polygon.difference(candidate["geometry"])
    lista_resultado = get_runs(df, polygon, alpha)
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    lista_resultado.append({
        "t1": {
            "title": candidate["s2:product_uri_left"],
            "date": datetime.strptime(candidate["datetime_left"], date_format).isoformat(),
            "preview": candidate["thumbnail_href_left"],
            "bbox": shapely.geometry.box(*candidate["bbox_left"]).wkt
        },
        "t2": {
            "title": candidate["s2:product_uri_right"],
            "date": datetime.strptime(candidate["datetime_right"], date_format).isoformat(),
            "preview": candidate["thumbnail_href_right"],
            "bbox": shapely.geometry.box(*candidate["bbox_right"]).wkt
        },
        "mask": mask
    })
    return lista_resultado

def changeDetectTask(date_t1:datetime, date_t2:datetime, polygon:geojson.Polygon, window:timedelta = DEFAULT_WINDOW, alpha:float=DEFAULT_ALPHA, max_cloud:int=DEFAULT_MAX_CLOUD)-> List:
    """
    Get Runs for a change detect task

    Args:
        date_t1 (datetime): Datetime for the first image.
        date_t2 (datetime): Datetime for the second image.
        polygon (geojson.Polygon): Polygon to cover.
        window (timedelta, optional): Time window to consider. Defaults to DEFAULT_WINDOW.
        alpha (float, optional): Value giving weight to quality vs coverage.
        Higher alphas will increase item quality over coverage. Defaults to DEFAULT_ALPHA.
        max_cloud (int, optional): Max cloud permited for each item. Defaults to DEFAULT_MAX_CLOUD

    Returns:
        List: List of run inputs. #TODO Format to actual run inputs
    """
    df_t1 = get_items(date_t1, polygon, window, max_cloud)
    df_t2 = get_items(date_t2, polygon, window, max_cloud)
    df_t1 = select_best_tile_orbit(df_t1)
    df_t2 = select_best_tile_orbit(df_t2)
    df = spatial_join_dates(df_t1, df_t2)

    polygon_shap = shapely.Polygon(polygon["coordinates"][0]) # Cast geojson polygon to shapley polygon.
    runs = get_runs(df, polygon_shap, alpha)
    return runs

