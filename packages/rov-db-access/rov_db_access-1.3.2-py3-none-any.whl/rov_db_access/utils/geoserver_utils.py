import os
import urllib
from pprint import pprint
from rov_db_access.config.settings import Settings

import requests
settings = Settings()


class GeoServerClient:
    workspace = None

    def __init__(self):
        self.server_url = settings.geoserver_api_url
        self.session = requests.Session()
        self.session.auth = (settings.geoserver_api_user, settings.geoserver_api_password)
        self.url = settings.geoserver_api_url + "/geoserver/rest"

    def __coverage_store_url(self) -> str:
        return os.path.join(self.url, f"workspaces/{self.workspace}/coveragestores")

    def reload_config(self):
        """
        Reloads the GeoServer catalog and configuration from disk.
        This operation is used in cases where an external tool has modified the on-disk configuration.
        This operation will also force GeoServer to drop any internal caches and reconnect to all data stores.
        """
        try:
            self.session.post(url=f"{self.url}/reload")
            print("Geoserver config reloaded")
        except Exception as e:
            print(f"Error reloading config: {e}")

    def set_workspace(self, workspace: str):
        self.workspace = workspace

    def add_mosaic_granule(self, coverage_store: str, granule_path: str):
        """Adds a new granule to an existing imagemosaic

        Args:
            coverage_store (str): name of the coverage store
            granule_path (str): url to granule
        """
        try:
            response = self.session.post(
                url=os.path.join(
                    self.__coverage_store_url(), f"{coverage_store}/remote.imagemosaic"
                ),
                data=granule_path,
                headers={"Content-Type": "text/plain"},
            )
            response.raise_for_status()
            print(f'Geoserver new granule added for coverage: {coverage_store}')
            return response
        except Exception as e:
            print(f"Error adding granule into coverage: {coverage_store}. ERROR: {e}")
            return None

    def create_empty_mosaic(self, coverage_store: str, zip_path: str):
        """Creates an empty mosaic in geoserver

        Args:
            coverage_store (str): name of the coverage store
            zip_path (str): path to a .zip file containing .properties configuration files
            for mosaic
        """
        with open(zip_path, "rb") as zip:
            data = zip.read()
        response = self.session.put(
            url=os.path.join(
                self.__coverage_store_url(),
                f"{coverage_store}/file.imagemosaic?configure=none",
            ),
            data=data,
            headers={"Content-Type": "application/zip"},
        )
        pprint(response.status_code)

    def delete_mosaic_granule(self, coverage_store: str, coverage_name: str, granule_id: str):
        """deletes granule based on it's id

        Args:
            coverage_store (str): name of coverage store that contains granule
            coverage_name (str): name of the coverage layer
            granule_id (str): granule identifier. Accessible through the index of granules.
        """
        try:
            response = self.session.delete(
                url=os.path.join(
                    self.__coverage_store_url(),
                    f"{coverage_store}/coverages/{coverage_name}/index/granules/{granule_id}",
                )
            )
            pprint(response.status_code)
        except Exception as e:
            print(f"Error deleting granule: {e}")
        pass

    def list_coverages(self, coverage_store: str):
        """Lists all coverages currently hosted in specified coverage store"""
        response = self.session.get(
            url=os.path.join(
                self.__coverage_store_url(), f"{coverage_store}/coverages.xml?list=all"
            )
        )
        pprint(response.text)

    def list_mosaic_granules(
        self, coverage_store: str, coverage: str, filter: str = ""
    ):
        """Lists all granules belonging to a specified coverage"""
        query_url = f"{coverage_store}/coverages/{coverage}/index/granules.json"
        if filter != "":
            filter = urllib.parse.quote(filter)
            query_url += f"?filter={filter}"
        response = self.session.get(
            url=os.path.join(
                self.__coverage_store_url(),
                query_url,
            )
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed listing mosaic granules: {response}")

    def setup_mosaic_config(self, coverage_store: str, xml_path: str):
        """Sends an xml with the mosaic configuration to the geoserver

        Args:
            coverage_store (str): name of the coveragestore to configure
            xml_path (str): path to xml
        """
        # open xml file and send it to geoserver
        with open(xml_path) as xml:
            response = self.session.post(
                url=os.path.join(
                    self.__coverage_store_url(),
                    f"{coverage_store}/coverages",
                ),
                data=xml,
                headers={"Content-Type": "text/xml"},
            )
            pprint(response.status_code)
