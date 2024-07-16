#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Yeedu hook.
This hook enable the submitting and running of jobs to the Yeedu platform. Internally the
operators talk to the ``/spark/job`
"""

import requests
import time
from typing import Optional, Dict
import os
from requests.exceptions import RequestException
from prefect.blocks.system import Secret
from prefect.blocks.system import JSON
from prefect import get_run_logger

session = requests.Session()

headers: dict = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}


class YeeduHook():
    """
    YeeduHook provides an interface to interact with the Yeedu API.

    :param token: Yeedu API token.
    :type token: str
    :param hostname: Yeedu API hostname.
    :type hostname: str
    :param workspace_id: The ID of the Yeedu workspace.
    :type workspace_id: int
    :param args: Additional positional arguments.
    :param kwargs: Additional keyword arguments.
    """

    def __init__(self, conf_id: int, tenant_id: str, base_url: str, workspace_id: int, connection_block_name: str,
                 password: str, token_block_name: str,*args, **kwargs) -> None:
        """
        Initializes YeeduHook with the necessary configurations to communicate with the Yeedu API.

        :param tenant_id: Yeedu API tenant_id.
        :param base_url: Yeedu API base_url.
        :param workspace_id: The ID of the Yeedu workspace.
        """

        super().__init__(*args, **kwargs)
        self.tenant_id: str = tenant_id
        self.conf_id = conf_id
        self.workspace_id = workspace_id
        self.connection_block_name = connection_block_name
        self.password = password
        self.base_url: str = base_url
        self.token_block_name = token_block_name
        self.username, self.YEEDU_VERIFY_SSL, self.YEEDU_SSL_CERT_FILE = self.get_connection_details()
        self.logger = get_run_logger()
        session.verify = self.check_ssl()
        self.useToken = False
        

    def get_connection_details(self):

        """
            Retrieves connection details from a specified connection name.

            Returns:
            - tuple: A tuple containing the username, SSL verification flag, and SSL certificate file path.

            Raises:
            - ValueError: If the username is not set in the connection details.
 """
        
        json_data = JSON.load(self.connection_block_name).value
        username = json_data.get("username")
        YEEDU_SSL_CERT_FILE = json_data.get("YEEDU_SSL_CERT_FILE")
        YEEDU_VERIFY_SSL = json_data.get("YEEDU_VERIFY_SSL")
        if not username:
            raise ValueError(f"Username is not set in the connection '{self.connection_block_name}'")
        return username, YEEDU_VERIFY_SSL, YEEDU_SSL_CERT_FILE

    def check_ssl(self):
        try:
            # if not provided set to true by default
            if self.YEEDU_VERIFY_SSL == 'true':

                # check for the ssl cert dir
                if not self.YEEDU_SSL_CERT_FILE:
                    self.logger.error(
                        f"Please provide YEEDU_SSL_CERT_FILE if YEEDU_VERIFY_SSL is set to: {self.YEEDU_VERIFY_SSL} (default: true)")
                    raise ValueError(
                        f"Please provide YEEDU_SSL_CERT_FILE if YEEDU_VERIFY_SSL is set to: {self.YEEDU_VERIFY_SSL} (default: true)")
                else:
                    # check if the file exists or not
                    if os.path.isfile(self.YEEDU_SSL_CERT_FILE):
                        return self.YEEDU_SSL_CERT_FILE
                    else:
                        self.logger.error(
                            f"Provided self.YEEDU_SSL_CERT_FILE: {self.YEEDU_SSL_CERT_FILE} doesnot exists")
                        raise ValueError(
                            f"Provided self.YEEDU_SSL_CERT_FILE: {self.YEEDU_SSL_CERT_FILE} doesnot exists")
            elif self.YEEDU_VERIFY_SSL == 'false':
                self.logger.info("YEEDU_VERIFY_SSL False")
                return False

            else:
                self.logger.error(
                    f"Provided YEEDU_VERIFY_SSL: {self.YEEDU_VERIFY_SSL} is neither true/false")
                raise ValueError(f"Provided YEEDU_VERIFY_SSL: {self.YEEDU_VERIFY_SSL} is neither true/false")

        except Exception as e:
            self.logger.error(f"Check SSL failed due to: {e}")
            raise ValueError(e)


    def _api_request(self, method: str, url: str, data=None, params: Optional[Dict] = None) -> requests.Response:
        """
        Makes an HTTP request to the Yeedu API with retries.

        :param method: The HTTP method (GET, POST, etc.).
        :param url: The URL of the API endpoint.
        :param data: The JSON data for the request.
        :param params: Optional dictionary of query parameters.
        :return: The API response.
        :raises Exception: If continuous request failures reach the threshold.
        """
        self.logger.info(f"Hitting Endpoint: {url}")
        if method == 'POST':
            response = session.post(url, headers=headers, json=data, params=params)
        else:
            response = session.get(url, headers=headers, json=data, params=params)
            # response = requests.request(method, url, headers=headers, json=data, params=params)
        return response  # Exit loop on successful response


    def check_token(self):
        if self.token_block_name is not None:
            self.useToken = True
            self.logger.info(f"useToken: {self.token_block_name}")
        else:
            self.useToken = False
            self.logger.info(f"useToken: {self.token_block_name}")


    def get_token(self):
        try:
            secret_block = Secret.load(self.token_block_name)
            token = secret_block.get()
            return token
        except Exception as e:
            self.logger.info(f"Please provide valid block name: {e}")
            raise ValueError(e)


    def yeedu_login(self):
        try:
            self.check_token()
            if self.useToken:
                self.logger.info("using token provided by user")
                token = self.get_token()
                headers['Authorization'] = f"Bearer {token}"
                self.associate_tenant()
            else:
                self.logger.info("generating token with the username and password provided by user")
                login_url = self.base_url + 'login'
                data = {
                    "username": f"{self.username}",
                    "password": f"{self.password}"
                }

                login_response = self._api_request('POST', login_url, data)

                if login_response.status_code == 200:
                    self.logger.info(
                        f'Login successful. Token: {login_response.json().get("token")}')
                    headers['Authorization'] = f"Bearer {login_response.json().get('token')}"
                    self.associate_tenant()
                    return login_response.json().get('token')
                else:
                    raise ValueError(login_response.text)
        except Exception as e:
            self.logger.info(f"An error occurred during yeedu_login: {e}")
            raise ValueError(e)

    def associate_tenant(self):
        try:
            # Construct the tenant URL
            tenant_url = self.base_url + f'user/select/{self.tenant_id}'

            # Make the POST request to associate the tenant
            tenant_associate_response = self._api_request('POST', tenant_url)

            if tenant_associate_response.status_code == 201:
                self.logger.info(
                    f'Tenant associated successfully. Status Code: {tenant_associate_response.status_code}')
                self.logger.info(
                    f'Tenant Association Response: {tenant_associate_response.json()}')
                return 0
            else:
                raise ValueError(tenant_associate_response.text)
        except Exception as e:
            self.logger.info(f"An error occurred during associate_tenant: {e}")
            raise ValueError(e)

    def yeedu_health_check(self) -> int:
        """
        Hitting Health Check API
        """
        health_check_url: str = self.base_url + f'healthCheck'
        return self._api_request('GET', health_check_url)
        
        
    def submit_job(self, job_conf_id: str) -> int:
        """
        Submits a job to Yeedu.

        :param job_conf_id: The job configuration ID.
        :return: The ID of the submitted job.
        """

        try:
            job_url: str = self.base_url + f'workspace/{self.workspace_id}/spark/job'
            data: dict = {'job_conf_id': job_conf_id}
            response = self._api_request('POST', job_url, data)
            api_status_code = response.status_code
            response_json = response.json()
            if api_status_code == 200:
                job_id = response.json().get('job_id')
                if job_id:
                    return job_id
                else:
                    raise ValueError(response_json)
            else:
                raise ValueError(response_json)

        except Exception as e:
            raise ValueError(e)

    def get_job_status(self, job_id: int) -> requests.Response:
        """
        Retrieves the status of a Yeedu job.

        :param job_id: The ID of the job.
        :return: The API response containing job status.
        """

        job_status_url: str = self.base_url + f'workspace/{self.workspace_id}/spark/job/{job_id}'
        return self._api_request('GET', job_status_url)

    def get_job_logs(self, job_id: int, log_type: str, restapi_port: int) -> str:
        """
        Retrieves logs for a Yeedu job.

        :param job_id: The ID of the job.
        :param log_type: The type of logs to retrieve ('stdout' or 'stderr').
        :return: The logs for the specified job and log type.
        """

        try:
            log_url: str = f'{self.base_url}tenant/{self.tenant_id}/workspace/{self.workspace_id}/spark/{job_id}/run-logs?log_type={log_type}'.replace(f':{restapi_port}/api/v1','')
            return log_url
        except Exception as e:
            raise ValueError(e)

    def kill_job(self, job_id: int):

        """
    Sends a request to stop a specific Spark job within a workspace.

    Args:
    - job_id (int): The ID of the job to be stopped.
    """
        try:
            job_kill_url = self.base_url + f'workspace/{self.workspace_id}/spark/job/kill/{job_id}'
            self.logger.info(f"Stopping job of Job Id {job_id}")
            response = self._api_request('POST',job_kill_url)
            if response.status_code == 201:
                self.logger.info("Stopped the Job")
        except Exception as e:
            raise ValueError(e)


    def wait_for_completion(self, job_id: int) -> str:
        """
        Waits for the completion of a Yeedu job and retrieves its final status.

        :param job_id: The ID of the job.
        :return: The final status of the job.
        :raises Exception: If continuous API failures reach the threshold.
        """

        try:
            max_attempts: int = 5
            attempts_failure: int = 0

            while True:
                time.sleep(5)
                # Check job status
                try:
                    response: requests.Response = self.get_job_status(job_id)
                    api_status_code: int = response.status_code
                    self.logger.info("Current API Status Code: %s", api_status_code)
                    if api_status_code == 200:
                        # If API status is a success, reset the failure attempts counter
                        attempts_failure = 0
                        job_status: str = response.json().get('job_status')
                        self.logger.info("Current Job Status: %s ", job_status)
                        if job_status in ['DONE', 'ERROR', 'TERMINATED', 'KILLED', 'STOPPED']:
                            self.logger.info("entered into if loop")
                            break
                    else:
                        raise ValueError(f"Failed to fetch job status, status_code: {api_status_code}")
                except (RequestException,ValueError) as e:
                    attempts_failure += 1
                    delay = 20
                    self.logger.info(
                        f"GET Job Status API request failed (attempt {attempts_failure}/{max_attempts}) due to {e}")
                    self.logger.info(f"Sleeping for {delay * attempts_failure} seconds before retrying...")
                    time.sleep(delay * attempts_failure)

                # If continuous failures reach the threshold, throw an error
                if attempts_failure == max_attempts:
                    raise ValueError("Continuous API failure reached the threshold")

            self.logger.info("returning job status")
            self.logger.info(job_status)
            return job_status

        except Exception as e:
            raise ValueError(e)

