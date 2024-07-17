import unittest
import sys

sys.path.append("src")

import dhuolib.utils as utils


class TestDhuolibUtils(unittest.TestCase):
    def test_0_transform_name_project_no_project_name(self):
        with self.assertRaises(ValueError):
            project_name = utils.validate_name(None)
            self.assertIsNone(project_name)

    def test_1_project_name_min_length(self):
        with self.assertRaises(ValueError) as context:
            utils.validate_name("abc")
            self.assertTrue(
                "project_name must have at least 4 characters" in str(context.exception)
            )

    def test_2_transform_name_project(self):
        with self.assertRaises(ValueError):
            utils.validate_name("Projeto Analise Sentimento")

    def test_3_transform_name_project(self):
        project_name = utils.validate_name("Projeto_Analise_Sentimento")
        self.assertEqual(project_name, "projeto_analise_sentimento")
