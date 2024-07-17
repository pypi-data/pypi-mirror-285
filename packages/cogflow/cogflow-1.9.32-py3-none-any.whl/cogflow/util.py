"""
    Utility functions
"""

import re
from datetime import datetime

import requests


def make_post_request(url, data=None, params=None, files=None):
    """
        utility function to make POST requests
    :param url: url of the API endpoint
    :param data: JSON payload
    :param params: request params
    :param files : file
    :return: response for the POST request in json format
    """
    try:
        if data:
            response = requests.post(url, json=data, params=params)
        elif files:
            with open(files, "rb") as file_data:
                file = {"file": file_data}
                response = requests.post(url, params=params, files=file)
                file_data.close()
        else:
            response = requests.post(url, params=params)

        if response.status_code == 201:
            print("POST request successful")
            return response.json()
        # if not the success response
        print(f"POST request failed with status code {response.status_code}")
        raise Exception("request failed")
    except requests.exceptions.RequestException as exp:
        print(f"Error making POST request: {exp}")
        raise Exception(f"Error making POST request: {exp}")


def custom_serializer(obj):
    """
        method to serializer obj to datetime isoformat
    :param obj:
    :return:
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def is_valid_s3_uri(uri):
    """
        method to check if the url is valid S3 url
    :param uri: url to check
    :return:
    """
    # Regular expression for S3 URI
    s3_uri_regex = re.compile(r"^s3://([a-z0-9.-]+)/(.*)$")

    # Check against the regex pattern
    match = s3_uri_regex.match(uri)

    if match:
        bucket_name = match.group(1)
        object_key = match.group(2)

        # Additional checks for bucket name and object key can be added here
        if bucket_name and object_key:
            return True

    return False


def make_delete_request(url, path_params=None, query_params=None):
    """
     utility function to make DELETE requests
    :url: url of the API endpoint
    :path_params: path params
    :query_params: query params
    :return: response for the POST request in json format
    """
    try:
        if query_params:
            response = requests.delete(url, params=query_params)
        else:
            # Make the DELETE request with query parameters
            response = requests.delete(url + "/" + path_params)
        if response.status_code == 200:
            print("DELETE request successful")
            return response.json()
        # if not the success response
        print(f"DELETE request failed with status code {response.status_code}")
        raise Exception("request failed")
    except requests.exceptions.RequestException as exp:
        print(f"Error making POST request: {exp}")
        raise Exception(f"Error making POST request: {exp}")


def make_get_request(url, path_params=None, query_params=None):
    """
     utility function to make GET requests
    :url: url of the API endpoint
    :path_params: path params
    :query_params: query params
    :return: response for the GET request in json format
    """

    try:
        if query_params:
            response = requests.get(url, params=query_params)
        else:
            # Make the GET request with query parameters
            response = requests.get(url + "/" + path_params)
        if response.status_code == 200:
            print("GET request successful")
            return response.json()
        # if not the success response
        print(f"GET request failed with status code {response.status_code}")
        raise Exception("request failed")
    except requests.exceptions.RequestException as exp:
        print(f"Error making GET request: {exp}")
        raise Exception(f"Error making GET request: {exp}")
