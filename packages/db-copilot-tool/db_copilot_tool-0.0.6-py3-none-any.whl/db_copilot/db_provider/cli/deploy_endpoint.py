import os
import json
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Environment,
    BuildContext,
    CodeConfiguration,
    OnlineRequestSettings
)
import shutil

from azure.identity import InteractiveBrowserCredential, DeviceCodeCredential, AzureCliCredential, ManagedIdentityCredential

def get_code_path(workspace_dir: str) -> str:
    import uuid
    version = str(uuid.uuid1())
    temp_workspace = workspace_dir + f"/.{version}"
    print("Temp workspace", temp_workspace)
    os.makedirs(temp_workspace)

    from db_copilot.db_provider.db_provider_api import _PKG_ABS_PATH
    tgt_dir = shutil.copytree(_PKG_ABS_PATH, os.path.join(temp_workspace, "db_copilot"))

    return tgt_dir, version

def read_config(config_path: str):
    with open(config_path, 'r', encoding='utf-8') as fr:
        config = json.load(fr)
        conn_envs = {}
        for db_config in config:
            db_id = db_config["db_id"]
            conn_string: str = db_config.pop("conn_string")
            if conn_string.startswith("{{") and conn_string.endswith("}}"):
                conn_string = os.getenv(conn_string[2:-2])
            conn_string_env = f"DB_PROVIDER_CONN_STRING_{db_id}"
            conn_envs[conn_string_env] = conn_string
            db_config["conn_string"] = "{{" + conn_string_env  +"}}"

        return config, conn_envs

def deploy_endpoint_main(args):
    # Subscription and its
    source_code_dir, version = get_code_path(workspace_dir=args.workspace_dir)
    print("Source dir", source_code_dir)

    subscription_id, resource_group, workspace_name = args.subscription_id, args.resource_group, args.workspace_name

    # Get a handle to the workspace
    if args.credential_type == "interactive_browser":
        credential = InteractiveBrowserCredential()
    elif args.credential_type == "device_code":
        credential = DeviceCodeCredential()
    else:
        client_id = os.environ.get("DEFAULT_IDENTITY_CLIENT_ID", None)
        if client_id:
            credential = ManagedIdentityCredential(client_id=client_id)
        else:
            credential = AzureCliCredential()
    
    ml_client = MLClient(
        credential, subscription_id, resource_group, workspace_name
    )

    endpoint_name, deployment_name = args.endpoint_name, args.deployment_name
    local_mode = False

    # create an online endpoint
    endpoint = ManagedOnlineEndpoint(
        name=endpoint_name,
        description="DB provider to support schema retrieval and query execution",
        auth_mode="key",
        tags={ "name": endpoint_name, "deployment": deployment_name, 'version': version },
    )

    ml_client.online_endpoints.begin_create_or_update(endpoint, local=local_mode).result()

    env_build = BuildContext(
        path=os.path.join(source_code_dir, 'db_provider/envs'),
        dockerfile_path="Dockerfile"
    )
    env = Environment(
        name="db_provider_env",
        #conda_file="envs/env_cpu.yml",
        #image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04:latest",
        build=env_build
    )

    env_variables = {}
    db_config, config_envs = read_config(args.db_config_path)
    config_dir = os.path.join(source_code_dir, 'db_provider/configs')
    os.makedirs(config_dir, exist_ok=True)
    env_variables.update(config_envs)
    config_path = os.path.join(config_dir, "db_provider.{}.json".format(deployment_name))
    with open(config_path, 'w', encoding='utf-8') as fw:
        json.dump(db_config, fw, indent=4)
        print(f"Save db config to {config_path}")
    
    env_variables["DB_CONFIG_PATH"] = "db_provider/configs/db_provider.{}.json".format(deployment_name)
    if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        print("Enable application insights logging")
        env_variables["APPLICATIONINSIGHTS_CONNECTION_STRING"] = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    blue_deployment = ManagedOnlineDeployment(
        name=deployment_name,
        endpoint_name=endpoint_name,
        model=None,
        environment=env,
        code_configuration=CodeConfiguration(
            code=source_code_dir,
            scoring_script="db_provider/db_provider_api.py"
        ),
        instance_type=args.instance_type,
        instance_count=args.instance_count,
        environment_variables=env_variables,
        request_settings=OnlineRequestSettings(request_timeout_ms=90000)
    )

    print(blue_deployment)
    print(endpoint.scoring_uri)
    
    # blue deployment takes 100 traffic
    if not local_mode:
        endpoint.traffic = { deployment_name: args.deployment_traffic }
        ml_client.online_deployments.begin_create_or_update(
            deployment=blue_deployment, local=local_mode
        ).result()
    else:
        ml_client.online_deployments.begin_create_or_update(
            deployment=blue_deployment, local=local_mode
        )

    
    logs = ml_client.online_deployments.get_logs(
        name=deployment_name, endpoint_name=endpoint_name, local=local_mode, lines=100
    )
    
    print(logs)
    online_endpoint = ml_client.online_endpoints.get(name=endpoint_name, local=local_mode)
    print(online_endpoint.scoring_uri)

    # shutil.rmtree(source_code_dir)
    print("Clean local source code over!")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Deploy DB Provider Endpoint")
    parser.add_argument(
        '--subscription_id', type=str, required=True
    )
    parser.add_argument(
        '--resource_group', type=str, required=True,
    )
    parser.add_argument(
        '--workspace_name', type=str, required=True
    )

    parser.add_argument(
        '--endpoint_name', type=str, default="db-provider",
    )

    parser.add_argument(
        '--deployment_name', type=str, default='blue',
    )

    parser.add_argument(
        '--deployment_traffic', type=int, default=100, 
    )
    parser.add_argument(
        '--instance_type', type=str, default="Standard_DS3_v2"
    )

    parser.add_argument(
        '--instance_count', type=int, default=1
    )

    parser.add_argument(
        '--credential_type', type=str, default=None
    )

    parser.add_argument(
        '--db_config_path', type=str, default=None
    )

    parser.add_argument(
        '--db_conn_string', type=str, default=None
    )

    parser.add_argument(
        "--workspace_dir", type=str, default="./"
    )
    
    args = parser.parse_args()
    #get_code_path(workspace_dir=args.workspace_dir)
    deploy_endpoint_main(args)
    pass