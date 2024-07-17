import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from cogflow.cogflow import (
    link_model_to_dataset,
    save_dataset_details,
    save_model_details_to_db,
)
from ..cogflow.plugins.dataset_plugin import DatasetMetadata, DatasetPlugin
from ..cogflow.plugins.notebook_plugin import NotebookPlugin


class TestNotebookPlugin(unittest.TestCase):
    @patch(
        "cogflow.cogflow.plugins.notebook_plugin.NotebookPlugin.get_model_latest_version"
    )
    @patch("os.getenv")
    def test_save_model_details_to_db(self, mock_env, mock_model_version):
        with patch("requests.post") as mock_requests_post:
            mock_env.side_effect = lambda x: {
                "MLFLOW_S3_ENDPOINT_URL": "localhost:9000",
                "AWS_ACCESS_KEY_ID": "minio",
                "AWS_SECRET_ACCESS_KEY": "minio123",
                "API_BASEPATH": "http://randomn",
            }[x]
            mock_model_version.return_value = 1

            mock_response = {
                "data": {
                    "id": 101,
                    "last_modified_time": "2024-05-16T12:33:08.890033",
                    "last_modified_user_id": 0,
                    "name": "testmodel",
                    "register_date": "2024-05-16T12:33:08.890007",
                    "register_user_id": 0,
                    "type": "sklearn",
                    "version": "1",
                },
                "errors": "None",
                "message": "Created new model.",
                "success": "True",
            }
            mock_requests_post.return_value.status_code = 201
            mock_requests_post.return_value.json.return_value = mock_response
            result = save_model_details_to_db("testmodel")
            self.assertEqual(result["data"]["id"], 101)

    @patch("os.getenv")
    def test_save_dataset_details(self, mock_env):
        with patch("requests.post") as mock_requests_post:
            mock_env.side_effect = lambda x: {
                "MLFLOW_S3_ENDPOINT_URL": "localhost:9000",
                "AWS_ACCESS_KEY_ID": "minio",
                "AWS_SECRET_ACCESS_KEY": "minio123",
                "API_BASEPATH": "http://randomn",
            }[x]

            mock_response = {
                "data": {
                    "dataset_id": 8,
                    "file_name": "breastcancerwisconsindiagnostic.zip",
                    "file_path": "mlflow",
                    "register_date": "2024-05-16T13:03:05.442386",
                    "user_id": 0,
                },
                "errors": "None",
                "message": "File uploaded successfully.",
                "success": "True",
            }
            mock_requests_post.return_value.status_code = 201
            mock_requests_post.return_value.json.return_value = mock_response
            # Dataset details
            source = (
                "https://archive.ics.uci.edu/static/public/17"
                "/breast+cancer+wisconsin+diagnostic.zip"
            )
            format = "zip"
            name = "breast+cancer+wisconsin+diagnostic.zip"
            description = "Breast cancer wisconsin diagnotic dataset"

            dm = DatasetMetadata(name, description, source, format)
            result = save_dataset_details(dataset=dm)
            self.assertEqual(result, mock_response["data"]["dataset_id"])

    @patch("os.getenv")
    def test_link_model_to_dataset(self, mock_env):
        with patch("requests.post") as mock_requests_post:
            mock_env.side_effect = lambda x: {
                "MLFLOW_S3_ENDPOINT_URL": "localhost:9000",
                "AWS_ACCESS_KEY_ID": "minio",
                "AWS_SECRET_ACCESS_KEY": "minio123",
                "API_BASEPATH": "http://randomn",
            }[x]

            mock_response = {
                "data": {
                    "dataset_id": 2,
                    "linked_time": "2024-05-16 15:23:24",
                    "model_id": 1,
                    "user_id": 0,
                },
                "errors": "None",
                "message": "Dataset linked with model successfully",
                "success": "True",
            }
            mock_requests_post.return_value.status_code = 201
            mock_requests_post.return_value.json.return_value = mock_response
            f = StringIO()
            with redirect_stdout(f):
                link_model_to_dataset(2, 1)
            out = f.getvalue().strip()
            assert out == "POST request successful"

    @patch("os.getenv")
    def test_delete_pipeline_details_from_db(self, mock_env):
        with patch("requests.delete") as mock_requests_delete:
            mock_env.side_effect = lambda x: {
                "MLFLOW_S3_ENDPOINT_URL": "localhost:9000",
                "AWS_ACCESS_KEY_ID": "minio",
                "AWS_SECRET_ACCESS_KEY": "minio123",
                "API_BASEPATH": "http://randomn",
            }[x]

            mock_response = {
                "errors": "None",
                "message": "Pipeline Details Deleted successfully",
                "success": "True",
            }
            mock_requests_delete.return_value.status_code = 200
            mock_requests_delete.return_value.json.return_value = mock_response
            f = StringIO()
            with redirect_stdout(f):
                NotebookPlugin().delete_pipeline_details_from_db("2")
            out = f.getvalue().strip()
            assert out == "DELETE request successful"

    @patch("os.getenv")
    def test_delete_run_details_from_db(self, mock_env):
        with patch("requests.delete") as mock_requests_delete:
            mock_env.side_effect = lambda x: {
                "MLFLOW_S3_ENDPOINT_URL": "localhost:9000",
                "AWS_ACCESS_KEY_ID": "minio",
                "AWS_SECRET_ACCESS_KEY": "minio123",
                "API_BASEPATH": "http://randomn",
            }[x]

            mock_response = {
                "errors": "None",
                "message": "Runs deleted successfully",
                "success": "True",
            }
            mock_requests_delete.return_value.status_code = 200
            mock_requests_delete.return_value.json.return_value = mock_response
            f = StringIO()
            with redirect_stdout(f):
                NotebookPlugin().delete_run_details_from_db("2")
            out = f.getvalue().strip()
            assert out == "DELETE request successful"

    @patch("os.getenv")
    def test_list_runs_by_pipeline_id(self, mock_env):
        with patch("requests.get") as mock_requests_get:
            mock_env.side_effect = lambda x: {
                "MLFLOW_S3_ENDPOINT_URL": "localhost:9000",
                "AWS_ACCESS_KEY_ID": "minio",
                "AWS_SECRET_ACCESS_KEY": "minio123",
                "API_BASEPATH": "http://randomn",
            }[x]

            # Define mock response
            mock_response = {
                "runs": [
                    {"run_id": "0d3ffa58-7d15-4456-a1f6-2c1355f95d22"},
                    {"run_id": "0d3ffa58-7d15-4456-a1f6-2c1355f95d23"},
                ]
            }

            mock_requests_get.return_value.status_code = 200
            mock_requests_get.return_value.json.return_value = mock_response
            f = StringIO()
            with redirect_stdout(f):
                NotebookPlugin().list_runs_by_pipeline_id("2")
            out = f.getvalue().strip()
            assert out == "GET request successful"


if __name__ == "__main__":
    unittest.main()
