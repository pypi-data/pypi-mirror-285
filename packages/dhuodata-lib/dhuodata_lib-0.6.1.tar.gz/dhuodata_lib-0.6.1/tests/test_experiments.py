import sys
import unittest
from unittest.mock import patch

sys.path.append("src")

from dhuolib.clients.experiment import DhuolibExperimentMLClient


class TestDhuolibPlatformClient(unittest.TestCase):
    def setUp(self):
        self.end_point = "http://localhost:8000"
        self.dhuolib = DhuolibExperimentMLClient(
            service_uri=self.end_point, token="123"
        )

    def test_0_invalid_run_params(self):
        response = self.dhuolib.create_experiment(experiment_name="teste1")
        self.assertEqual(list(response.keys()), ["error"])

    @patch("requests.post")
    def test_1_create_experiment_with_valid_params(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 201
        mock_response.json.return_value = {"experiment_id": "1"}

        response = self.dhuolib.create_experiment(
            experiment_name="teste1",
            experiment_tags={"version": "v1", "priority": "P1"},
        )
        self.assertEqual(response, mock_response.json.return_value)

    @patch("requests.post")
    def test_3_predict_online_with_valid_dataset(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "model_name": "nlp_framework",
            "predictions": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        }

        run_params = {
            "stage": "Production",
            "data": "tests/files/data_predict.csv",
            "modelname": "nlp_framework",
        }

        response = self.dhuolib.predict_online(run_params)

        self.assertEqual(response, mock_response.json.return_value)
