from unittest.mock import patch
from dhuolib.clients.platform import DhuolibPlatformClient
import unittest
import sys

sys.path.append("src")


class TestDhuolibPlatform(unittest.TestCase):
    def setUp(self):
        self.endpoint = "http://localhost:8000"
        self.dhuolib = DhuolibPlatformClient(
            service_uri=self.endpoint, project_name="test-6", token="123"
        )

    @patch("requests.post")
    def test_0_create_batch_project_successful(self, mock_post):
        project_name = "teste-project"
        mock_response = mock_post.return_value
        mock_response.status_code = 201
        mock_response.json.return_value = {"status": "success", "project_id": 123}
        response = self.dhuolib.create_batch_project(project_name)
        self.assertEqual(response, {"status": "success", "project_id": 123})

    def test_1_create_batch_project_raises_exception_on_none(self):
        with self.assertRaises(ValueError) as context:
            self.dhuolib.create_batch_project(None)
            self.assertIn("project_name is required", str(context.exception))

    def test_2_deploy_batch_project_no_project_name(self):
        self.dhuolib = DhuolibPlatformClient(service_uri=self.endpoint, token="123")
        with self.assertRaises(ValueError) as context:
            self.dhuolib.deploy_batch_project(
                script_filename="script.py", requirements_filename="requirements.txt"
            )
            self.assertIn("Batch project is required", str(context.exception))

    def test_3_deploy_batch_project_missing_files(self):
        with self.assertRaises(ValueError) as context:
            self.dhuolib.deploy_batch_project(None, None)
            self.assertIn(
                "script_filename and requirements_filename are required",
                str(context.exception),
            )

    def test_4_deploy_batch_project_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            response = self.dhuolib.deploy_batch_project(
                "script.py", "requirements.txt"
            )
            self.assertEqual(response, {"error": "File not found"})

    def test_5_schedule_batch_run_no_project_name(self):
        self.dhuolib = DhuolibPlatformClient(service_uri=self.endpoint, token="123")
        with self.assertRaises(ValueError) as context:
            self.dhuolib.schedule_batch_run(None, "1h")
            self.assertIn("Batch project is required", str(context.exception))

    def test_6_remove_schedule_no_project_name(self):
        self.dhuolib = DhuolibPlatformClient(service_uri=self.endpoint, token="123")
        with self.assertRaises(ValueError) as context:
            self.dhuolib.remove_schedule(None)
            self.assertIn("Batch project is required", str(context.exception))
