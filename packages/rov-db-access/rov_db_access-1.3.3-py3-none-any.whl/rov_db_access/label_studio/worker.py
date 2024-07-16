from typing import TypedDict, List
from PIL import Image as im
import io

from rov_sent_api.sentinel_api import SentinelApi
from shapely import wkt
from sqlalchemy.orm import Session
from sqlalchemy import select, insert

from rov_db_access.config.db_utils import init_db_engine
from rov_db_access.label_studio.models import Task, Label, Project
from rov_db_access.config.settings import Settings
from rov_db_access.utils.utils import wkbelement_to_wkt

import rasterio
from rasterio.session import AWSSession

settings = Settings()

SaveLabelDict = TypedDict("SaveLabelDict", {
    "task_id": str,
    "task_is_valid": bool,
    "user_id": int,
    "updated_labels": List[dict],
    "new_labels": List[dict]
})


class RovLabelStudioWorker:

    def __init__(self) -> None:

        self.engine = init_db_engine(
            settings.db_rov_gis_user,
            settings.db_rov_gis_password,
            settings.db_rov_gis_host,
            settings.db_rov_gis_port,
            settings.db_rov_gis_database
        )

    def load_projects(self):
        with Session(self.engine) as session:
            project_query = (
                select(Project)
            )
            projects = session.execute(project_query).all()
            projects_list = []
            for project in projects:
                project = project[0]
                types = []
                for type in project.types:
                    types.append({
                        "id": type.id,
                        "name": type.name,
                        "colour": type.colour
                    })
                batches = len(project.batches)
                projects_list.append({
                    "id": project.id,
                    "name": project.name,
                    "types": types,
                    "batches": batches
                })
            return projects_list

    def load_project(self, id: str):
        with Session(self.engine) as session:
            project_query = (
                select(Project)
                .where(Project.id == id)
                .limit(1)
            )
            project = session.scalar(project_query)
            if project is None:
                return {}
            print(f'Load project with id: {id} found! Batches:  #{len(project.batches)}')
            types = []
            for type in project.types:
                types.append({
                    "id": type.id,
                    "name": type.name,
                    "colour": type.colour
                })
            batches = []
            for batch in project.batches:
                tasks = []
                for task in batch.tasks:
                    tasks.append({
                        "id": task.id,
                        "name": task.name,
                        "status": task.status
                    })
                batches.append({
                    "id": batch.id,
                    "name": batch.name,
                    "tasks": tasks
                })
            return {
                "id": project.id,
                "name": project.name,
                "types": types,
                "batches": batches
            }

    def get_task(self, id: str):
        with Session(self.engine) as session:
            task_query = (
                select(Task)
                .where(Task.id == id)
                .limit(1)
            )
            task = session.scalar(task_query)
            if task is None:
                return {}
            print(f'Get task with id: {id} found is {task}')
            bbox_wkt = wkbelement_to_wkt(task.bbox)
            labels = []
            images = []
            for label in task.labels:
                labels.append({
                    "id": label.id,
                    "name": label.name,
                    "time": label.time,
                    "status": label.status,
                    "created_at": label.created_at,
                    "modified_at": label.modified_at,
                    "geom": wkbelement_to_wkt(label.geom),
                    "type_id": label.type_id
                })
            for image in task.images_rl:
                images.append({
                    "id": image.id,
                    "in_storage": image.in_storage,
                    "url": image.url
                })
            return {
                "id": task.id,
                "name": task.name,
                "time": task.time,
                "bbox": bbox_wkt,
                "created_at": task.created_at,
                "modified_at": task.modified_at,
                "status": task.status,
                "comments": task.comments,
                "is_valid": task.is_valid,
                "labels": labels,
                "images": images
            }

    def get_cog_image_window(self, path: str, geom: str):
        geometry = wkt.loads(geom)
        bbox = geometry.bounds
        bbox_adapted = (bbox[0], bbox[3], bbox[2], bbox[1])
        print(f'get_cog_image_window to find image path: {path} and bbox={bbox_adapted}')
        rasterio_session = AWSSession(aws_unsigned=True, region_name='us-west-2', endpoint_url='s3.us-west-2.amazonaws.com')
        with rasterio.Env(session=rasterio_session) as env:
            sen_api = SentinelApi(settings.sentinel_user, settings.sentinel_password)
            image_array = sen_api.extract_window_from_cog(
                path,
                'TCI',
                window_coords=bbox_adapted
            )
            print("Rasterio image_array found! ")
            data = im.fromarray(image_array, mode='RGB')
            img_bytes = io.BytesIO()
            data.save(img_bytes, format='png')
            return img_bytes

    def save_label(self, data: SaveLabelDict):
        task_id = data["task_id"]
        task_is_valid = data["task_is_valid"]
        user_id = data["user_id"]
        new_labels = data["new_labels"]

        with Session(self.engine) as session:
            task_query = (
                select(Task)
                .where(Task.id == task_id)
                .limit(1)
            )
            task = session.scalar(task_query)
            if task is None:
                return False
            print(f'Save label to task with id: {id} found is {task}')

            new_labels_insertion = []
            for new_label in new_labels:
                new_labels_insertion.append({
                    "name": new_label.get("name"),
                    "time": new_label.get("time"),
                    "status": "edited",
                    "geom": new_label.get("geom"),
                    "task_id": task_id,
                    "user_id": user_id,
                    "type_id": new_label.get("type_id")
                })

            task.is_valid = task_is_valid
            task.status = "edited"

            if len(new_labels_insertion) > 0:
                session.execute(
                    insert(Label),
                    new_labels_insertion
                )
            try:
                session.commit()
                return True
            except:
                return False
