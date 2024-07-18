import pandas as pd
import json
import requests
from pydantic import ValidationError
from werkzeug.datastructures import FileStorage

import dhuolib.utils as ut
from dhuolib.config import logger
from dhuolib.services import ServiceAPIMLFacade
from dhuolib.utils import validate_name
from dhuolib.validations import (
    ExperimentBody,
    PredictBatchModelBody,
    PredictOnlineModelBody,
    RunExperiment,
    TransitionModel,
    RunSearch,
    ModelBody,
)


class DhuolibExperimentMLClient:
    def __init__(self, service_uri: str, token: str = None):
        if not service_uri:
            raise ValueError("service_uri is required")

        if not token:
            raise ValueError("token is required")

        self.service = ServiceAPIMLFacade(service_uri=service_uri, token=token)

    def create_experiment(
        self, experiment_name: str, experiment_tags: dict = None
    ) -> dict:
        try:
            experiment = ExperimentBody.model_validate(
                {
                    "experiment_name": validate_name(experiment_name),
                    "experiment_tags": experiment_tags,
                }
            )
        except ValidationError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}

        response = self.service.experiment_api.create(experiment.model_dump())
        logger.info(f"Experiment Name: {experiment.experiment_name} created")

        return response

    def predict_online(self, run_params) -> dict:
        try:
            PredictOnlineModelBody.model_validate(run_params)
        except ValidationError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}
        try:
            with open(run_params["data"], "rb") as f1:
                files = {
                    "data": FileStorage(
                        stream=f1, filename="data.csv", content_type="csv"
                    )
                }
                response = self.service.experiment_api.predict_online(
                    params=run_params, files=files
                )
                logger.info(f"Model Name: {run_params['modelname']} predictions")
                return response
        except FileNotFoundError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}

    def _get_model_to_prediction(self, predict: PredictBatchModelBody) -> dict:

        path_to_pickle = self.service.experiment_api.download_pickle(
            model_name=predict.modelname,
            model_stage=predict.stage,
            run_id=predict.run_id,
            experiment_name=predict.experiment_name,
            local_filename=predict.batch_model_dir,
            type_model=predict.type_model,
        )

        return ut.load_pickle_model(path_to_pickle)

    def prediction_batch_with_dataframe(
        self, batch_params: dict, df: pd.DataFrame
    ) -> dict:
        try:
            predict = PredictBatchModelBody.model_validate(batch_params)
        except ValidationError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}

        model = self._get_model_to_prediction(predict)
        return model.predict(df)

    def search_experiments(
        self, filter_string: str = "", max_results: int = 10, page_token: str = ""
    ) -> dict:

        response = self.service.experiment_api.search(
            filter_string=filter_string, max_results=max_results, page_token=page_token
        )
        return response

    def execute_run_for_experiment(
        self,
        type_model: str,
        experiment_name: str,
        modelpkl_path: str,
        requirements_path: str,
        tags={},
    ) -> dict:

        if not experiment_name or not modelpkl_path or not requirements_path:
            raise ValueError(
                "experiment_name, modelpkl_path and requirements_path are required"
            )
        params = {
            "type_model": type_model,
            "experiment_name": experiment_name,
            "tags": tags,
        }

        try:
            RunExperiment.model_validate(params)
        except ValidationError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}

        try:
            with open(requirements_path, "rb") as f1, open(modelpkl_path, "rb") as f2:
                files = {
                    "requirements_path": (requirements_path, f1, "text/plain"),
                    "modelpkl_path": (modelpkl_path, f2, "application/octet-stream"),
                }

                chunk_size = 10 * 1024 * 1024
                for file_name, file_info in files.items():
                    file_path, file_obj, content_type = file_info
                    while True:
                        chunk = file_obj.read(chunk_size)
                        if not chunk:
                            break
                        self.service.runs_api.upload_chunk(
                            chunk=chunk,
                            content_type=content_type,
                            experiment_name=experiment_name,
                            file_name=file_name,
                            file_path=file_path,
                        )

                response = self.service.runs_api.create(run_params=params)
                logger.info(f"Experiment Name: {params['experiment_name']} running")
                return response
        except FileNotFoundError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}

    def search_runs(
        self,
        filter_string: str = "",
        max_results: int = 10,
        page_token: str = "",
        experiment_name: str = "",
    ) -> dict:

        if experiment_name == "":
            raise ValueError("experiment_name is required")
        try:
            RunSearch.model_validate(
                {
                    "experiment_name": experiment_name,
                    "filter_string": filter_string,
                    "max_results": max_results,
                    "page_token": page_token,
                }
            )
        except ValidationError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}
        try:
            response = self.service.runs_api.search(
                filter_string=filter_string,
                max_results=max_results,
                page_token=page_token,
                experiment_name=experiment_name,
            )
            return response
        except ValueError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}

    def create_model(
        self, modelname: str, stage: str, run_id: str, model_uri: str, tags: dict
    ) -> dict:
        try:
            transition_model = ModelBody.model_validate(
                {
                    "modelname": validate_name(modelname),
                    "stage": stage,
                    "run_id": run_id,
                    "model_uri": model_uri,
                    "tags": tags,
                }
            )
            response = self.service.model_api.create(transition_model.model_dump())
            return response
        except ValidationError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}

    def transition_model(self, model_name: str, version: str, stage: str) -> dict:
        try:
            TransitionModel.model_validate(
                {"model_name": model_name, "version": version, "stage": stage}
            )
        except ValidationError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}

        response = self.service.model_api.transition_model(
            model_name=model_name, version=version, stage=stage
        )
        return response

    def search_models(
        self, filter_string: str = "", max_results: int = 10, page_token: str = ""
    ) -> dict:
        response = self.service.model_api.search(
            filter_string=filter_string, max_results=max_results, page_token=page_token
        )
        return response
