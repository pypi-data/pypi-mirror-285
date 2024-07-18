import sys
import unittest
from unittest.mock import mock_open, patch

sys.path.append("src")

from dhuolib.clients.experiment import DhuolibExperimentMLClient


class TestDhuolibPlatformClient(unittest.TestCase):
    def setUp(self):
        self.end_point = "http://localhost:8000"
        self.dhuolib = DhuolibExperimentMLClient(
            service_uri=self.end_point, token="123"
        )

    @patch("requests.post")
    def test_1_run_experiment_with_valid_params(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "experiment_name": "experiment_name",
            "run_id": "run_id",
            "model_uri": "model_uri",
        }

        response = self.dhuolib.execute_run_for_experiment(
            type_model="teste1",
            experiment_name="2",
            tags={"version": "v1", "priority": "P1"},
            modelpkl_path="tests/files/LogisticRegression_best.pickle",
            requirements_path="tests/files/requirements.txt",
        )

        self.assertEqual(response, mock_response.json.return_value)
