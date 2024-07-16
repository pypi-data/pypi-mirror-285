# Setting up Yeedu with Prefect

This guide provides step-by-step instructions for integrating Yeedu with Prefect to create and manage data workflows.

## Prerequisites

- An active Yeedu account
- An active Prefect account
- Access to the Prefect Cloud or Prefect Orion instance
- Python 3.6 or higher

## Steps

### 1. Configure and Start a Cluster on Yeedu

1. Log in to Yeedu.
2. Configure and start a cluster.
3. Create a workspace and a job configuration or notebook.
4. Fetch the URL of the created resource.

### 2. Create Yeedu Specific Tokens in Prefect

1. Log in to Prefect.
2. Create a block with name `yeedu_connection_details` witb below JSON.

```json
{
    "username": "YSU0000",
    "YEEDU_VERIFY_SSL": "false",
    "YEEDU_SSL_CERT_FILE": ""
}
```

3. If the Yeedu authentication type is
    a. LDAP or Azure AD: create a block with name with `yeedu_password` to connect to Yeedu with the username given in `yeedu_connection_details`
    b. Azure AD SSO: create a block with name with `yeedu_token` to connect to Yeedu with the username given in `yeedu_connection_details` where you can the token value using the Yeedu RESTAPI

4. Create a block to store the access token (PAT) of github. Recommended name `github_pat_token` (For remote storage)

### 3. Setup Pre-requisites

#### 3.1 Install Pip Packages

We need to install the below python packages in the worker

```python
requests>=2.27
websocket-client>=1.8.0
rel>=0.4.9.19
prefect_github==0.2.6
prefect
```

### 3.2 Login to Prefect Cloud via CLI

Please refer to prefect documentation to generate API_KEY

```bash
prefect cloud login -k <API_KEY>
```

### 3.3 Install Yeedu's Prefect Operator

Install the Yeedu Prefect operator using pip:

```bash
pip3 install yeedu-prefect-operator
```

### 4. Create a Flow code using Yeedu's Prefect Operator

Use the Yeedu Prefect operator to create a flow for each job. Use the URL fetched in step 1 and the credentials configured in step 2 for authentication.

```python
from prefect import flow
from operators.yeedu import YeeduOperator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@flow(retries=0, retry_delay_seconds=5, log_prints=True)
def job_run_flow():
    """
    Prefect flow to execute a Yeedu job.

    This flow uses the YeeduOperator to run a job specified by the job_url.
    The credentials and connection details are managed within the YeeduOperator using the block names.
    """
    # URL of the Yeedu Notebook or job
    job_url = '<YEEDU_JOB_URL>'
    logger.info(f"Job URL: {job_url}")

    # Connection block name and login password block name
    connection_block_name = '<NAME_OF_CONNECTION_BLOCK_VARIABLE>'
    login_password_block_name = 'NAME_OF_PASSWORD_BLOCK_VARIABLE'
    # connection_block_name='<NAME_OF_TOKEN_BLOCK>' # Use this instead of password block for handling SSO signin
    
    logger.info("Initializing Yeedu operator...")

    # Initialize and execute the Yeedu operator  
    operator = YeeduOperator(
        job_url=job_url,
        connection_block_name=connection_block_name,
        login_password_block_name=login_password_block_name
        # connection_block_name=connection_block_name
    )
        
    logger.info("Executing Yeedu job...")
    operator.execute()
    logger.info("Yeedu job execution completed.")

```

### 5. Execute the Flow - Creating Deployment

#### 5.1 Using Local Machine as Prefect Worker and Prefect Flow Code stored in Local

When you want to the craete the workflow written abov from your local, we need to do the below steps

1. Add the below code to your flow python code

```python
# To use your local machine as prefect worker, use the code below which is commented
if __name__ == "__main__":
    # Serve the flow with a specific name
    job_run_flow.serve(name="<NAME_OF_DEPLOYMENT>")
```

3. Run the python file and your local will be used as Prefect worker and the python file in your local will be used to create the flow

#### 5.2 Using Prefect Worker and Prefect Flow Code stored in Remote Github

To deploy the Prefect flow stored in the GitHub repository, you need to provide the GitHub details in the code snippet below. This code fetches the flow from the specified GitHub repository and deploys it.

```python
from prefect import flow
from prefect.runner.storage import GitRepository
from prefect.blocks.system import Secret
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flow.from_source(
    source=GitRepository(
        url="<YOUR_GITHUB_REPO_URL>",
        branch="<YOUR_BRANCH_NAME>",
        credentials={
            "access_token": Secret.load("<NAME_OF_THE_GITHUB_TOKEN_BLOCK_VARIABLE>")
        }
    ),
    entrypoint="<YOUR_ENTRYPOINT_FILE>:<YOUR_FLOW_FUNCTION>",
).deploy(
    name="<NAME_OF_THE_DEPLOYMENT>",
    work_pool_name="<NAME_OF_WORKER>"
)
```

To Build Prefect Custom Operator, download the source code and run the below command

```python
python setup.py sdist bdist_wheel
```

## Architecture Diagram

Below is a high-level architecture diagram depicting the interaction between Yeedu and Prefect:

![Architecture Diagram](https://via.placeholder.com/800x600.png?text=Yeedu+and+Prefect+Integration+Architecture+Diagram)

### Diagram Explanation

1. **User Interaction**:
   - Users log in to Yeedu to configure clusters and workspaces.
   - Users log in to Prefect to create blocks for Yeedu credentials.

2. **Yeedu Cluster and Job Configuration**:
   - Clusters and job configurations are set up in Yeedu.
   - URLs for the configured jobs are fetched from Yeedu.

3. **Prefect Flow Creation**:
   - Flows are created in Prefect using the Yeedu operator.
   - Prefect uses the credentials stored in Prefect blocks to authenticate with Yeedu.

4. **Deployment and Scheduling**:
   - Flows are deployed and scheduled in Prefect.
   - Prefect workers execute the flows and communicate with Yeedu API to run the jobs.

5. **Execution and Monitoring**:
   - Yeedu executes the jobs and Prefect monitors the job execution.
