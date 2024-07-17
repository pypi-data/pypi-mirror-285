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

import json
import logging

from screwdriver_cd_python_sdk.events import start_build
from screwdriver_cd_python_sdk.pipeline import (create_pipeline,
                                                search_pipelines_by_name)
from screwdriver_cd_python_sdk.secrets import create_or_update_secret


def initialize(pipelines_config_path: str, screwdriver_api_url: str, token: str) -> None:
    """
    Given a JSON file containing Screwdriver pipeline definitions, this method initializes all pipelines on a running
    Screwdriver instance.

    The basics works like this

    .. highlight:: json
    .. code-block:: json

        [
            {
                "git": "git@github.com:QubitPi/hashicorp-aws.git"
            },
            {
                "git": "git@github.com:QubitPi/docker-kong.git"
            },
        ]

    We also support loading AWS secrets into Screwdriver instances. To do that, download the IAM credentials CSV file
    and specify the absolute path of that file by

    .. highlight:: json
    .. code-block:: json

        [
            {
                "git": "git@github.com:QubitPi/docker-kong.git",
                "awsCredentialFile": "abs-path-to/aws_accessKeys.csv",
            }
        ]

    In addition, one can also preload
    `Screwdriver Secrets <https://screwdriver-docs.qubitpi.org/user-guide/configuration/secrets>`_ with, for example

    .. highlight:: json
    .. code-block:: json

        [
            {
                "git": "git@github.com:QubitPi/docker-kong.git",
                "secrets": [
                    {
                        "name": "MY_CREDENTIAL_FILE",
                        "type": "file",
                        "value": "/home/root/credential.json"
                    },
                    {
                        "name": "MY_PASSWORD",
                        "type": "value",
                        "value": "23efdsf324gfdg"
                    }
                ],
            }
        ]

    Note that both value and file based secrets are supported as shown in the example above

    We can now iterate each pipeline and initialize them using the script below

    .. code-block:: console

        pip3 install screwdriver-cd-python-sdk

    .. highlight:: python
    .. code-block:: python

        import argparse
        from screwdriver_cd_python_sdk.screwdriver_initializer import initialize

        if __name__ == "__main__":
            parser = argparse.ArgumentParser(description='Initiate all pipelines of Screwdriver CD')
            parser.add_argument(
                '-t',
                '--token',
                help='Screwdriver API Token - https://screwdriver-docs.qubitpi.org/user-guide/api',
                required=True
            )
            args = vars(parser.parse_args())
            token = args['token']

            initialize(
                pipelines_config_path="pipelines.json",
                screwdriver_api_url="https://screwdriver-api.mycompany.com",
                token=token
            )

    :param pipelines_config_path:  The absolute JSON file containing Screwdriver pipeline definitions
    :param screwdriver_api_url:  The Screwdriver API URL. For example, "screwdriver-api.mycompany.com". See
                                 https://screwdriver-docs.qubitpi.org/user-guide/api for more information.
    :param token:  `The Screwdriver API Token <https://screwdriver-docs.qubitpi.org/user-guide/tokens.html>`_
    """
    with open(pipelines_config_path, 'r') as file:
        pipelines = json.load(file)

    for pipeline in pipelines:

        git_url = pipeline["git"]
        repo_name = git_url[git_url.find(":") + 1:git_url.find(".git")]

        pipeline_id = None
        for match in search_pipelines_by_name(name=repo_name, screwdriver_api_url=screwdriver_api_url, token=token):
            if match["name"] == repo_name:
                pipeline_id = match["id"]
                logging.debug("{} is already created.".format(repo_name))

                break

        if pipeline_id is None:
            logging.debug("Creating {}...".format(repo_name))
            pipeline_id = create_pipeline(
                checkout_url=pipeline["git"],
                screwdriver_api_url=screwdriver_api_url,
                token=token
            )["id"]

        if pipeline["secrets"]:
            for secret in pipeline["secrets"]:
                if secret["type"] == "value":
                    create_or_update_secret(
                        secret_name=secret["name"],
                        secret_value=secret["value"],
                        pipeline_id=pipeline_id,
                        screwdriver_api_url=screwdriver_api_url,
                        token=token
                    )
                else:
                    create_or_update_secret(
                        secret_name=secret["name"],
                        secret_value=_file_content(secret["value"]),
                        pipeline_id=pipeline_id,
                        screwdriver_api_url=screwdriver_api_url,
                        token=token
                    )

        if pipeline["runOnCreate"]:
            start_build(pipeline_id=pipeline_id, screwdriver_api_url=screwdriver_api_url, token=token)


def _file_content(file_path: str) -> str:
    with open(file_path, 'r') as file:
        return file.read().rstrip('\n')  # https://stackoverflow.com/a/70233945
