#!/usr/bin/python3
import logging
import os
from pathlib import Path

import requests

from deserializers import deserialize_file

S3_ENDPOINT = 'https://lnti-bigbeans-problems-dataset-public.s3.dualstack.us-east-2.amazonaws.com'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_dest_file(problem_name, file_name, data_home=None) -> str:
    if data_home is None:
        data_home = str(Path.home()) + '/.bigbeans'
    return data_home + '/' + problem_name + '/' + file_name


def _fetch_s3_file(problem_name, file_name, data_home=None):
    object_key = problem_name + '/' + file_name
    local_file = get_dest_file(problem_name, file_name, data_home)
    logger.debug(f"Downloading {object_key} to {local_file}")
    # make sure the directory exists
    local_dir = local_file[:local_file.rfind('/')]
    os.makedirs(local_dir, exist_ok=True)
    response = requests.get(S3_ENDPOINT + '/' + object_key, stream=True)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        with open(local_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        response.raise_for_status()
    return local_file


def fetch(problem_name, data_home=None):
    metadata_file = _fetch_s3_file(problem_name, 'data.json', data_home)
    data_file = _fetch_s3_file(problem_name, 'data.bin', data_home)
    return deserialize_file(data_file, metadata_file)
