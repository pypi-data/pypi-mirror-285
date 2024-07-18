import base64
import hashlib
import json
import uuid
from typing import Optional

import click
import requests

from tensorkube.constants import NAMESPACE, SERVICE_ACCOUNT_NAME, REGION
from tensorkube.services.eks_service import get_cluster_oidc_issuer_url
from tensorkube.services.iam_service import create_s3_csi_driver_role, attach_role_policy


def create_mountpoint_driver_role_with_policy(cluster_name, account_no, role_name, policy_name,
                                              service_account_name=SERVICE_ACCOUNT_NAME, namespace=NAMESPACE,
                                              region=REGION):
    oidc_issuer_url = get_cluster_oidc_issuer_url(cluster_name)
    create_s3_csi_driver_role(account_no, role_name, oidc_issuer_url, namespace, service_account_name)
    attach_role_policy(account_no, policy_name, role_name, region)


def get_base64_encoded_docker_config(username: str, password: str, email: str):
    auth = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")

    docker_config_dict = {"auths": {
        "https://index.docker.io/v1/": {"username": username, "password": password, "email": email, "auth": auth, }}}

    base64_encoded_docker_config = base64.b64encode(json.dumps(docker_config_dict).encode("utf-8")).decode("utf-8")
    return base64_encoded_docker_config


def sanitise_name(name: str):
    return name.replace("_", "-").replace(" ", "-").lower()


def sanitise_assumed_role_arn(arn: str):
    arn = arn.replace('assumed-role', 'role')
    last_slash_index = arn.rfind('/')
    if last_slash_index != -1:
        arn = arn[:last_slash_index]
    return arn


def track_event(event_name: str, event_properties: dict):
    try:
        mac = uuid.getnode()
        id = hashlib.sha256(str(mac).encode())
        id.hexdigest()
        url = 'https://api.tensorfuse.io/tensorfuse/track/tensorkube-event/'

        body = {"id": id.hexdigest(), "event": event_name, "properties": event_properties}
        x = requests.post(url, json=body)
        click.echo(x.text)
    except Exception as e:
        click.echo(f"Error while tracking event: {e}")


def extract_workdir_from_dockerfile(dockerfile_path: str) -> Optional[str]:
    with open(dockerfile_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("WORKDIR"):
                return line.split(" ")[1].replace("\n", "")
    
    return None


def extract_command_from_dockerfile(dockerfile_path: str) -> Optional[str]:
    command = None
    with open(dockerfile_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("CMD") or line.startswith("ENTRYPOINT"):
                command = line.split(" ")[1:]
    
    if not command:
        return None
    
    command = " ".join(command)
    command = command.replace('[', "").replace(']', "").replace('"', '').replace(",", " ").replace("\n", "")
    return command
