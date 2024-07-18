import json
import requests
from abc import ABC, abstractmethod


class APIError(Exception):
    pass


class ServiceML(ABC):
    def __init__(self, service_uri: str = "http://localhost:8000", token: str = None):
        self.service_uri = f"{service_uri}/api"
        self.token = token

    @abstractmethod
    def create(self, params, **kwargs):
        pass

    @abstractmethod
    def search(
        self,
        filter_string: str = "",
        max_results: int = 10,
        page_token: str = None,
        **kwargs,
    ):
        pass

    def _handle_response(self, response):
        if not response.ok:
            raise APIError(
                f"API request failed with status {response.status_code}: {response.text}"
            )
        return response.json()


class ExperimentMLAPI(ServiceML):
    def __init__(self, service_uri, token):
        super().__init__(service_uri, token)
        self.service_uri = f"{self.service_uri}/experiment"
        self.authorization_header = {"Authorization": f"Bearer {token}"}
        self.headers = {"Content-Type": "application/json", **self.authorization_header}

    def create(self, experiment_params: dict):
        response = requests.post(
            f"{self.service_uri}",
            data=json.dumps(experiment_params),
            headers=self.headers,
        )
        return self._handle_response(response)

    def search(
        self,
        filter_string: str = "",
        max_results: int = 10,
        page_token: str = "",
        view_type: int = 1,
    ):
        response = requests.get(
            f"{self.service_uri}/search?filter_string={filter_string}&max_results={max_results}&page_token={page_token}&view_type={view_type}",
            headers=self.authorization_header,
        )
        return self._handle_response(response)

    def predict_online(self, params={}, files=None):
        if params is None and not isinstance(params, dict):
            raise ValueError("json_data must be a dict")
        response = requests.post(
            f"{self.service_uri}/predict_online",
            data=params,
            files=files,
        )
        return self._handle_response(response)

    def download_pickle(
        self,
        experiment_name: str,
        type_model: str,
        model_name: str,
        model_stage: str = "",
        run_id: str = "",
        local_filename: str = "model.pickle",
    ):
        url = f"{self.service_uri}/dowload/batch/{experiment_name}/{model_name}?model_stage={model_stage}&run_id={run_id}&type_model={type_model}"
        with requests.get(url, stream=True, headers=self.authorization_header) as r:
            r.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return local_filename


class ModelMLAPI(ServiceML):
    def __init__(self, service_uri, token):
        super().__init__(service_uri, token)
        self.service_uri = f"{self.service_uri}/models"
        self.authorization_header = {"Authorization": f"Bearer {token}"}
        self.headers = {"Content-Type": "application/json", **self.authorization_header}

    def create(self, model_params):
        if model_params is None and not isinstance(model_params, dict):
            raise ValueError("json_data must be a dict")
        response = requests.post(
            f"{self.service_uri}",
            data=json.dumps(model_params),
            headers=self.headers,
        )
        return self._handle_response(response)

    def transition_model(self, model_name: str, version: str, stage: str):
        response = requests.get(
            f"{self.service_uri}/transition-model/{model_name}?version={version}&stage={stage}",
            headers=self.authorization_header,
        )
        return self._handle_response(response)

    def search(
        self, filter_string: str = "", max_results: int = 10, page_token: str = ""
    ):
        response = requests.get(
            f"{self.service_uri}/search?filter_string={filter_string}&max_results={max_results}&page_token={page_token}",
            headers=self.authorization_header,
        )
        return self._handle_response(response)


class RunsMLAPI(ServiceML):
    def __init__(self, service_uri, token):
        super().__init__(service_uri, token)
        self.service_uri = f"{self.service_uri}/runs"
        self.authotization_header = {"Authorization": f"Bearer {token}"}

    def create(self, run_params):
        response = requests.post(
            f"{self.service_uri}",
            json=run_params,
            headers={"Content-Type": "application/json", **self.authotization_header},
        )
        return self._handle_response(response)

    def upload_chunk(
        self,
        experiment_name: str,
        file_name: str,
        file_path: str,
        chunk: bytes,
        content_type: str,
    ):
        response = requests.post(
            f"{self.service_uri}/upload_chunk",
            data={"experiment_name": experiment_name, "file_name": file_name},
            files={file_name: (file_path, chunk, content_type)},
            headers=self.authotization_header,
        )
        if response.status_code != 200:
            return {"error": "Failed to upload chunk"}

    def search(
        self,
        filter_string: str = "",
        max_results: int = 10,
        page_token: str = "",
        experiment_name: str = "",
    ):
        response = requests.get(
            f"{self.service_uri}/{experiment_name}?filter_string={filter_string}&max_results={max_results}&page_token={page_token}",
            headers=self.authotization_header,
        )
        if response.status_code == 204:
            raise ValueError("Experiment not found")
        return self._handle_response(response)


class ProjectMLAPI:
    def __init__(self, service_uri, token):

        if not isinstance(service_uri, str):
            raise ValueError("service_uri must be a string")

        self.service_uri = f"{service_uri}/api"
        self.authorization_token = {"Authorization": f"Bearer {token}"}

    def create_project(self, project_name):
        body = {"project_name": project_name}
        return requests.post(
            f"{self.service_uri}/project",
            json=body,
            headers={"Content-Type": "application/json", **self.authorization_token},
        )

    def deploy_script(
        self, project_name: str, script_file_encode: str, requirements_file_enconde: str
    ):
        body = {
            "project_name": project_name,
            "requirements_content": requirements_file_enconde.decode("utf-8"),
            "run_script_content": script_file_encode.decode("utf-8"),
        }
        response = requests.post(
            f"{self.service_uri}/deploy",
            json=body,
            headers={"Content-Type": "application/json", **self.authorization_token},
        )

        return response.json()

    def get_pipeline_status(self, project_name: str):
        route = "deploy/{}".format(project_name)
        response = requests.get(
            f"{self.service_uri}/{route}", headers=self.authorization_token
        )

        return response.json()

    def create_cluster(self, project_name: str, cluster_size: int):
        body = {"project_name": project_name, "cluster_size": cluster_size}
        response = requests.post(
            f"{self.service_uri}/cluster",
            json=body,
            headers={"Content-Type": "application/json", **self.authorization_token},
        )

        return response.json()

    def run_pipeline(self, project_name: str):
        body = {"project_name": project_name}
        response = requests.post(
            f"{self.service_uri}/cluster/run",
            json=body,
            headers={"Content-Type": "application/json", **self.authorization_token},
        )

        return response.json()

    def remove_schedule(self, project_name: str):
        response = requests.delete(
            f"{self.service_uri}/cluster/schedule/{project_name}",
            headers=self.authorization_token,
        )

        return response.json()

    def create_schedule(self, project_name: str, schedule_interval: str):
        body = {"project_name": project_name, "schedule_interval": schedule_interval}
        response = requests.post(
            f"{self.service_uri}/cluster/schedule",
            json=body,
            headers={"Content-Type": "application/json", **self.authorization_token},
        )

        return response.json()


class ServiceAPIMLFacade:
    def __init__(self, service_uri, token):
        self.experiment_api = ExperimentMLAPI(service_uri, token)
        self.model_api = ModelMLAPI(service_uri, token)
        self.runs_api = RunsMLAPI(service_uri, token)
        self.project_api = ProjectMLAPI(service_uri, token)
