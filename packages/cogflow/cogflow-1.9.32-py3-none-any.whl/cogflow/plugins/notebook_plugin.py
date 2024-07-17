"""
This module provides functionality related to Model actions via plugin.
"""

import json
import os

from .mlflowplugin import MlflowPlugin
from .. import plugin_config
from ..pluginmanager import PluginManager
from ..util import custom_serializer
from ..util import make_post_request, make_delete_request, make_get_request
from .kubeflowplugin import KubeflowPlugin


class NotebookPlugin:
    """
    Class for defining reusable components.
    """

    def __init__(self):
        """
        Initializes the ModelPlugin class.
        """
        self.section = "notebook_plugin"

    @staticmethod
    def link_model_to_dataset(dataset_id, model_id):
        """
        Links a model to a dataset using the provided API endpoint.

        This method sends a POST request to the API to associate a specified model
        with a given dataset. It uses the user's ID defined in the plugin configuration.

        Args:
            dataset_id (str): The ID of the dataset to link to the model.
            model_id (str): The ID of the model to be linked to the dataset.

        Returns:
            Response: The response object from the API call.

        Raises:
            requests.exceptions.RequestException: An error occurred when making the POST request.
        """
        # Verify plugin activation
        PluginManager().verify_activation(NotebookPlugin().section)

        data = {
            "user_id": plugin_config.JUPYTER_USER_ID,
            "model_id": model_id,
            "dataset_id": dataset_id,
        }
        # call the api
        url = os.getenv(plugin_config.API_BASEPATH) + "/link_dataset_model"
        return make_post_request(url, data=data)

    def save_model_details_to_db(self, registered_model_name):
        """
        store model details in database
        :param registered_model_name: name of the registered model
        :return: id of model
        """
        # Verify plugin activation
        PluginManager().verify_activation(NotebookPlugin().section)

        data = {
            "name": registered_model_name,
            "version": self.get_model_latest_version(registered_model_name),
            "type": "sklearn",
            "user_id": plugin_config.JUPYTER_USER_ID,
        }

        # call the api to register model
        url = os.getenv(plugin_config.API_BASEPATH) + "/models"
        return make_post_request(url, data=data)

    @staticmethod
    def get_model_latest_version(registered_model_name: str):
        """
        return the latest version of registered model
        :param registered_model_name: model name to get the versions
        :return: latest version
        """
        # Verify plugin activation
        PluginManager().verify_activation(NotebookPlugin().section)

        latest_version_info = MlflowPlugin().search_model_versions(
            filter_string=f"name='{registered_model_name}'"
        )
        sorted_model_versions = sorted(
            latest_version_info, key=lambda x: x.version, reverse=True
        )

        if sorted_model_versions:
            latest_version = sorted_model_versions[0]
            print("Latest Version:", latest_version.version)
            print("Status:", latest_version.status)
            print("Stage:", latest_version.current_stage)
            print("Description:", latest_version.description)
            print("Last Updated:", latest_version.last_updated_timestamp)
            return latest_version.version

        print(f"No model versions found for {registered_model_name}")
        return 1

    @staticmethod
    def save_model_uri_to_db(model_id, model_uri):
        """
            method to call the api to save model uri
        :param model_id: model id of the model
        :param model_uri: model uri
        :return: API response
        """
        # Verify plugin activation
        PluginManager().verify_activation(NotebookPlugin().section)

        # call the api for saving model_uri
        data = {
            "user_id": plugin_config.JUPYTER_USER_ID,
            "model_id": model_id,
            "uri": model_uri,
            "description": f"model uri of model id :{model_id}",
        }
        url = os.getenv(plugin_config.API_BASEPATH) + "/models/uri"
        return make_post_request(url, data=data)

    @staticmethod
    def delete_pipeline_details_from_db(pipeline_id):
        """
        delete the pipeline details
        :param pipeline_id: pipeline id
        :return:
        """

        url = os.getenv(plugin_config.API_BASEPATH) + "/pipeline"
        return make_delete_request(url=url, path_params=pipeline_id)

    @staticmethod
    def list_runs_by_pipeline_id(pipeline_id):
        """
        list the pipeline run details
        :param pipeline_id: pipeline_id
        :return: list of run details
        """
        url = os.getenv(plugin_config.API_BASEPATH) + "/pipeline/runs"
        return make_get_request(url=url, path_params=pipeline_id)

    @staticmethod
    def delete_run_details_from_db(pipeline_id):
        """
         delete the pipeline details
        :param pipeline_id: pipeline_id
        :return: successful deletion message or 404 error
        """
        url = os.getenv(plugin_config.API_BASEPATH) + "/pipeline/runs"
        return make_delete_request(url=url, path_params=pipeline_id)

    @staticmethod
    def get_pipeline_id_by_name(pipeline_name):
        """
        Retrieves the pipeline ID for a given pipeline name.

        Args:
            pipeline_name (str): The name of the pipeline to fetch the ID for.

        Returns:
            str: The ID of the specified pipeline if found.

        Raises:
            ValueError: If no pipeline with the given name is found.

        Example:
            pipeline_id = NotebookPlugin.get_pipeline_id_by_name("Example Pipeline")
        """
        kfp = KubeflowPlugin()
        pipelines_response = kfp.client().list_pipelines()
        pipeline_id = None
        if pipelines_response.pipelines:
            for pipeline in pipelines_response.pipelines:
                if pipeline.name == pipeline_name:
                    pipeline_id = pipeline.id
                    return pipeline_id

        if not pipeline_id:
            print(f"No pipeline found with the name '{pipeline_name}'")

    @staticmethod
    def list_pipelines_by_name(pipeline_name):
        """
        Lists all versions and runs of the specified pipeline by name.

        Args:
            pipeline_name (str): The name of the pipeline to fetch details for.

        Returns:
            dict: A dictionary containing the pipeline ID, versions,
             and runs of the specified pipeline.

        Raises:
            ValueError: If the pipeline name is invalid or not found.
            Exception: For any other issues encountered during the fetch operations.
        """
        # Fetch all versions of the specified pipeline
        kfp = KubeflowPlugin()

        pipeline_id = NotebookPlugin.get_pipeline_id_by_name(pipeline_name)
        versions_response = kfp.list_pipeline_versions(pipeline_id=pipeline_id)
        run_list = NotebookPlugin.list_runs_by_pipeline_id(pipeline_id=pipeline_id)
        result_dict = {
            "pipeline_id": pipeline_id,
            "versions": versions_response.versions,
            "runs": run_list,
        }
        return result_dict

    @staticmethod
    def save_pipeline_details_to_db(details):
        """
            save the details related to pipeline to the database
        :param details: dictionary with all the details of pipeline,run_details,task_details,experiments
        :return:
        """
        data = json.dumps(details, default=custom_serializer, indent=4)
        url = os.getenv(plugin_config.API_BASEPATH) + "/pipeline/add"
        make_post_request(url=url, data=data)
