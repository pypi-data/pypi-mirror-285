import os
import json
from datetime import datetime, timedelta
from typing import Literal, TypedDict, List, Optional, Dict, Any

import boto3
import hashlib

import json

import geojson
from botocore.client import Config
from botocore.exceptions import ClientError
from shapely import wkt, to_geojson
from shapely.geometry import shape, mapping

from rov_db_access.authentication.models import User, Organization
from rov_db_access.element84.tasks import changeDetectTask
from rov_db_access.gis.geo_operations import OpLayer, OpVectorResult, OpWkt, st_geojson
from rov_db_access.utils.geoserver_utils import GeoServerClient
from rov_db_access.utils.s3_utils import S3Client
from rov_db_access.utils.utils import add_srid_to_raw_wkt, get_wkt_area, wkbelement_to_wkt
from rov_db_access.config.db_utils import init_db_engine
from rov_db_access.config.settings import Settings
from rov_db_access.sentinel.worker import is_valid_uuid
from rov_db_access.gis.models import Process, Image, InferenceModel, RunData, ResultsRaster, Run, ResultsVector, Mosaic
from sqlalchemy import MetaData, Table, select, and_, func, insert
from sqlalchemy.orm import Session, Mapped, mapped_column
from geoalchemy2 import Geometry

settings = Settings()

CreateProcessDict = TypedDict("CreateProcessDict", {
    "name": str,
    "inference_model_id": int,
    "area": float,
    "cost_estimated": float,
    "images": List[dict],
    "geom": str,
    "mask": Optional[str],
    "data": Optional[dict]
})

CreateProcessChangeDetectorDict = TypedDict("CreateProcessChangeDetectorDict", {
    "name": str,
    "area": float,
    "cost_estimated": float,
    "date_t1": str,
    "date_t2": str,
    "geom": str,
    "mask": Optional[str],
    "data": Optional[dict]
})

CreateTaskingDict = TypedDict("CreateTaskingDict", {
    "name": str,
    "inference_model_id": int,
    "area": float,
    "cost_estimated": float,
    "tasking_config": dict,
    "geom": str,
    "mask": Optional[str]
})

UploadImageDict = TypedDict("UploadImageDict", {
    "name": str,
    "url": str,
    "bbox": str
})


def get_upload_s3_url():
    region = settings.gis_inference_region
    bucket_name = settings.gis_inference_bucket
    access_key_id = settings.aws_key
    secret_access_key = settings.aws_secret

    s3 = boto3.client(
        "s3",
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        config=Config(signature_version='s3v4', region_name=region)
    )

    # Generate a unique image name
    raw_bytes = os.urandom(16)
    image_name = hashlib.sha256(raw_bytes).hexdigest()
    object_key = image_name + ".tif"

    params = {
        "Bucket": bucket_name,
        "Key": object_key,
    }

    try:
        upload_url = s3.generate_presigned_url(
            "put_object",
            Params=params,
            ExpiresIn=60
        )
        return {"upload_url": upload_url, "object_key": object_key}

    except ClientError as e:
        return None


def get_date(obj):
    return tuple(map(int, obj["date"].split("/")[::-1]))


def create_merge_run_from_process(session: Session, process: Process, user: User) -> bool:
    user_id = user.id
    organization_id = user.organization_id
    print("create_merge_run_from_process: process to start run: ", process)
    runs = process.runs
    run_data_input_ids = []
    for run in runs:
        if run.inference_model_id != 9:
            run_data_input_ids.append(run.output_id)
    if len(runs) < 2 or len(runs) != len(run_data_input_ids):
        print("Process create merge run do not have conditions to proceed. Run not created but succedeed call.")
        return True
    merge_new_input = RunData(
        type='merge',
        status="waiting",
        data={
            "run_data_ids": run_data_input_ids,
        },
        user_id=user_id,
        organization_id=organization_id
    )
    session.add(merge_new_input)
    merge_new_output = RunData(
        type='vector',
        status='waiting',
        user_id=user_id,
        organization_id=organization_id
    )
    session.add(merge_new_output)
    model_merge = session.get(InferenceModel, 9)
    if model_merge is None:
        print("ERROR Process create merge run . An exception occurred during run merge creation: Merge inference_model does not exist!!")
        return False
    merge_new_run = Run(
        input=merge_new_input,
        inference_model_id=model_merge.id,
        inference_model_version=model_merge.current_version,
        process=process,
        output=merge_new_output,
    )
    session.add(merge_new_run)
    try:
        session.commit()
        return True
    except Exception as error:
        print("ERROR Process create merge run . An exception occurred during run merge creation:", error)
        return False


def add_mosaic_granules(granule_path_list: List[str], coverage_store: str, workspace: str):
    geoserver_client = GeoServerClient()
    geoserver_client.set_workspace(workspace)
    try:
        granules_added_counter = 0
        for granule_path in granule_path_list:
            result = geoserver_client.add_mosaic_granule(coverage_store, granule_path)
            if result:
                granules_added_counter = granules_added_counter + 1
        if len(granule_path_list) != granules_added_counter:
            print(f'WARNING add_mosaic_granules. Not all granules added: {granules_added_counter}/{len(granule_path_list)}')
            return False
        print(f'add_mosaic_granules. Granules added: {granules_added_counter}')
        return True
    except Exception as error:
        print("ERROR add_mosaic_granule. An exception occurred during granule insertion:", error)
        return False


def submit_job(job_name: str, run_ids: List[int] = []):
    batch = boto3.client("batch")
    job_queue = (
        "arn:aws:batch:us-east-2:510999855650:job-queue/change-detect-queue-fargate"
    )
    job_definition = "arn:aws:batch:us-east-2:510999855650:job-definition/change-detect-job-definition-fargate"
    container_overrides = {}
    if len(run_ids) != 0:
        command = ["python", "pipe.py"]
        for run_id in run_ids:
            command += ["--run_ids", str(run_id)]
        container_overrides["command"] = command
    submit_job_response = batch.submit_job(
        jobName=job_name,
        jobQueue=job_queue,
        jobDefinition=job_definition,
        containerOverrides=container_overrides,
    )
    job_id = submit_job_response["jobId"]
    print("Submitted job {} {} to the job queue {}".format(job_name, job_id, job_queue))


class GisWorker:

    def __init__(self) -> None:
        self.engine = init_db_engine(
            settings.db_rov_proxy_user,
            settings.db_rov_proxy_password,
            settings.db_rov_proxy_host,
            settings.db_rov_proxy_port,
            settings.db_rov_gis_database
        )
        self.geodata_engine = init_db_engine(
            settings.db_rov_proxy_user,
            settings.db_rov_proxy_password,
            settings.db_rov_proxy_host,
            settings.db_rov_proxy_port,
            settings.db_rov_geodata_database
        )

    def add_mosaic_result(self, raster_result_id: str, mosaic_id: str, user: User):
        with Session(self.engine) as session:
            mosaic = session.get(Mosaic, mosaic_id)
            if mosaic is None:
                print(f'No Mosaic with id ${raster_result_id} found!')
                return None
            if mosaic.organization_id != user.organization_id:
                print(f'This mosaic is not from this org_id: {user.organization_id}')
                return None

            raster_result = session.get(ResultsRaster, raster_result_id)
            if raster_result is None:
                print(f'No Raster with id ${raster_result_id} found!')
                return None

            workspace = user.organization.workspace

            s3 = S3Client(settings.run_results_bucket, settings.s3_region)
            granule_path = s3.get_file_url(key=raster_result.url)
            coverage_store = mosaic.coverage_store
            granules = [granule_path]
            print(f'BORRAR add_mosaic_result with params granules: {granules}, coverage: {coverage_store}, workspace: {workspace}')
            result = add_mosaic_granules(granules, coverage_store, workspace)
            return result

    def remove_mosaic_result(self, raster_result_id: str, mosaic_id: str, user: User):
        # TODO: get Fid of the geoserver table and remove granule
        return False

    def copy_process(self, process_id, user: User):
        with Session(self.engine) as session:
            process_to_copy = session.get(Process, process_id)
            if process_to_copy is None:
                print(f'No process with id ${id} found!')
                return {}
            elif process_to_copy.organization_id != user.organization_id:
                print(f'This process is not from this org_id: {user.organization_id}')
                return None
            else:
                process_type = process_to_copy.type
                new_name = "Copy of " + process_to_copy.name
                model_id: int = process_to_copy.inference_model_id
                area: float = process_to_copy.area
                cost_estimated: float = process_to_copy.cost_estimated
                geom: str = wkbelement_to_wkt(process_to_copy.geom)
                mask = wkbelement_to_wkt(process_to_copy.mask)
                config = process_to_copy.config
                print(f'Process with id: {process_to_copy.id} found! type: {process_type}')

                if process_type == 'on demand':
                    process = Process(
                        name=new_name,
                        cost_estimated=cost_estimated,
                        area=area,
                        type=process_type,
                        inference_model_id=model_id,
                        organization_id=process_to_copy.organization_id,
                        geom=geom,
                        mask=mask,
                        config=config,
                        user_id=user.id
                    )
                    session.add(process)

                    copy_merge_run = False
                    for run in process_to_copy.runs:
                        #Check if run is type merge
                        if run.inference_model_id == 9:
                            copy_merge_run = True
                        else:
                            new_output = RunData(
                                status="waiting",
                                type=run.output.type,
                                user_id=user.id,
                                organization_id=process_to_copy.organization_id,
                            )
                            new_run = Run(
                                status='queued',
                                runtime=run.runtime,
                                engine=run.engine,
                                cost=run.cost,
                                inference_model_version=run.inference_model_version,
                                input=run.input,
                                output=new_output,
                                inference_model_id=run.inference_model_id,
                                process=process
                            )
                            session.add(new_output)
                            session.add(new_run)
                    try:
                        session.commit()
                        if copy_merge_run:
                            print("Copy process: Copying merge last run:")
                            try:
                                session.refresh(process)
                                result = create_merge_run_from_process(session, process, user)
                                return result
                            except Exception as error:
                                print("ERROR Copy process. An exception occurred during second (merge) copy process step:", error)
                                return False
                        else:
                            return True
                    except Exception as error:
                        print("ERROR Copy process. An exception occurred during first copy process step:", error)
                        return False
                elif process_type == 'tasking':
                    data: CreateTaskingDict = {
                        "name": new_name,
                        "inference_model_id": model_id,
                        "area": area,
                        "cost_estimated": cost_estimated,
                        "tasking_config": {},  # TODO: esto hay que hacerlo bien
                        "geom": geom,
                        "mask": mask
                    }
                    return self.create_tasking(data, user)
                else:
                    return False

    def create_process(self, createProcessDict: CreateProcessDict, user: User):
        name = createProcessDict["name"]
        inference_model_id = createProcessDict["inference_model_id"]
        area = createProcessDict["area"]
        cost_estimated = createProcessDict["cost_estimated"]
        images = createProcessDict["images"]
        geom = createProcessDict["geom"]
        mask = createProcessDict["mask"]
        data = createProcessDict["data"]
        user_id = user.id
        organization_id = user.organization_id
        config = {
            "data": data,
            "images": images
        }

        print(f'Creating process for user_id: {user_id}')

        with Session(self.engine) as session:
            # Check if inference_model_id exists
            model = session.get(InferenceModel, inference_model_id)
            if model is None:
                return False

            input_images = {
                "sentinel": [],
                "upload": []
            }
            unsorted_sentinel = []
            for img in images:
                img_type = img.get("type")
                if img_type == "sentinel":
                    data = {
                        "id": img.get("id"),
                        "date": img.get("date"),
                        "title": img.get("title")
                    }
                    unsorted_sentinel.append(data)
                elif img_type == "upload":
                    input_images["upload"].append(img.get("id"))

            input_images["sentinel"] = sorted(unsorted_sentinel, key=get_date)

            print(f'Create process validation on images: {input_images}')
            if len(input_images["upload"]) > 0:
                # Check upload image exists
                img_query_count = session.scalar(
                    select(func.count(Image.id))
                    .where(
                        (Image.id.in_(input_images["upload"])) &
                        (Image.organization_id == organization_id)
                    )
                )
                if img_query_count != len(input_images["upload"]):
                    print(f'Create process validation failed! An Upload image is not valid')
                    return False

            if len(input_images["sentinel"]) > 0:
                # Check format of sentinel uuid
                for data in input_images["sentinel"]:
                    if not is_valid_uuid(data["id"]):
                        print(f'Create process validation failed! A Sentinel image is not valid')
                        return False

            print(f'Create process validation ready!. Adding to DB...')
            process = Process(
                name=name,
                cost_estimated=cost_estimated,
                area=area,
                type='on demand',
                inference_model_id=inference_model_id,
                organization_id=organization_id,
                geom=geom,
                mask=mask,
                user_id=user_id,
                config=config
            )

            # if model is change detector with sentinel, then different process creation with multiple runs
            if inference_model_id == 1:
                if len(input_images["sentinel"]) < 2:
                    print("ERROR Create change detector process. Not enough sentinel images:")
                    return False
                for i in range(len(input_images["sentinel"]) - 1):
                    new_input = RunData(
                        type='change',
                        status="ready",
                        data={
                            "t1": input_images["sentinel"][i],
                            "t2": input_images["sentinel"][i+1],
                            "mask": mask,
                        },
                        user_id=user_id,
                        organization_id=organization_id
                    )
                    session.add(new_input)
                    new_output = RunData(
                        type='raster_result',
                        status='waiting',
                        user_id=user_id,
                        organization_id=organization_id
                    )
                    session.add(new_output)
                    new_run = Run(
                        input=new_input,
                        inference_model_id=inference_model_id,
                        inference_model_version=model.current_version,
                        process=process,
                        output=new_output,
                    )
                    session.add(new_run)
                session.add(process)
                try:
                    session.commit()
                    return True
                except Exception as error:
                    print("ERROR Create change detector process. An exception occurred during DB insertion:", error)
                    return False
            else:
                for img in input_images["upload"]:
                    satellite = data.get("satellite")
                    new_input = RunData(
                        type="raster_upload",
                        status="ready",
                        data={
                            "id": img,
                            "mask": mask,
                            "satellite": satellite
                        },
                        user_id=user_id,
                        organization_id=organization_id,    
                    )
                    session.add(new_input)

                    new_output = RunData(
                        type='vector',
                        status='waiting',
                        user_id=user_id,
                        organization_id=organization_id
                    )
                    session.add(new_output)
                    
                    new_run = Run(
                        input=new_input,
                        inference_model_id=inference_model_id,
                        inference_model_version=model.current_version,
                        process=process,
                        output=new_output,
                    )
                    session.add(new_run)
                session.add(process)
                try:
                    session.commit()
                    return True
                except Exception as error:
                    print("ERROR Create process. An exception occurred during DB insertion:", error)
                    return False

    def create_process_change_detector(self, createProcessChangeDetectorDict: CreateProcessChangeDetectorDict, user: User):
        name = createProcessChangeDetectorDict["name"]
        area = createProcessChangeDetectorDict["area"]
        cost_estimated = createProcessChangeDetectorDict["cost_estimated"]
        date_t1 = createProcessChangeDetectorDict["date_t1"]
        date_t2 = createProcessChangeDetectorDict["date_t2"]
        geom = createProcessChangeDetectorDict["geom"]
        mask = createProcessChangeDetectorDict["mask"]
        data = createProcessChangeDetectorDict["data"]
        user_id = user.id
        organization_id = user.organization_id
        config = {
            "data": data,
            "date_t1": date_t1,
            "date_t2": date_t2
        }

        print(f'Creating process change-detector for user_id: {user_id}')
        t1 = datetime.fromisoformat(date_t1)
        t2 = datetime.fromisoformat(date_t2)

        mask_polygon = wkt.loads(mask)
        coordinates = mapping(mask_polygon).get("coordinates")
        geojson_polygon = geojson.Polygon(coordinates)
        days = data.get("days", 15)
        window = timedelta(days=days)
        alpha = data.get("alpha", 0.8)
        max_cloud = data.get("max_cloud", 30)

        runs_inputs = changeDetectTask(t1, t2, geojson_polygon, window, alpha, max_cloud)
        print(f'Creating process change-detector run_inputs: #{len(runs_inputs)}')
        if len(runs_inputs) == 0:
            return None
        with Session(self.engine) as session:
            model = session.get(InferenceModel, 1)
            if model is None:
                return None
            process = Process(
                name=name,
                cost_estimated=cost_estimated,
                area=area,
                type='on demand',
                inference_model_id=model.id,
                organization_id=organization_id,
                geom=geom,
                mask=mask,
                user_id=user_id,
                config=config
            )

            for run_input in runs_inputs:
                run_input_t1 = run_input.get("t1")
                run_input_t2 = run_input.get("t2")
                run_input_mask = run_input.get("mask")
                new_input = RunData(
                    type='change',
                    status="ready",
                    data={
                        "t1": run_input_t1,
                        "t2": run_input_t2,
                        "mask": run_input_mask.wkt,
                    },
                    user_id=user_id,
                    organization_id=organization_id
                )
                session.add(new_input)
                new_output = RunData(
                    type='vector',
                    status='waiting',
                    user_id=user_id,
                    organization_id=organization_id
                )
                session.add(new_output)
                new_run = Run(
                    input=new_input,
                    inference_model_id=model.id,
                    inference_model_version=model.current_version,
                    process=process,
                    output=new_output,
                )
                session.add(new_run)
            session.add(process)
            try:
                session.commit()
                session.refresh(process)
                print(f'Creating process change-detector process: {process.id}, STEP 1 DONE!')
                # Create merge last run
                if len(runs_inputs) > 1:
                    print(f'Creating process change-detector process: {process.id}, starting last Run merge creation!')
                    result_create_merge_run = create_merge_run_from_process(session, process, user)
                    if result_create_merge_run:
                        print(f'Creating process change-detector process: {process.id}, STEP 2 DONE!')
                        return process.id
                    else:
                        print("ERROR Create change detector process. Could not create last merge run")
                        return None
                else:
                    return process.id
            except Exception as error:
                print("ERROR Create change detector process. An exception occurred during process creation:", error)
                return None

    def execute_runs_by_process(self, process_id: str, user: User):
        with Session(self.engine) as session:
            organization_id = session.scalar(select(Process.organization_id).where(Process.id == process_id))

            if organization_id is None or organization_id != user.organization_id:
                return None

            query_run = (
                select(Run)
                .where(Run.process_id == id)
                .order_by(Run.id)
            )
            runs = session.scalars(query_run).all()
            if len(runs) == 0:
                print(f'No runs for process_id ${id}')
                return []
            print(f'Runs for process_id={id} found!: {len(runs)} processes')
            runs_to_execute = []

            for run in runs:
                input_run_data = run.input
                if input_run_data.type != 'merge':
                    runs_to_execute.append(run.id)

            name = f'Job process #{id}'
            try:
                submit_job(name, runs_to_execute)
                return True
            except Exception as error:
                # handle the exception
                print("ERROR execute_runs_by_process. An exception occurred during submit job:", error)
                return False

    def create_tasking(self, data: CreateTaskingDict, user: User):
        name = data["name"]
        inference_model_id = data["inference_model_id"]
        area = data["area"]
        cost_estimated = data["cost_estimated"]
        tasking_config = data["tasking_config"]
        user_id = user.id
        geom = data["geom"]
        mask = data["mask"]
        organization_id = user.organization_id

        print(f'Creating tasking for user_id: {user_id}')

        # Check if inference_model_id exists
        with Session(self.engine) as session:
            model = session.get(InferenceModel, inference_model_id)
            if model is None:
                return False

            process = Process(
                name=name,
                cost_estimated=cost_estimated,
                area=area,
                inference_model_id=inference_model_id,
                data=tasking_config,
                organization_id=organization_id,
                type='tasking',
                geom=geom,
                mask=mask,
                user_id=user_id,
                config=data
            )

            session.add(process)
            try:
                session.commit()
                return True
            except Exception as error:
                # handle the exception
                print("Create tasking. An exception occurred during DB insertion:", error)
                return False

    def get_inference_models(self):
        with Session(self.engine) as session:
            query = (
                select(InferenceModel)
                .order_by(InferenceModel.id)
            )
            models = session.scalars(query).all()
            if models is None or len(models) == 0:
                return []
            result = []
            for model in models:
                result.append({
                    "id": model.id,
                    "name": model.name,
                    "title": model.title,
                    "description": model.description,
                    "img_url": model.img_url,
                    "price": model.price,
                    "type": model.type,
                    "current_version": model.current_version,
                    "min_resolution": model.min_resolution,
                    "config": model.config
                })
            return result

    def get_inference_model_by_id(self, id: str):
        with Session(self.engine) as session:
            model = session.get(InferenceModel, id)
            if model is None:
                return {}
            print(f'Model with id: {id} found! ')
            return {
                "id": model.id,
                "name": model.name,
                "title": model.title,
                "description": model.description,
                "img_url": model.img_url,
                "price": model.price,
                "type": model.type,
                "current_version": model.current_version,
                "min_resolution": model.min_resolution,
                "config": model.config
            }

    def load_images_by_org(self, organization_id: str):
        with Session(self.engine) as session:
            query = (
                select(Image)
                .where(
                    (Image.organization_id == organization_id)
                )
            )
            images = session.scalars(query)
            if images is None:
                return {}
            result = []
            for img in images:
                bbox = None
                footprint = None
                if img.bbox is not None:
                    bbox = wkbelement_to_wkt(img.bbox)
                if img.footprint is not None:
                    footprint = wkbelement_to_wkt(img.footprint)
                result.append({
                    "id": img.id,
                    "name": img.name,
                    "created_at": img.created_at,
                    "url": img.url,
                    "data": img.data,
                    "bbox": bbox,
                    "footprint": footprint,
                    "user": img.user.username
                })
            return result

    def load_mosaics_by_org(self, organization_id: str):
        with Session(self.engine) as session:
            query = (
                select(Mosaic)
                .where(
                    (Mosaic.organization_id == organization_id)
                )
            )
            mosaics = session.scalars(query)
            if mosaics is None:
                return {}
            result = []
            for mosaic in mosaics:
                result.append({
                    "id": mosaic.id,
                    "name": mosaic.name,
                    "description": mosaic.description,
                    "created_at": mosaic.created_at,
                    "coverage_store": mosaic.coverage_store,
                    "workspace": mosaic.organization.workspace
                })
            return result

    def load_process_by_id(self, id: str, user: User):
        with Session(self.engine) as session:
            process = session.get(Process, id)
            if process is None:
                print(f'No process with id ${id} found!')
                return {}
            elif process.organization_id != user.organization_id:
                print(f'This process is not from this org_id: {user.organization_id}')
                return None
            else:
                print(f'Process with id: {id} found! ')
                geom = None
                if process.geom is not None:
                    geom = wkbelement_to_wkt(process.geom)
                mask = None
                if process.mask is not None:
                    mask = wkbelement_to_wkt(process.mask)
                return {
                    "id": process.id,
                    "name": process.name,
                    "status": process.status,
                    "type": process.type,
                    "created_at": process.created_at,
                    "finished_at": process.finished_at,
                    "runtime": process.runtime,
                    "area": process.area,
                    "cost_estimated": process.cost_estimated,
                    "inference_model_id": process.inference_model_id,
                    "config": process.config,
                    "user_id": process.user_id,
                    "organization_id": process.organization_id,
                    "geom": geom,
                    "mask": mask,
                }

    def load_processes_by_org(self, org_id: int):
        with Session(self.engine) as session:
            query = (
                select(Process)
                .where(Process.organization_id == org_id)
                .order_by(Process.id)
            )
            processes = session.scalars(query).all()
            if processes is None:
                print(f'No processes for org_id ${org_id}')
                return []
            result = []
            print(f'Processes for org_id={org_id} found!: {len(processes)} processes')
            for process in processes:
                geom = None
                if process.geom is not None:
                    geom = wkbelement_to_wkt(process.geom)
                mask = None
                if process.mask is not None:
                    mask = wkbelement_to_wkt(process.mask)
                result.append({
                    "id": process.id,
                    "name": process.name,
                    "status": process.status,
                    "type": process.type,
                    "created_at": process.created_at,
                    "finished_at": process.finished_at,
                    "runtime": process.runtime,
                    "area": process.area,
                    "cost_estimated": process.cost_estimated,
                    "config": process.config,
                    "inference_model_id": process.inference_model_id,
                    "user_id": process.user_id,
                    "organization_id": process.organization_id,
                    "geom": geom,
                    "mask": mask,
                })
            return result

    def load_results_by_run_id(self, id: str):
        results = {
            "vector": [],
            "raster": []
        }
        with Session(self.engine) as session:
            output_id = session.scalar(select(Run.output_id).where(Run.id == id))
            query_vector = (
                select(ResultsVector)
                .where(ResultsVector.run_data_id == output_id)
                .order_by(ResultsVector.id)
            )
            vector_results = session.scalars(query_vector).all()
            if len(vector_results) == 0:
                print(f'No vector results for run_id ${id}')
            else:
                print(f'Vector results for run_id={id} found!: {len(vector_results)} results')
                for vector_result in vector_results:
                    wkt = wkbelement_to_wkt(vector_result.geom)
                    results["vector"].append({
                        "id": vector_result.id,
                        "data": vector_result.data,
                        "geom": wkt
                    })

            query_raster = (
                select(ResultsRaster)
                .where(ResultsRaster.run_data_id == output_id)
                .order_by(ResultsRaster.id)
            )
            raster_results = session.scalars(query_raster).all()
            if len(raster_results) == 0:
                print(f'No raster results for run_id ${id}')
            else:
                print(f'Raster results for run_id={id} found!: {len(raster_results)} results')
                for raster_result in raster_results:
                    wkt = wkbelement_to_wkt(raster_result.bbox)
                    results["raster"].append({
                        "id": raster_result.id,
                        "url": raster_result.url,
                        "data": raster_result.data,
                        "bbox": wkt
                    })

            return results

    def load_runs_by_process(self, id: str, user: User):
        with Session(self.engine) as session:
            organization_id = session.scalar(select(Process.organization_id).where(Process.id == id))

            if organization_id is None or organization_id != user.organization_id:
                return None

            query_run = (
                select(Run)
                .where(Run.process_id == id)
                .order_by(Run.id)
            )
            runs = session.scalars(query_run).all()
            if len(runs) == 0:
                print(f'No runs for process_id ${id}')
                return []
            print(f'Runs for process_id={id} found!: {len(runs)} processes')
            results = []

            for run in runs:
                results.append({
                    "id": run.id,
                    "status": run.status,
                    "created_at": run.created_at,
                    "finished_at": run.finished_at,
                    "engine": run.engine,
                    "runtime": run.runtime,
                    "cost": run.cost,
                    "input_id": run.input_id,
                    "output_id": run.output_id,
                    "inference_model_id": run.inference_model_id,
                    "inference_model_version": run.inference_model_version
                })

            return results

    def load_run_by_id(self, id: str, user: User):
        with Session(self.engine) as session:
            run = session.get(Run, id)
            if run is None:
                print(f'No run with id ${id} found!')
                return {}
            elif run.process.organization_id != user.organization_id:
                print(f'This process is not from this org_id: {user.organization_id}')
                return None
            else:
                print(f'Run with id: {id} found! ')
                return {
                    "id": run.id,
                    "status": run.status,
                    "created_at": run.created_at,
                    "finished_at": run.finished_at,
                    "engine": run.engine,
                    "runtime": run.runtime,
                    "cost": run.cost,
                    "process_id": run.process_id,
                    "inference_model_id": run.inference_model_id,
                    "inference_model_version": run.inference_model_version,
                    "input_id": run.input_id,
                    "output_id": run.output_id
                }

    def upload_image(self, img: UploadImageDict, user: User):
        name = img["name"]
        url = img["url"]
        bbox = img["bbox"]
        area = get_wkt_area(bbox)/1000000
        data = {
            "area": area,
            "thumbnail_url": ""
        }
        print(f'Adding new uploaded image: {name} from user_id: {user.id}')
        with Session(self.engine) as session:
            new_image = Image(
                name=name,
                url=url,
                data=data,
                bbox=bbox,
                user_id=user.id,
                organization_id=user.organization_id
            )
            session.add(new_image)
            session.commit()
            return new_image

    def add_run_data_output(self, run_data_id, data=None):
        with Session(self.engine) as session:
            runData = session.get(RunData, run_data_id)
            if runData is None:
                print(f'Run data {run_data_id} does not exists')
            else:
                runData.data = data
                runData.status = "ready"
                session.commit()

    def add_raster_results(self, run_data_id, object_key, data=None, bbox=None):
        with Session(self.engine) as session:
            new_result = ResultsRaster(
                url=object_key,
                data=data,
                bbox=bbox,
                run_data_id=run_data_id,
            )
            session.add(new_result)
            session.commit()
            return new_result
        
    def add_vector_result(self, run_data_id, geom, data=None):
        with Session(self.engine) as session:
            new_result = ResultsVector(
                data=data,
                geom=geom,
                run_data_id=run_data_id,
            )
            session.add(new_result)
            session.commit()
            return new_result
        
    def add_vector_results(self, run_data_id, vector_results):
        with Session(self.engine) as session:
            for result in vector_results:
                new_result = ResultsVector(
                    data=result.data,
                    geom=result.geom,
                    run_data_id=run_data_id,
                )
                session.add(new_result)
            session.commit()
            return new_result

    def delete_process(self, id: str, user: User):
        with Session(self.engine) as session:
            query = (
                select(Process)
                .where(
                    and_(
                        (Process.id == id),
                        (Process.organization_id == user.organization_id)
                    )
                )
                .limit(1)
            )
            process = session.scalar(query)
            if process is None:
                print(f'No process with id ${id} found!')
                return False
            else:
                print(f'Deleting process with id: {id}')
                session.delete(process)
                session.commit()
                return True

    def get_geojson_results(self, run_id: str):
        result = {
            'type': 'FeatureCollection',
            'features': []
        }
        features = []
        with Session(self.engine) as session:
            output_id = session.scalar(select(Run.output_id).where(Run.id == run_id))
            query_vector = (
                select(st_geojson(ResultsVector))
                .where(ResultsVector.run_data_id == output_id)
                .order_by(ResultsVector.id)
            )
            vector_results = session.scalars(query_vector).all()
            if len(vector_results) == 0:
                print(f'No vector results for run_id ${run_id}')
            else:
                print(f'Vector results for run_id={run_id} found!: {len(vector_results)} results')
                for vector in vector_results:
                    vector_json = json.loads(vector)
                    features.append(vector_json)
            result["features"] = features
            return json.dumps(result)

    def get_raster_img_url(self, id: str, user: User):
        with Session(self.engine) as session:
            raster = session.get(ResultsRaster, id)
            if raster is None:
                print(f'No raster result with id: {id} found!')
                return None
            else:
                print(f'Raster result with id: {id} found!')
                return raster.url

    def get_run_data(self, id: str, user: User):
        with Session(self.engine) as session:
            run_data = session.get(RunData, id)
            if run_data is None:
                print(f'No run_data with id ${id} found!')
                return None
            else:
                print(f'Run_data with id: {id} found!')
                if run_data.organization_id != user.organization_id:
                    print(f'No permission allowed for this user!')
                    return None
                return run_data

    def get_run_data_data(self, id: str, user: User):
        with Session(self.engine) as session:
            run_data = session.get(RunData, id)
            if run_data is None:
                print(f'No run_data with id ${id} found!')
                return None
            else:
                print(f'Run_data with id: {id} found!')
                data = run_data.data
                if run_data.organization_id != user.organization_id:
                    print(f'No permission allowed for this user!')
                    return None
                if data is None:
                    print(f'No data for run_data id ${id} found!')
                    return None
                return data

    def edit_process_name(self, id: str, name: str, user: User):
        with Session(self.engine) as session:
            query = (
                select(Process)
                .where(
                    and_(
                        (Process.id == id),
                        (Process.organization_id == user.organization_id)
                    )
                )
                .limit(1)
            )
            process = session.scalar(query)
            if process is None:
                print(f'No process with id ${id} found!')
                return False
            else:
                print(f'Editing process name with id: {id}')
                process.name = name
                session.commit()
                return True

    def get_vector_runs(self, org_id: int):
        with Session(self.engine) as session:
            query = (
                select(RunData, Process.name, Run.id)
                .join(Run, RunData.id == Run.output_id)
                .join(Process, Process.id == Run.process_id)
                .where(
                    (RunData.organization_id == org_id) &
                    (RunData.type == 'vector')
                )
            )
            results = session.execute(query).all()
            if results is None:
                return []
            runs_data = []
            for run_data, process_name, run_id in results:
                run_data_serialized = run_data.serialize()
                run_data_serialized['process_name'] = process_name
                run_data_serialized['run_id'] = run_id
                runs_data.append(run_data_serialized)
            return runs_data

    def execute_query(self, query, engine):
        with Session(engine) as session:
            results = session.execute(query).all()
        return results

    def analysis_operation_tool(self, operation: str, type1: str, type2: str, entity1: str | int, entity2: str | int):
        # entities are wkt
        if type1 == 'wkt':
            item1 = OpWkt(entity1)
            item1.add_srid(4326)
        if type2 == 'wkt':
            item2 = OpWkt(entity2)
            item2.add_srid(4326)

        # entities are output_data_id in ResultsVector Table
        if type1 == 'vector':
            item1 = OpVectorResult(entity1)
        if type2 == 'vector':
            item2 = OpVectorResult(entity2)

        # entities are layer in geodata_engine (table name of the layer)
        if type1 == 'layer':
            item1 = OpLayer(entity1, self.geodata_engine)
        if type2 == 'layer':
            item2 = OpLayer(entity2, self.geodata_engine)

        if type1 == 'wkt' and type2 == 'wkt':
            query = item2.operate(item1, operation)
            result = self.execute_query(query, self.engine)
            return [{
                "id": None,
                "geom": wkbelement_to_wkt(result[0][0]),
                "data": None
            }]

        if type1 == 'vector' or type2 == 'vector':
            vector_obj = item1 if type1 == 'vector' else item2
            wkt_obj = item1 if type1 == 'wkt' else item2
            query = wkt_obj.operate(vector_obj, operation)
            results = self.execute_query(query, self.engine)
            return [{
                "id": result[0].id,
                "geom": wkbelement_to_wkt(result[1]),
                # result[0].data  # Accessing the data column of ResultsVector
                "data": None
            } for result in results]

        if type1 == 'layer' or type2 == 'layer':
            layer_obj = item1 if type1 == 'layer' else item2
            wkt_obj = item1 if type1 == 'wkt' else item2
            query = wkt_obj.operate(layer_obj, operation)
            results = self.execute_query(query, self.geodata_engine)
            return [{
                "id": result[0],
                "geom": wkbelement_to_wkt(result[-1]),
                # "data": {col: result[idx] for idx, col in enumerate(table.columns.keys()) if col != 'geom' and col != 'geom_intersection'}
                "data": None
            } for result in results]

        return None

    def wkt_buffer(self, wkt: str, distance: float):
        with Session(self.engine) as session:
            wkt = add_srid_to_raw_wkt(wkt)
            query = select(
                func.ST_Transform(
                    func.ST_Buffer(
                        func.ST_Transform(wkt, 32719),
                        distance
                    )
                , 4326)
            )
            result = session.scalar(query)
            new_wkt = wkbelement_to_wkt(result)
            #save for testing
            # if result:
            #     session.add(GeomTest(geom=result))
            #     session.commit()
            return new_wkt

    def get_operation_entity(self, type: str, entity: str | int, id: int):
        if type == 'vector':
            with Session(self.engine) as session:
                query = (
                    select(ResultsVector)
                    .where(ResultsVector.id == id)
                    .where(ResultsVector.run_data_id == entity)
                )

                result = session.execute(query).first()

                if result is None:
                    return None

                result_data = result[0]

                return {
                    "id": result_data.id,
                    "data": result_data.data
                }

        if type == 'layer':
            with Session(self.geodata_engine) as geo_session:
                metadata = MetaData(schema='infrastructure')
                table = Table(entity, metadata, autoload_with=self.geodata_engine)
                query = select(table).where(table.c.id == id)
                result = geo_session.execute(query).first()
                return {col: result[idx] for idx, col in enumerate(table.columns.keys()) if col != 'geom'}

        return None

#######################################
######### library methods #############
#######################################

    def add_mosaic_inputs(self, granule_path_list: List[str], mosaic_id: str):
        with Session(self.engine) as session:
            mosaic = session.get(Mosaic, mosaic_id)
            if mosaic is None:
                print(f'No Mosaic with id ${mosaic_id} found!')
                return None
            # TODO: Agregar esta verificacion en caso que esta funcion se ocupe desde un API endpoint
            # if mosaic.organization_id != user.organization_id:
            #     print(f'This mosaic is not from this org_id: {user.organization_id}')
            #     return None

            workspace = mosaic.organization.workspace
            coverage_store = mosaic.coverage_store

            print(f'BORRAR add_mosaic_inputs with params granules: {granule_path_list}, coverage: {coverage_store}, workspace: {workspace}')
            result = add_mosaic_granules(granule_path_list, coverage_store, workspace)
            return result

    def download_image_from_library(self, image_id: int, filepath: str = None):
        with Session(self.engine) as session:
            image = session.get(Image, image_id)
            if image is None:
                print(f'No image with id ${image_id} found!')
                return False
        print(f'Image found: ${image}')
        s3 = S3Client(settings.gis_inference_bucket, settings.gis_inference_region)
        if filepath is None:
            s3.download_file(image.url, image.name)
        else:
            s3.download_file(image.url, os.path.join(filepath, image.name))
        return True

    def update_run_status(self, run_id: int, status: Literal['queued', 'running', 'finished', 'failed', 'canceled']):
        """
        Updates the status of the run

        Args:
            run_id: The id of the run
            status: The new status of the run
        """
        assert isinstance(run_id, int), 'Invalid run_id!'
        assert status in ['queued', 'running', 'finished', 'failed', 'canceled'], 'Invalid status!'

        with Session(self.engine) as session:
            run = session.get(Run, run_id)
            if run is None:
                print(f'No run with id ${run_id} found!')
                return False
            run.status = status
            if status == 'running':
                run.process.status = 'running'
            session.commit()
            return True

    def upload_run_results(self, run_id: int, runtime: int, bbox: str, files_path: str, raster_name: str, preview_name: str, file_names: list[str]=[], data: dict=None):
        """
        Uploads the files to the S3 bucket and updates the run status to finished

        Args:
            run_id: The id of the run
            bbox: The bbox of the raster
            files_path: The path where the files are located
            runtime: The runtime of the run
            raster_name: The name of the raster file
            preview_name: The name of the preview file (i.e: thumbnail.png)
            file_names: Array with the names of additional files to upload
            data: additional data to store in the results raster table
        """
        assert isinstance(run_id, int), 'Invalid run_id!'
        assert bbox is None or isinstance(bbox, str), 'Invalid bbox!'
        assert isinstance(runtime, (int, float)), 'Invalid runtime!'
        runtime = int(runtime)
        assert isinstance(files_path, str), 'Invalid files_path!'
        assert raster_name is None or isinstance(raster_name, str), 'Invalid raster_name!'
        assert preview_name is None or isinstance(preview_name, str), 'Invalid preview_name!'
        assert isinstance(file_names, list), 'Invalid file_names!'
        assert data is None or isinstance(data, dict), 'Invalid data!'

        assert raster_name is not None or len(file_names) != 0, 'No files to upload!'

        with Session(self.engine) as session:
            # actual function
            run = session.get(Run, run_id)
            if run is None:
                print(f'No run with id {run_id} found!')
                return False

            process_id = run.process_id
            org_id = run.process.organization_id
            run_id = run.id

            # upload files to bucket
            s3_client = S3Client(settings.run_results_bucket, settings.s3_region)
            bucket_base_directory = f"{org_id}/{process_id}/{run_id}/"

            for file_name in file_names:
                if not isinstance(file_name, str):
                    print('Invalid file_name!')
                    return False
                print(f'Uploading file: {file_name}')
                object_key = bucket_base_directory + file_name
                file_path = os.path.join(files_path, file_name)
                s3_client.upload_file(file_path, object_key)
                print(f'File uploaded to S3 with key: {object_key}')

            if raster_name is not None:
                print(f'Uploading raster file: {raster_name}')
                object_key = bucket_base_directory + raster_name
                file_path = os.path.join(files_path, raster_name)
                s3_client.upload_file(file_path, object_key)
                print(f'File uploaded to S3 with key: {object_key}')
                self.add_raster_results(run.output_id, object_key, data, bbox)

            if preview_name is not None:
                print(f'Uploading preview file: {preview_name}')
                object_key = bucket_base_directory + preview_name
                file_path = os.path.join(files_path, preview_name)
                s3_client.upload_file(file_path, object_key)
                print(f'File uploaded to S3 with key: {object_key}')

            # update Run status
            # when all runs of a process are finished, an SQL trigger will update the process status
            run.status = 'finished'
            run.finished_at = func.now()

            # SQL trigger will update the process runtime
            run.runtime = runtime
            # run.filepath = bucket_base_directory
            session.commit()

            # update RunData status and data
            run_data_data = {
                'bbox': bbox,
                'preview': bucket_base_directory + preview_name
            }
            self.add_run_data_output(run_data_id=run.output_id, data=run_data_data)

            return True

    def upload_run_vector_results(self, run_id: int, runtime: int, bbox: str, geojson_input: Dict[str, Any], preview_name: str, files_path: str, file_names: list[str]=[], data: dict=None):
        """
        Inserts polygons from a GeoJSON input into the results_vector table.

        :param run_id: The ID of the Run to associate with the ResultsVector entries.
        :param runtime: The runtime of the run.
        :param bbox: The bbox of the preview
        :param geojson_input: GeoJSON input containing multiple polygons.
        :param preview_name: The name of the preview file (i.e: thumbnail.png).
        :param files_path: The path where the files are located
        :param file_names: Array with the names of additional files to upload
        :param data: additional data to store in the results vector table
        """
        assert isinstance(run_id, int), 'Invalid run_id!'
        assert bbox is None or isinstance(bbox, str), 'Invalid bbox!'
        assert isinstance(runtime, (int, float)), 'Invalid runtime!'
        runtime = int(runtime)
        assert isinstance(files_path, str), 'Invalid files_path!'
        assert isinstance(file_names, list), 'Invalid file_names!'
        assert preview_name is None or isinstance(preview_name, str), 'Invalid preview_name!'

        # Ensure the input is a FeatureCollection
        if geojson_input.get("type") != "FeatureCollection":
            raise ValueError("Input GeoJSON must be a FeatureCollection")

        with Session(self.engine) as session:
            run = session.get(Run, run_id)
            if run is None:
                print(f'No run with id {run_id} found!')
                return False

            process_id = run.process_id
            org_id = run.process.organization_id
            run_id = run.id

            # upload files to bucket
            s3_client = S3Client(settings.run_results_bucket, settings.s3_region)
            bucket_base_directory = f"{org_id}/{process_id}/{run_id}/"

            for file_name in file_names:
                if not isinstance(file_name, str):
                    print('Invalid file_name!')
                    return False
                print(f'Uploading file: {file_name}')
                object_key = bucket_base_directory + file_name
                file_path = os.path.join(files_path, file_name)
                s3_client.upload_file(file_path, object_key)
                print(f'File uploaded to S3 with key: {object_key}')

            if preview_name is not None:
                print(f'Uploading preview file: {preview_name}')
                object_key = bucket_base_directory + preview_name
                file_path = os.path.join(files_path, preview_name)
                s3_client.upload_file(file_path, object_key)
                print(f'File uploaded to S3 with key: {object_key}')

            run_data_id = run.output_id

            results_vector_list = []
            for feature in geojson_input.get("features", []):
                if feature.get("type") != "Feature":
                    continue

                geometry = feature.get("geometry")
                properties = feature.get("properties", {})

                # Ensure the geometry type is MultiPolygon
                #if not (geometry.get("type") == "MultiPolygon" or geometry.get("type") == "Polygon"):
                #    raise ValueError("Only Polygon & MultiPolygon geometries are supported")

                polygon = shape(geometry)
                wkt = "SRID=4326;" + polygon.wkt

                # Create a new ResultsVector instance
                result_vector = ResultsVector(
                    data=properties,
                    geom=wkt,
                    run_data_id=run_data_id
                )

                results_vector_list.append(result_vector)

            # update Run status
            # when all runs of a process are finished, an SQL trigger will update the process status
            # an SQL trigger will also merge all the overlapping polygons if needed
            run.status = 'finished'
            run.finished_at = func.now()
            run.runtime = runtime

            session.add_all(results_vector_list)
            session.commit()

            # update RunData status and data
            run_data_data = {
                'bbox': bbox,
                'preview': bucket_base_directory + preview_name
            }
            self.add_run_data_output(run_data_id=run_data_id, data=run_data_data)

    def load_queued_runs_ids_by_model(self, model_id: str):
        with Session(self.engine) as session:
            query_runs = (
                select(Run.id)
                .where(Run.inference_model_id == model_id)
                .where(Run.status == 'queued')
                .order_by(Run.id)
            )
            runs = session.scalars(query_runs).all()
            if runs is None or len(runs) == 0:
                return []
            else:
                print(f'Queued runs found!: {len(runs)} results')
                return runs

    def load_run_input(self, run_id: str):
        with Session(self.engine) as session:
            query = select(Run.input_id).where(Run.id == run_id)
            input_id = session.scalar(query)
            input = session.get(RunData, input_id)
            
            if input is None:
                print('Run with corrupted Input data')
                return None
            elif input.status == 'waiting':
                print('Run data is not ready yet')
                return None
            else:
                return input.data
