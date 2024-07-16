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

"""This module contains Yeedu Operator."""
from typing import Optional, Tuple, Union
from hooks.yeedu import YeeduHook
from prefect.blocks.system import Secret
from hooks.yeedu import headers
import time
import json
import websocket
import _thread
import uuid
import copy
import ssl
import threading
import rel
import signal
from urllib.parse import urlparse
from prefect import get_run_logger


class YeeduOperator:

    def __init__(self, job_url, connection_block_name, login_password_block_name, token_block_name=None, *args, **kwargs):
        """
        Initializes the YeeduOperator instance with the given parameters.

        Parameters:
        - job_url (str): The URL of the Yeedu Notebook or job.
        - connection_block_name (str): The Prefect connection name. This connection is a JSON string and should contain:
            - username (str): The username for the connection.
            - YEEDU_VERIFY_SSL (str): true or false to verify SSL.
            - YEEDU_SSL_CERT_FILE (str): Path to the SSL certificate file.
        - login_password_block_name (str): The password variable name for connection in Prefect.
        - token_block_name (str, optional): The token variable name in Prefect. Default is None.
        - *args: Additional arguments.
        - **kwargs: Additional keyword arguments.
        
        Raises:
        - ValueError: If the job URL is not provided.
        - ValueError: If the connection_block_name is not a valid JSON string.
        """
        super().__init__(*args, **kwargs)
        self.job_url = self.check_url(job_url)
        self.connection_block_name = connection_block_name
        self.login_password_block_name = login_password_block_name
        self.password = self.get_password()
        self.token_block_name = token_block_name
        self.base_url, self.tenant_id, self.workspace_id, self.job_type, self.conf_id, self.restapi_port = self.extract_ids(self.job_url)
        self.logger = get_run_logger()

        self.hook = YeeduHook(
            conf_id=self.conf_id, 
            tenant_id=self.tenant_id, 
            base_url=self.base_url, 
            workspace_id=self.workspace_id, 
            connection_block_name=self.connection_block_name, 
            password=self.password,
            token_block_name=self.token_block_name
        )

        
        
        
    def check_url(self,job_url):

        """
        Checks if the job URL is provided.
        Parameters:
        - job_url (str): The URL for the job.
        Returns:
        - str: The job URL if it is provided.
        Raises:
        - ValueError: If the job URL is not provided (i.e., None).
    """
        if job_url is not None:
            return job_url
        else:
            raise ValueError(f"url is not set'{job_url}'")




    def get_password(self):
        """
    Retrieves the password from a secret block using the provided login password.

    This method loads a secret block identified by `self.login_password_block_name` using `Secret.load`.
    It then retrieves the password from the loaded secret block using `get()`.
    If the retrieved password is empty or not set, a `ValueError` is raised.

    Returns:
    - str: The retrieved password.
    """
        secret_block = Secret.load(self.login_password_block_name)
        password = secret_block.get()
        if not password:
            raise ValueError(f"password is not set'{self.login_password_block_name}'")
        return password


    
    def extract_ids(self, url):
        """
    Extracts various identifiers and constructs the base URL from the provided URL.

    Parses the URL to extract the base URL, tenant ID, workspace ID, job type, and configuration ID.
    The extracted base URL is constructed by appending ':{restapi_port}/api/v1/' to the parsed scheme and hostname.

    Args:
    - url (str): The URL from which to extract IDs and construct the base URL.
    """
        parsed_url = urlparse(url)
        restapi_port= urlparse(url).port
        path_segments = parsed_url.path.split('/')
        # Extract tenant_id and workspace_id based on path segments
        tenant_id = path_segments[2] if len(path_segments) > 2 else None
        workspace_id = path_segments[4] if len(path_segments) > 4 else None

        # Determine job_type and conf_id based on path segments

        if 'notebook' in path_segments:
            conf_id = path_segments[path_segments.index('notebook') + 1] if len(path_segments) > path_segments.index('notebook') + 1 else None
            job_type = 'notebook'
        elif 'conf' in path_segments:
            conf_id = path_segments[path_segments.index('conf') + 1] if len(path_segments) > path_segments.index('conf') + 1 else None
            job_type = 'conf'
        elif 'healthCheck' in path_segments:
            job_type = 'healthCheck'
            conf_id = -1
            workspace_id = -1
        else:
            raise ValueError("Please provide valid URL to schedule/run Jobs and Notebooks")
            
            
        # Construct base URL with :{restapi_port}/api/v1/ appended
        base_url = f"{parsed_url.scheme}://{parsed_url.hostname}:{restapi_port}/api/v1/"

        return base_url, tenant_id, int(workspace_id), job_type, int(conf_id), int(restapi_port)
    
    def execute(self):
        """
        Execute the YeeduOperator.

        - Submits a job to Yeedu based on the provided configuration ID.
        - Executes the appropriate operator based on the job_type parameter.

        """
        if self.job_type == 'conf':
            self.hook.yeedu_login()
            self._execute_job_operator()
        elif self.job_type == 'notebook':
            self.hook.yeedu_login()
            self._execute_notebook_operator()
        elif self.job_type == 'healthCheck':
            self._execute_heathcheck()
        else:
            raise ValueError(f"Invalid operator type: {self.job_type}")

    def _execute_heathcheck(self):
        # Create and execute YeeduJobRunOperator
        health_check_operator = YeeduHealthCheckOperator(
            base_url=self.base_url,
            connection_block_name=self.connection_block_name,
            password=self.password
        )
        health_check_operator.execute()
        
    def _execute_job_operator(self):
        # Create and execute YeeduJobRunOperator
        job_operator = YeeduJobRunOperator(
            job_conf_id=self.conf_id,
            tenant_id=self.tenant_id,
            base_url=self.base_url,
            workspace_id=self.workspace_id,
            connection_block_name=self.connection_block_name,
            password=self.password,
            token_block_name=self.token_block_name,
            restapi_port=self.restapi_port
        )
        job_operator.execute()

    def _execute_notebook_operator(self):
        # Create and execute YeeduNotebookRunOperator
        notebook_operator = YeeduNotebookRunOperator(
            base_url=self.base_url,
            workspace_id=self.workspace_id,
            notebook_conf_id=self.conf_id,
            tenant_id=self.tenant_id,
            connection_block_name=self.connection_block_name,
            password=self.password,
            token_block_name=self.token_block_name,
            restapi_port=self.restapi_port

        )
        notebook_operator.execute()

"""
YeeduHealthRunOperator
"""

class YeeduHealthCheckOperator():
    """
    YeeduHealthCheckOperator submits a job to Yeedu and waits for its completion.

    :param hostname: Yeedu API hostname (mandatory).
    :type hostname: str

    :param args: Additional positional arguments.
    :param kwargs: Additional keyword arguments.
    """

    template_fields: Tuple[str] = ("job_id",)

    def __init__(
        self,
        base_url: str,
        connection_block_name: str,
        password: str,
        *args,
        **kwargs,
    ) -> None:
        """
        Initialize the YeeduJobRunOperator.

        :param job_conf_id: The ID of the job configuration in Yeedu (mandatory).
        :param tenant_id: Yeedu API tenant_id. If not provided, retrieved from url provided.
        :param hostname: Yeedu API hostname (mandatory).
        :param workspace_id: The ID of the Yeedu workspace to execute the job within (mandatory).
        """
        super().__init__(*args, **kwargs)
        self.base_url: str = base_url
        self.connection_block_name=connection_block_name
        self.password=password
        self.hook: YeeduHook = YeeduHook(conf_id = None, tenant_id=None, base_url=self.base_url, workspace_id=None, connection_block_name=self.connection_block_name,password=self.password, token_block_name=None)
        self.job_id: Optional[Union[int, None]] = None
        self.logger = get_run_logger()

    def execute(self) -> None:
        """
        Execute the YeeduHealthCheckOperator.

        - Hits HealthCheck API

        """
        try:
            health_check_status: str = self.hook.yeedu_health_check()
            self.logger.info("Health Check Status: %s", health_check_status.status_code)           
        except Exception as e:
            raise ValueError(e)
        

"""
YeeduJobRunOperator
"""

class YeeduJobRunOperator():
    """
    YeeduJobRunOperator submits a job to Yeedu and waits for its completion.

    :param job_conf_id: The job configuration ID (mandatory).
    :type job_conf_id: str
    :param hostname: Yeedu API hostname (mandatory).
    :type hostname: str
    :param workspace_id: The ID of the Yeedu workspace to execute the job within (mandatory).
    :type workspace_id: int
    :param tenant_id: Yeedu API tenant_id. If not provided, it will be retrieved from Airflow Variables.
    :type token: str

    :param args: Additional positional arguments.
    :param kwargs: Additional keyword arguments.
    """

    template_fields: Tuple[str] = ("job_id",)

    def __init__(
        self,
        job_conf_id: str,
        base_url: str,
        workspace_id: int,
        tenant_id: str,
        connection_block_name: str,
        password: str,
        token_block_name: str,
        restapi_port: int,
        *args,
        **kwargs,
    ) -> None:
        """
        Initialize the YeeduJobRunOperator.

        :param job_conf_id: The ID of the job configuration in Yeedu (mandatory).
        :param tenant_id: Yeedu API tenant_id. If not provided, retrieved from url provided.
        :param hostname: Yeedu API hostname (mandatory).
        :param workspace_id: The ID of the Yeedu workspace to execute the job within (mandatory).
        """
        super().__init__(*args, **kwargs)
        self.job_conf_id: str = job_conf_id
        self.tenant_id: str = tenant_id
        self.base_url: str = base_url
        self.workspace_id: int = workspace_id
        self.connection_block_name=connection_block_name
        self.password=password
        self.token_block_name=token_block_name
        self.restapi_port=restapi_port
        self.hook: YeeduHook = YeeduHook(conf_id = self.job_conf_id, tenant_id=self.tenant_id, base_url=self.base_url, workspace_id=self.workspace_id, connection_block_name=self.connection_block_name,password=self.password,token_block_name=self.token_block_name)
        self.job_id: Optional[Union[int, None]] = None
        self.logger = get_run_logger()

    def execute(self) -> None:
        """
        Execute the YeeduJobRunOperator.

        - Submits a job to Yeedu based on the provided configuration ID.
        - Waits for the job to complete and retrieves job logs.

        """
        try:
            self.logger.info("Job Config Id: %s",self.job_conf_id)
            job_id = self.hook.submit_job(self.job_conf_id)
            
            restapi_port = self.restapi_port
            self.logger.info("Job Submited (Job Id: %s)", job_id)
            job_run_url = f'{self.base_url}tenant/{self.tenant_id}/workspace/{self.workspace_id}/spark/{job_id}/run-metrics?type=spark_job'.replace(f':{restapi_port}/api/v1','')
            self.logger.info("Check Yeedu Job run status and logs here " + job_run_url)
            job_status: str = self.hook.wait_for_completion(job_id)

            self.logger.info("Final Job Status: %s", job_status)
            

            job_log_stdout: str = self.hook.get_job_logs(job_id, 'stdout',restapi_port)
            job_log_stderr: str = self.hook.get_job_logs(job_id, 'stderr',restapi_port)
            job_log: str = " stdout : "+job_log_stdout+", stderr : "+job_log_stderr
            self.logger.info("Check for Yeedu job logs here %s ( %s )", job_id, job_log)

            if job_status in ['ERROR', 'TERMINATED', 'KILLED','STOPPED']:
                self.logger.error(job_log)
                raise ValueError(job_log)
                       
        except Exception as e:
            raise ValueError(e)

        finally:
            self.logger.info("Executing finally block")
            job_status = self.hook.get_job_status(job_id).json().get('job_status')
            if job_status not in ['ERROR', 'TERMINATED', 'KILLED','STOPPED','DONE']:
                self.logger.info(f"Job status in finally block: {job_status}")
                self.hook.kill_job(job_id)



"""
YeeduNotebookRunOperator
"""



class YeeduNotebookRunOperator():

    content_status = None 
    error_value = None

    def __init__(self, base_url, workspace_id, notebook_conf_id, tenant_id, connection_block_name, password, token_block_name, restapi_port,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = base_url
        #self.headers = {'Accept': 'application/json'}
        self.workspace_id = workspace_id
        self.notebook_conf_id = notebook_conf_id
        self.tenant_id = tenant_id
        self.notebook_cells = {}
        self.notebook_executed = True
        self.notebook_id = None
        self.cell_output_data = []
        self.cells_info = {}
        self.ws = None
        self.connection_block_name=connection_block_name
        self.token_block_name=token_block_name
        self.password=password
        self.restapi_port=restapi_port
        self.logger = get_run_logger()
        self.hook: YeeduHook = YeeduHook(conf_id = self.notebook_conf_id, tenant_id=self.tenant_id, base_url=self.base_url, workspace_id=self.workspace_id, connection_block_name=self.connection_block_name,password=self.password,token_block_name=self.token_block_name)

        # default (30, 60) -- connect time: 30, read time: 60 seconds
        # https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
        self.timeout = (30, 60)
        self.is_connection_alive = False
        self.keep_running = True

         
    def create_notebook_instance(self):

        """
    Create a notebook instance in the specified workspace using the configured hook.

    Raises:
    - Exception: If the POST request to create the notebook instance fails.

    Notes:
    - Constructs the POST URL using the base URL and workspace ID.
    - Sends a POST request to create the notebook instance with `notebook_conf_id`.
    - Logs the status code and response details of the POST request.
    - If successful (status code 200), extracts `notebook_id` from the response and updates `notebook_run_url`.
    - Logs the URL to check Yeedu notebook run status and logs.
    - Calls `get_active_notebook_instances`, `wait_for_kernel_status`, and `get_websocket_token` methods.
    """
        
        try:
            post_url = self.base_url + f'workspace/{self.workspace_id}/notebook'
            data={'notebook_conf_id': self.notebook_conf_id}
            post_response = self.hook._api_request('POST',post_url,data)

            status_code = post_response.status_code

            self.logger.info(f'Create Notebook - POST Status Code: {status_code}')
            self.logger.debug(
                f'Create Notebook - POST Response: {post_response.json()}')
            restapi_port=self.restapi_port
            if status_code == 200:
                self.notebook_id = post_response.json().get('notebook_id')
                notebook_run_url = f'{self.base_url}tenant/{self.tenant_id}/workspace/{self.workspace_id}/spark/{self.notebook_id}/run-metrics?type=notebook'.replace(f':{restapi_port}/api/v1','')
                self.logger.info("Check Yeedu notebook run status and logs here " + notebook_run_url)
                self.get_active_notebook_instances()
                self.wait_for_kernel_status(self.notebook_id)
                self.get_websocket_token()
                return
            else:
                raise Exception(post_response.text)
        except Exception as e:
            self.logger.error(
                f"An error occurred during create_notebook_instance: {e}")
            raise e

    def get_active_notebook_instances(self):
        """
    Retrieves the active notebook instance ID that matches the given notebook configuration ID
    from the specified workspace.

    Returns:
    - str: The ID of the active notebook instance.
    """
        try:
            retry_interval = 60
            max_retries = 20
            for retry in range(1, max_retries + 1):

                get_params = {
                    'notebook_conf_id': self.notebook_conf_id,
                    'notebook_status': 'RUNNING',
                    'isActive': 'true'
                }

                get_url = self.base_url + f'workspace/{self.workspace_id}/notebooks'

                get_active_notebook_instances_response = self.hook._api_request('GET',
                    url=get_url,
                    params=get_params,
                )

                if get_active_notebook_instances_response is not None:

                    status_code_response = get_active_notebook_instances_response.status_code

                    self.logger.info(
                        f'Get Active Notebooks - GET Status Code: {status_code_response}')
                    self.logger.debug(
                        f'Get Active Notebooks - GET Response: {get_active_notebook_instances_response.json()}')

                    if status_code_response == 200:
                        return (get_active_notebook_instances_response.json()).get('data')[0].get('notebook_id')
                    else:
                        self.logger.warning(
                            f'Retry attempt {retry}/{max_retries}. Retrying in {retry_interval} seconds...')
                        time.sleep(retry_interval)
                else:
                    # Handle the case where the response is None
                    self.logger.warning(
                        f'Retry attempt {retry}/{max_retries}. Retrying in {retry_interval} seconds...')
                    time.sleep(retry_interval)

            self.logger.error(
                f"Failed after {max_retries} retry attempts. Stopping program.")
            raise Exception(
                f"Failed after {max_retries} retry attempts. Stopping program.")
        except Exception as e:
            self.logger.error(
                f"An error occurred during get_active_notebook_instances: {e}")
            raise e

    def wait_for_kernel_status(self, notebook_id):
        """
    Waits for the kernel status of the specified notebook instance to match desired status ('idle', 'starting', 'busy').

    Args:
    - notebook_id (str): The ID of the notebook instance.

    Raises:
    - Exception: If unable to match the desired kernel status after maximum retries.
"""
        try:
            kernel_url = self.base_url + f'workspace/{self.workspace_id}/notebook/{notebook_id}/kernel/startOrGetStatus'

            # self.logger.info(f"Kernel URL: {kernel_url}")

            max_retries = 3
            self.logger.info("Notebook is starting. Please wait....")
            time.sleep(10)

            for retry in range(1, max_retries + 1):
                kernel_response = self.hook._api_request('POST',kernel_url)

                kernel_info = kernel_response.json().get('kernel_info', {})
                kernel_status = kernel_info.get('kernel_status')

                self.logger.info(
                    f"Kernel status attempt {retry}/{max_retries}: {kernel_status}")

                if self.check_kernel_status(kernel_status):
                    self.logger.info("Kernel status matched the desired status.")
                    break

                if retry == max_retries:
                    self.logger.warning(
                        f"Kernel status did not match the desired status after {max_retries} retries.")
                    raise Exception(
                        f"Kernel status did not match the desired status after {max_retries} retries.")
                else:
                    self.logger.info(
                        f"Retrying in 10 seconds... (Retry {retry}/{max_retries})")
                    time.sleep(10)

        except Exception as e:
            self.logger.error(
                f"An error occurred while checking kernel status: {e}")
            raise e

    # Example usage:
    def check_kernel_status(self, status):
        """
    Checks if the provided kernel status is one of the desired statuses ('idle', 'starting', 'busy').

    Args:
    - status (str): The kernel status to check.

    Returns:
    - bool: True if the kernel status is one of the desired statuses, False otherwise.
    """
        
        return status in ['idle', 'starting', 'busy']

    def get_websocket_token(self):
        """
    Retrieves the WebSocket token and constructs the WebSocket URL for the notebook instance.

    Returns:
    - str: The WebSocket URL for the notebook instance.

    Raises:
    - Exception: If unable to retrieve the WebSocket token or construct the WebSocket URL.

    Notes:
    - Extracts the token from the 'Authorization' header.
    - Constructs the WebSocket URL using the base URL, workspace ID, notebook ID, and token.
    - Sends a GET request using `_api_request` method of `hook` to get the WebSocket token.
    """
        
        try:
            token = headers.get('Authorization').split(" ")[1]

            # Construct WebSocket token URL
            proxy_url = self.base_url + f'workspace/{self.workspace_id}/notebook/{self.notebook_id}/kernel/ws'

            #self.logger.info(f"WebSocket Token URL: {proxy_url}")


            # hit proxy api to create web socket connection
            proxy_response = self.hook._api_request('GET',
                url=proxy_url,
                params={
                    'yeedu_session': token
                },
            )

            if proxy_response.status_code == 200:

                self.logger.debug(
                    f"WebSocket Token Response: {proxy_response.json()}")

                # creating web socket url
                websocket_url = self.base_url + f"workspace/{self.workspace_id}/notebook/{self.notebook_id}/kernel/ws/yeedu_session/{token}"
                websocket_url = websocket_url.replace('http://', 'ws://').replace('https://', 'wss://')
                #self.logger.info(f"WebSocket URL: {websocket_url}")
                return websocket_url
            else:
                raise Exception(
                    f"Failed to get WebSocket token. Status code: {proxy_response.status_code} messsgae: {proxy_response.text}")

        except Exception as e:
            self.logger.error(
                f"An error occurred while getting WebSocket token: {e}")

    def get_code_from_notebook_configuration(self):
        
        """
    Retrieves the notebook configuration details for the specified notebook configuration ID.

    Returns:
    - Response object: The response object containing notebook configuration details.

    Raises:
    - Exception: If unable to retrieve the notebook configuration details.

    Notes:
    - Constructs the GET URL using the base URL and workspace ID.
    - Sends a GET request using `_api_request` method of `hook` with specific parameters.
    - Logs the status code and response details of the GET request.
    - Raises an exception if the status code of the response is not 200.
    """
        
        try:
            # Construct notebook configuration URL
            get_notebook_url = self.base_url + f'workspace/{self.workspace_id}/notebook/conf'

            notebook_conf_response = self.hook._api_request('GET',
                get_notebook_url,
                params={'notebook_conf_id': self.notebook_conf_id},
            )

            if notebook_conf_response.status_code == 200:
                return notebook_conf_response
            else:
                self.logger.warning(
                    f"Failed to get notebook configuration. Status code: {notebook_conf_response.status_code} message: {notebook_conf_response.text}")
                raise Exception(
                    f"Failed to get notebook configuration. Status code: {notebook_conf_response.status_code} message: {notebook_conf_response.text}")

        except Exception as e:
            self.logger.error(
                f"An error occurred while getting notebook configuration: {e}")
            raise e

    def check_notebook_instance_status(self):

        """
            Checks the status of the notebook instance with the specified notebook ID.

            Returns:
            - str: The status of the notebook instance ('STOPPED' if stopped).

            Raises:
            - Exception: If unable to retrieve the notebook status after maximum retries.

            Notes:
            - Constructs the GET URL for notebook status using the base URL and notebook ID.
            - Sends a GET request using `_api_request` method of `hook`.
            - Logs the status code of the GET request and the retrieved notebook status.
            - Retries up to `max_retries` times with 10 seconds delay between retries.
        """
        
        try:
            check_notebook_status_url = self.base_url + f'workspace/{self.workspace_id}/notebook/{self.notebook_id}'

            self.logger.info(
                f"Checking notebook_instance status of : {self.notebook_id}")

            max_retries = 3
            status = None

            # Check if the notebook status is 'stopped'
            for retry in range(0, max_retries + 1):
                notebook_status_response = self.hook._api_request('GET',
                    url=check_notebook_status_url,
                )

                self.logger.info(
                    f'Notebook_instance GET status response: {notebook_status_response.status_code}')
                self.logger.debug(
                    f'Notebook_instance GET status response: {notebook_status_response.json()}')

                if notebook_status_response.status_code == 200:

                    status = notebook_status_response.json().get('notebook_status')
                    self.logger.info(f"notebook_status: {status}")
                    self.logger.info(f"retry number: {retry}")

                    if status == 'STOPPED':
                        self.logger.info("Notebook is stopped.")
                        break

                    time.sleep(10)

                    # elif retry == max_retries:
                    #     self.logger.warning(
                    #         f"Notebook_instance status did not match the desired status after {max_retries} retries.")
                    #     raise Exception(
                    #         f"Failed to get notebook status. Status code: {notebook_status_response.status_code}")
                    # else:
                    #     self.logger.info(
                    #         f"Retrying in 10 seconds... (Retry {retry}/{max_retries})")
                    #     time.sleep(10)

                elif retry == max_retries:
                        
                    self.logger.warning(
                            f"Error occured while checking notebook status after {max_retries} retries.")
                    raise Exception(
                            f"Failed to get notebook status. Status code: {notebook_status_response.status_code}")
                else:
                        
                    self.logger.info(
                            f"Retrying to get notebook status in 10 seconds... (Retry {retry}/{max_retries})")
                    time.sleep(10)

            return status
        except Exception as e:
            self.logger.error(
                f"An error occurred while checking notebook instance status: {e}")

    def check_notebook_status(self):

        """
        Checks the status of the notebook instance with the specified notebook ID.

        Returns:
        - tuple: A tuple containing the status of the notebook instance and the execution time in seconds.

        Raises:
        - Exception: If unable to retrieve the notebook status after maximum retries.

        Notes:
        - Constructs the GET URL for notebook status using the base URL and notebook ID.
        - Sends a GET request using `_api_request` method of `hook`.
        - Logs the status code of the GET request and the retrieved notebook status.
        - Retries up to `max_retries` times with 10 seconds delay between retries.
    """
        
        try:
            check_notebook_status_url = self.base_url + f'workspace/{self.workspace_id}/notebook/{self.notebook_id}'

            max_retries = 5
            status = None

            # Check if the notebook status is 'stopped'
            for retry in range(0, max_retries + 1):
                notebook_status_response = self.hook._api_request('GET',url=check_notebook_status_url,
                                                                  )

                if notebook_status_response.status_code == 200:

                    status = notebook_status_response.json().get('notebook_status')
                    notebook_execution_time = notebook_status_response.json().get('job_execution_time_sec')


                elif retry == max_retries:
                    self.logger.warning(
                        f"Notebook_instance status did not match the desired status after {max_retries} retries.")
                    raise Exception(
                        f"Failed to get notebook status. Status code: {notebook_status_response.status_code}")
                else:
                    self.logger.info(
                        f"Retrying in 10 seconds... (Retry {retry}/{max_retries})")
                    time.sleep(20)

            return status, notebook_execution_time
        except Exception as e:
            self.logger.error(
                f"An error occurred while checking notebook instance status: {e}")

    def stop_notebook(self):

        """
            Stops the notebook instance with the specified notebook ID.

            Returns:
            - Response object: The response object containing the result of stopping the notebook instance.

            Raises:
            - Exception: If unable to stop the notebook instance.

            Notes:
            - Constructs the POST URL for stopping the notebook instance using the base URL and notebook ID.
            - Sends a POST request using `_api_request` method of `hook`.
            - Logs the status code and response details of the POST request.
            - Checks the notebook instance status after stopping.
    """
        
        try:
            stop_notebook_url = self.base_url + f'workspace/{self.workspace_id}/notebook/kill/{self.notebook_id}'

            self.logger.debug(f"Stopping notebook instance id: {self.notebook_id}")

            # Use post_request function
            notebook_stop_response = self.hook._api_request('POST',stop_notebook_url)

            self.logger.info(
                f'Stop Notebook - POST Response Status: {notebook_stop_response.status_code}')
            self.logger.debug(
                f'Stop Notebook - POST Response: {notebook_stop_response.json()}')

            if notebook_stop_response.status_code == 201:
                self.check_notebook_instance_status()
                self.logger.info(
                    f"Notebook instance id: {self.notebook_id} stopped successfully.")
                return notebook_stop_response
            else:
                self.logger.error(
                    f"Failed to stop notebook. Status code: {notebook_stop_response.status_code}, Message: {notebook_stop_response.text}")
                raise Exception(
                    f"Failed to stop notebook. Status code: {notebook_stop_response.status_code}, Message: {notebook_stop_response.text}")
        except Exception as e:
            self.logger.error(f"An error occurred while stopping notebook: {e}")
            raise e

    def update_notebook_cells(self):

        """
            Updates the output of notebook cells based on the message ID.

            Returns:
            - Response object: The response object containing the result of updating the notebook cells.

            Raises:
            - Exception: If unable to update the notebook cells.

            Notes:
            - Constructs the POST URL for updating notebook cells using the base URL and notebook configuration ID.
            - Prepares the data containing updated cell information.
            - Sends a POST request using `_api_request` method of `hook`.
            - Logs the status code and response details of the POST request.
        """
        
        try:
            cells_info = {"cells": self.cells_info}
            msg_id_to_update = self.cell_output_data[0]['msg_id']
            # Iterate through cells and update output if msg_id matches
            for cell in cells_info['cells']:
                if 'cell_uuid' in cell and cell['cell_uuid'] == msg_id_to_update:
                    self.logger.info(f"MSG ID {msg_id_to_update}")
                    self.logger.info(f"THE OUTPUT VALUE {self.cell_output_data[0]['output']}")
                    cell['output'] = [{"text": self.cell_output_data[0]['output']}] 
                    self.cell_output_data.clear()

            for cell in cells_info['cells']:
                if 'msg_id' in cell:
                    del cell['msg_id']

            self.logger.info(f"CELLS INFO {cells_info}")
            update_cell_url = self.base_url + f'workspace/{self.workspace_id}/notebook/{self.notebook_conf_id}/update'
            data = cells_info
            update_cells_response = self.hook._api_request('POST',update_cell_url,data)

            self.logger.info(f'this is cell response {update_cells_response}')

            self.logger.info(update_cells_response.status_code)

            self.logger.debug(
                f'Update Notebook cells - POST Response: {update_cells_response.json()}')

            if update_cells_response.status_code == 201:
                self.logger.info("Notebook cells updated successfully.")
                self.cell_output_data.clear()
                return update_cells_response
            else:
                self.logger.error(
                    f"Failed to update notebook cells. Status code: {update_cells_response.status_code}, Message: {update_cells_response.text}")
                raise Exception(
                    f"Failed to update notebook cells. Status code: {update_cells_response.status_code}, Message: {update_cells_response.text}")
        except Exception as e:
            self.logger.error(f"An error occurred while updating notebook cells: {e}")
            raise e

    def exit_notebook(self, exit_reason):

        """
    Exits the notebook instance, clearing its cells and stopping it if necessary.

    Args:
    - exit_reason (str): The reason for exiting the notebook.

    Raises:
    - Exception: If an error occurs while exiting the notebook.

    Notes:
    - Clears the notebook cells and stops the notebook instance if it has not been executed yet.
    - Logs the action and any errors encountered during the process.
    """
        
        try:
            if self.notebook_executed:
                return 0

            self.logger.info(f'Clearing the notebook cells')

            self.notebook_cells.clear()
            self.stop_notebook()
            #raise Exception(exit_reason)
        except Exception as e:
            self.logger.error(f'Error while exiting notebook: {e}')
            raise e

    def on_message(self, ws, message):

        """
    Handles incoming WebSocket messages.

    Args:
    - ws: WebSocketApp object.
    - message (str): Incoming message from the WebSocket.

    Raises:
    - Exception: If an unsupported message type is encountered or if notebook instance status check fails.

    Notes:
    - Parses incoming JSON message and processes based on 'msg_type'.
    - Handles 'execute_result', 'error', 'execute_input', 'stream', 'display_data', 'status', and 'execute_reply' messages.
    - Logs messages and errors appropriately.
    """
        
        try:
            response = json.loads(message)

            msg_type = response.get('msg_type', '')

            if msg_type == 'execute_result':
                content = response.get('content', {})
                output_data = content.get('data', {}).get('text/plain', '')
                self.logger.info(f"Execution Result:\n{output_data}")
            elif msg_type == 'error':
                content = response.get('content', {})
                error_name = content.get('ename', '')
                self.error_value = content.get('evalue', '')
                traceback = content.get('traceback', [])
                self.logger.error(f"Error: {error_name} - {self.error_value}")
                self.logger.error("Traceback:")
                #self.logger.info(self.error_value)
                for tb in traceback:
                    self.logger.error(tb)
            elif msg_type == 'execute_input':
                self.logger.info(response)
                content = response.get('content', {})
                code_input = content.get('code', '')
                self.logger.info(f"Execute Input:\n{code_input}")
            elif msg_type == 'stream':
                content = response.get('content', {})
                text_value = content.get('text', '')
                msg_id = response['parent_header']['msg_id']
                self.logger.info(f'this msg_id is in stream {msg_id}')
                self.cell_output_data.append({'msg_id': msg_id, 'type': 'text', 'output': [text_value]})
                self.logger.info(f'stream output is {self.cell_output_data}')
                self.update_notebook_cells()
            elif msg_type == 'display_data':
                content = response.get('content', {})
                self.logger.info(f"Display Data: {content}")
                msg_id = response['parent_header']['msg_id']
                img_resp = response.get('content', {}).get('data', {}).get('image/png')
                text_resp = response.get('content', {}).get('data', {}).get('text/plain')
                if img_resp:
                     image_url = f'data:image/png;base64,{img_resp}'
                     self.cell_output_data.append({'msg_id': msg_id,'type': 'image', 'output': image_url})
                if text_resp:
                    self.cell_output_data.append({'msg_id': msg_id,'type': 'text', 'output': text_resp})
                self.update_notebook_cells()
            elif msg_type == 'status':
                execution_state = response.get(
                    'content', {}).get('execution_state', '')
                self.logger.info(f"Execution State: {execution_state}")
            elif msg_type == 'execute_reply':
                content = response.get('content', {})
                self.logger.info(f"Content {content}")
                self.content_status = content.get('status', '')
                self.logger.info(self.content_status)
                msg_id = response['parent_header']['msg_id']
                self.logger.info(f"Message Id: {msg_id}")
                if self.content_status == 'ok':
                    try:
                        self.logger.info('Removing notebook cells ...')

                        # Update the notebook_cells array after content.status is ok by removing the msg_id under parent_header
                        self.notebook_cells = [
                            cell for cell in self.notebook_cells if cell.get('msg_id') != msg_id]
                        self.logger.info(
                            f"Notebook cells array after removing {msg_id}: {self.notebook_cells}")
                    except ValueError:
                        pass
                elif self.content_status == 'error':
                    self.error_value = content.get('evalue', '')
                    traceback = content.get('traceback', [])
                    self.logger.info(traceback)

                    self.notebook_executed = False

                    self.exit_notebook(
                        f'cell with message_id: {msg_id} failed with error: {self.error_value}')
                else:
                    raise Exception(
                        f"Invalid self.content_status: {self.content_status}")

        except Exception as e:
            self.logger.error(f"Unsupported message type: {e}")

            if self.check_notebook_instance_status() != 'STOPPED':
                self.exit_notebook(f'Unsupported message_type: {e}')

            raise e

    def on_error(self, ws, error):

        """
        Handles WebSocket errors.

        Args:
        - ws: WebSocketApp object.
        - error: The error encountered.

        Raises:
        - Exception: If an error occurs while handling the WebSocket error.

        Notes:
        - Logs the WebSocket error.
    """
        
        try:
            self.logger.info(f"WebSocket encountered an error: {error}")
 
        except Exception as e:
            self.logger.error(e)
            raise e

    def on_close(self,ws, close_status_code, close_msg):

        """
            Handles WebSocket closure.

            Args:
            - ws: WebSocketApp object.
            - close_status_code (int): The status code for WebSocket closure.
            - close_msg (str): The close message.

            Raises:
            - Exception: If an error occurs while handling WebSocket closure.

    """
        
        try:
            self.logger.info(f"WebSocket closed {close_status_code} {close_msg}")
            self.is_connection_alive = False

            # if self.check_notebook_instance_status()!= 'STOPPED':
            #     self.exit_notebook(f"Websocket closed : {e}")

        except Exception as e:
            self.logger.error(e)
            raise e

    def on_open(self, ws):

        """
            Handles WebSocket opening.

            Args:
            - ws: WebSocketApp object.
    """
        
        self.logger.info("WebSocket opened")
        self.is_connection_alive = True

    def close_websocket_connection(self):

        if self.is_connection_alive:
            self.logger.info("Closing the active WebSocket connection")
            self.keep_running = False
            if self.ws:
                self.ws.close()
            if self.thread:
                self.thread.join()
            self.logger.info("WebSocket connection closed")
            self.is_connection_alive = False
        else:
            self.logger.info("No active WebSocket connections")

     

    def send_execute_request(self, ws, code, session_id, msg_id):

        """
            Sends an execute request over WebSocket.

            Args:
            - ws: WebSocketApp object.
            - code (str): The code to execute.
            - session_id (str): The session ID.
            - msg_id (str): The message ID.
    """
        try:
            from datetime import datetime
            current_date = datetime.now()

            execute_request = {
                'header': {
                    'msg_type': 'execute_request',
                    'msg_id': msg_id,
                    'username': 'username',
                    'session': session_id,
                    'date': current_date.strftime("%Y-%m-%d %H:%M:%S"),
                    'version': '5.3'
                },
                'metadata': {},
                'content': {
                    'code': code,
                    'silent': False,
                    'store_history': True,
                    'user_expressions': {},
                    'allow_stdin': False
                },
                'buffers': [],
                'parent_header': {},
                'channel': 'shell'
            }

            ws.send(json.dumps(execute_request))
        except Exception as e:
            self.logger.error(f"Error while sending execute request: {e}")
            raise e

    def connect_websocket(self):
        self.ws = websocket.WebSocketApp(
            self.get_websocket_token(),
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        def run_forever_in_thread():
            while self.keep_running:
                try:
                    if self.hook.YEEDU_VERIFY_SSL == 'true':
                        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_REQUIRED, "ca_certs": self.hook.YEEDU_SSL_CERT_FILE}, reconnect=5)
                    elif self.hook.YEEDU_VERIFY_SSL == 'false':
                        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, reconnect=5)
                except Exception as e:
                    self.logger.error(f"Error in run_forever: {e}")

        self.thread = threading.Thread(target=run_forever_in_thread)
        self.thread.start()
        return self.ws
 

    # Define the signal handler function
    def signal_handler(self,sig, frame):
        self.logger.info("Signal received, aborting...")
        rel.abort()  # Stop the event loop and gracefully shut down the WebSocket connection

    def execute(self):

        """
    Executes the notebook cells by sending execute requests over WebSocket.

    Raises:
    - Exception: If an error occurs during notebook execution.

    Notes:
    - Initializes the notebook execution environment by creating a notebook instance and setting up a WebSocket connection.
    - Retrieves the notebook cells from the notebook configuration and sends execute requests for each cell.
    - Handles incoming messages through the `on_message` method and processes execution results, errors, and other message types.
    - Periodically checks the status of the notebook execution and exits if the notebook is terminated or stopped.
    - Stops the notebook instance if execution is completed or if an error occurs, and logs the appropriate messages.
    - Handles graceful shutdown of the notebook instance and WebSocket connection in case of interruption or error.
    """
        
        # Send execute requests for notebook cells
        try:

            self.create_notebook_instance()

            signal.signal(signal.SIGINT, self.signal_handler)

            self.ws = self.connect_websocket()

            rel.dispatch()

            time.sleep(5)

            # Get notebook cells from configuration

            notebook_get_response = self.get_code_from_notebook_configuration()

            self.notebook_cells = notebook_get_response.json().get(
                'notebook_cells', {}).get('cells', [])

            self.cells_info = copy.deepcopy(self.notebook_cells)

            self.logger.info(f"Notebook Cells: {self.notebook_cells}")

            session_id = str(uuid.uuid4())

            # Send execute requests for each notebook cell
            for cell in self.notebook_cells:
                code = cell.get('code')
                msg_id = cell.get('cell_uuid')

                self.send_execute_request(self.ws, code, session_id, msg_id)

                cell['msg_id'] = msg_id

            # awaiting all the notebook cells executing
            while len(self.notebook_cells) > 0:
                time.sleep(10)
                self.logger.info('Waiting {} cells to finish'.format(
                    len(self.notebook_cells)))
                
                notebook_status, notebook_execution_time = self.check_notebook_status()
                self.logger.info(f"Current Notebook Status {notebook_status}")
                if notebook_status in ['TERMINATED', 'STOPPED']:
                    self.notebook_executed = False
                    self.logger.info(f"Notebok Status {notebook_status}")
                    self.exit_notebook(f'Exiting notebook as the Notebook status is {notebook_status}')
                    break


            # Stop the notebook if execution is completed
            if self.notebook_executed:
                time.sleep(5)
                self.stop_notebook()
                return 0
            else:
                self.logger.info("Exiting notebook from main function")

                if self.check_notebook_instance_status() != 'STOPPED':
                    self.exit_notebook(
                        f'Exiting notebook from main function')

            self.close_websocket_connection()

            if self.content_status == 'error': 
                raise ValueError(f"{self.error_value}")
            

            if notebook_status in ['TERMINATED']:
                raise ValueError("Notebook is Terminated")

        except Exception as e:
            self.logger.error(
                f"Notebook execution failed with error:  {e}")
            raise e
        
        finally:
            self.notebook_executed = False
            self.logger.info("Closing the websocket connection in finally block")
            self.close_websocket_connection()
            if self.notebook_id is not None:
                if self.check_notebook_instance_status() != 'STOPPED':
                    self.logger.info("Exiting notebook in finally block")
                    self.exit_notebook(
                            f'Exiting notebook')