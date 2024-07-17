import base64
import time

from dhuolib.config import logger
from dhuolib.services import ServiceAPIMLFacade
from dhuolib.utils import validate_name


class DhuolibPlatformClient:
    def __init__(self, service_uri=None, project_name=None, token=None):
        if not service_uri:
            raise ValueError("service_uri is required")
        if not token:
            raise ValueError("token is required")

        self.service = ServiceAPIMLFacade(service_uri, token=token)
        self.project_name = project_name

    def create_batch_project(self, project_name: str):
        self.project_name = validate_name(project_name)
        response = self.service.project_api.create_project(project_name)
        if response.status_code == 400:
            raise ValueError("Project already exists")
        elif response.status_code == 404:
            return ConnectionError("Connection error")

        return response.json()

    def deploy_batch_project(self, script_filename: str, requirements_filename: str):
        if not self.project_name:
            raise ValueError("Batch project is required")

        if not (script_filename or requirements_filename):
            raise ValueError("script_filename and requirements_filename are required")

        try:
            with open(script_filename, "rb") as script_file, open(
                requirements_filename, "rb"
            ) as requirements_file:
                encoded_script = base64.b64encode(script_file.read())
                encoded_requirements = base64.b64encode(requirements_file.read())
                response = self.service.project_api.deploy_script(
                    project_name=self.project_name,
                    script_file_encode=encoded_script,
                    requirements_file_enconde=encoded_requirements,
                )
                return response
        except FileNotFoundError as e:
            logger.error(f"Error: {e}")
            return {"error": str(e)}

    def pipeline_status_report(self):
        lst = []
        if not self.project_name:
            raise ValueError("Batch project is required")
        response = self.service.project_api.get_pipeline_status(self.project_name)
        for data in response["data"]:
            lst.append(
                {
                    "date_log": data["date_log"],
                    "step": data["step"],
                    "status": data["status"],
                }
            )
        return lst

    def create_cluster(self, cluster_size: int):
        if not self.project_name:
            raise ValueError("Batch project is required")

        if cluster_size not in [1, 2, 3]:
            raise ValueError("cluster_size must be 1, 2 or 3")

        response = self.service.project_api.create_cluster(
            self.project_name, cluster_size
        )
        return response

    def batch_run(self):
        if not self.project_name:
            raise ValueError("Batch project is required")

        response = self.service.project_api.run_pipeline(self.project_name)
        return response

    def schedule_batch_run(self, project_name: str, schedule_interval: str):
        if not project_name:
            raise ValueError("Batch project is required")

        response = self.service.project_api.create_schedule(
            project_name, schedule_interval
        )
        return response

    def remove_schedule(self, project_name: str):
        if not project_name:
            raise ValueError("Batch project is required")

        response = self.service.project_api.remove_schedule(project_name)
        return response
