import platform
import subprocess
import uuid

import boto3
import botocore

from tensorkube.constants import get_cluster_name
from tensorkube.services.s3_service import list_s3_buckets


def get_eks_client():
    return boto3.client("eks")


def get_cloudformation_client():
    return boto3.client("cloudformation")


def get_ec2_client():
    return boto3.client("ec2")


def get_iam_client():
    return boto3.client("iam")


def get_aws_account_id():
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    return identity['Account']


def get_aws_user_arn() -> str:
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    return identity['Arn']


def get_karpenter_namespace():
    return "kube-system"


def get_karpenter_version():
    return "0.37.0"


def get_aws_default_region():
    return "us-east-1"


def get_kubernetes_context_name():
    return f"{get_cluster_name()}.{get_aws_default_region()}.eksctl.io"


def check_and_install_aws_cli():
    """Check if aws cli is installed and if not install it."""
    try:
        subprocess.run(["aws", "--version"], check=True)
    except Exception as e:
        # check if the operating system is mac and install aws cli
        if platform.system() == "Darwin":
            try:
                subprocess.run(["brew", "install", "awscli"])
            except Exception as e:
                print("Unable to install aws cli. Please install aws cli manually.")


def get_credentials():
    return boto3.Session().get_credentials().get_frozen_credentials()


def are_credentials_valid(credentials):
    sts = boto3.client('sts', aws_access_key_id=credentials.access_key, aws_secret_access_key=credentials.secret_key,
                       aws_session_token=credentials.token)
    try:
        sts.get_caller_identity()
        return True
    except botocore.exceptions.ClientError as e:
        return False


# TODO!: make function generic to get any config value
def get_bucket_name():
    buckets = list_s3_buckets()
    for bucket in buckets:
        if bucket['Name'].startswith(f'{get_cluster_name()}-build-bucket-'):
            return bucket['Name']
    else:
        bucket_name = f"{get_cluster_name()}-build-bucket-{uuid.uuid4()}"
        return bucket_name
