# Copyright Jiaqi Liu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import sys

import requests

logging.basicConfig(level=logging.DEBUG)


def _headers(token: str) -> object:
    return {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json',
    }


def create_or_update_secret(
        secret_name: str,
        secret_value: str,
        pipeline_id: int,
        screwdriver_api_url: str,
        token: str
) -> None:
    """
    Create or update a secret of a Screwdriver pipeline.

    Example usage:

    .. code-block:: console

        pip3 install screwdriver-cd-python-sdk

    .. highlight:: python
    .. code-block:: python

        import argparse
        import requests

        from screwdriver_cd_python_sdk.secrets import create_or_update_secret

        SCREWDRIVER_API_SERVER_URL = "screwdriver-api.mycompany.com"
        SCREWDRIVER_API_TOKEN      = requests.get(
            "{url}/v4/auth/token".format(url=SCREWDRIVER_API_SERVER_URL)
        ).json()["token"]


        def __loadFromFileByPath(filePath) -> str:
            with open(filePath, 'r') as file:
                return file.read().rstrip()


        def __load_all_secrets() -> list[dict]:
            return [
                {
                    "pipeline": "QubitPi/my-github-repo",
                    "pipelineId": 77,
                    "secretName": "MY_SCREWDRIVER_SECRET_1",
                    "secreteValue": __loadFromFileByPath("/abs/or/relative/path/to/MY_SCREWDRIVER_SECRET_1"),
                    "screwdriverApiUrl": SCREWDRIVER_API_SERVER_URL,
                    "token": SCREWDRIVER_API_TOKEN
                },
                {
                    "pipeline": "QubitPi/my-github-repo",
                    "pipelineId": 77,
                    "secretName": "MY_SCREWDRIVER_SECRET_2",
                    "secreteValue": __loadFromFileByPath("/abs/or/relative/path/to/MY_SCREWDRIVER_SECRET_2"),
                    "screwdriverApiUrl": SCREWDRIVER_API_SERVER_URL,
                    "token": SCREWDRIVER_API_TOKEN
                },
            ]

        if __name__ == "__main__":
            parser = argparse.ArgumentParser(description='UPSERT a single Screwdriver Secret')
            parser.add_argument('-n', '--name', help='The Screwdriver secret name', required=True)
            parser.add_argument('-v', '--value', help='The Screwdriver secret value', required=True)
            parser.add_argument(
                '-i',
                '--id',
                help='The ID of the Screwdriver pipeline that receives the secret',
                required=True
            )
            parser.add_argument(
                '-u',
                '--url',
                help='The URL of the Screwdriver API server. For example: "screwdriver-api.mycompany.com"',
                required=True
            )
            parser.add_argument(
                '-t',
                '--token',
                help='The Screwdriver API token obtained via "https://screwdriver-api.mycompany.com/v4/auth/token"',
                required=True
            )
            args = vars(parser.parse_args())

            create_or_update_secret(
                secret_name=args["name"],
                secret_value=args["value"],
                pipeline_id=args["id"],
                screwdriver_api_url=args["url"],
                token=args["token"]
            )


    "allowInPR" is set to be false by default

    :param secret_name:
    :param secret_value:
    :param pipeline_id:
    :param token:
    """

    response = requests.get(
        "{}/v4/pipelines/{}/secrets".format(screwdriver_api_url, pipeline_id),
        headers={
            'accept': 'application/json',
            'Authorization': token,
        }
    )
    if secret_name in str(response.content):
        logging.debug("Updating secret '{}'".format(secret_name))

        for secrete in response.json():
            if secrete["name"] == secret_name:
                json_data = {
                    'value': secret_value,
                    'allowInPR': False,
                }

                if requests.put(
                        '{}/v4/secrets/{}'.format(screwdriver_api_url, secrete["id"]),
                        headers=_headers(token),
                        json=json_data
                ).status_code != 200:
                    sys.exit(os.EX_CONFIG)
    else:
        logging.debug("Creating secret '{}'".format(secret_name))

        json_data = {
            'pipelineId': pipeline_id,
            'name': secret_name,
            'value': secret_value,
            'allowInPR': False,
        }

        if requests.post(
                '{}/v4/secrets'.format(screwdriver_api_url), headers=_headers(token), json=json_data
        ).status_code != 201:
            sys.exit(os.EX_CONFIG)
