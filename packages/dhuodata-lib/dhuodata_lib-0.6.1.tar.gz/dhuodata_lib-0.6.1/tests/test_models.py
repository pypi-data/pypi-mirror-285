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

    @patch("requests.post")
    def test_1_create_model_with_valid_params(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "current_stage": "Production",
            "last_updated_timestamp": 1713582060414,
            "model_version": "1",
            "run_id": "9434e517ed104958b6f5f47d33c79184",
            "status": "READY",
        }

        response = self.dhuolib.create_model(
            modelname="nlp_framework",
            stage="Production",
            run_id="9434e517ed104958b6f5f47d33c79184",
            model_uri="model_uri",
            tags={"version": "v1", "priority": "P1"},
        )

        self.assertEqual(response, mock_response.json.return_value)

    @patch("requests.get")
    def test_2_transition_model_with_valid_params(self, mock_get):
        model_name = "nlp_framework"
        version = "117"
        stage = "Production"
        expected_response = {
            "current_stage": "Production",
            "last_updated_timestamp": 1713582060414,
            "model_version": "1",
            "run_id": "9434e517ed104958b6f5f47d33c79184",
            "status": "READY",
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = expected_response

        response = self.dhuolib.transition_model(model_name, version, stage)
        self.assertEqual(response, expected_response)

    def test_3_transition_model_with_invalid_params(self):
        with self.assertRaises(TypeError):
            self.dhuolib.transition_model(model_name="nlp_framework")
        with self.assertRaises(TypeError):
            self.dhuolib.transition_model(stage="Production")
        with self.assertRaises(TypeError):
            self.dhuolib.transition_model(version="117")
