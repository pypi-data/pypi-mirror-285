from tensorkube.services.s3_service import create_s3_bucket
from tensorkube.services.iam_service import create_mountpoint_iam_policy
from tensorkube.services.eks_service import create_eks_addon
from tensorkube.services.k8s_service import create_namespace, create_docker_registry_secret, apply_k8s_buildkit_config
from tensorkube.helpers import create_mountpoint_driver_role_with_policy, get_base64_encoded_docker_config
from tensorkube.constants import NAMESPACE, SERVICE_ACCOUNT_NAME
import os

account_no = "089962644720"
namespace = NAMESPACE
cluster_name = "shared-cluster-6"
region = "us-east-1"
bucket_name = "16114020-test-bucket-6"
mountpoint_policy_name = "16114020-mountpoint-test-policy-6"
mountpoint_driver_role_name = "16114020-mountpoint-test-role-6"
addon_name = "aws-mountpoint-s3-csi-driver"
service_account_name = SERVICE_ACCOUNT_NAME
args = [ "--context=dir:///data/fastapi_app",
            "--dockerfile=/data/fastapi_app/Dockerfile",
            "--destination=divtf/kaniko-test-1:v5"]

if namespace not in ["default", "kube-system"]:
    create_namespace(namespace)

# # NOTE: bucket name must be universally unique
# # NOTE: bucket name should not be guessable
print(create_s3_bucket(bucket_name, region))

# print(upload_folder_to_bucket(bucket_name,
#                               "/Users/divys/Documents/tensorfuse-all/testing/fastapi_app/",
#                               region=region,
#                               s3_path="fastapi_app/"))


print(create_mountpoint_iam_policy(mountpoint_policy_name, bucket_name, region=region))


print(create_mountpoint_driver_role_with_policy(cluster_name, account_no, mountpoint_driver_role_name, mountpoint_policy_name, service_account_name, namespace, region))

print(create_eks_addon(cluster_name, addon_name, account_no, mountpoint_driver_role_name, region))

DOCKER_USERNAME = os.evniron.get("DOCKER_USERNAME")
DOCKER_PASSWORD = os.evniron.get("DOCKER_PASSWORD")
DOCKER_EMAIL = os.evniron.get("DOCKER_EMAIL")
base64_encoded_docker_config = get_base64_encoded_docker_config(DOCKER_USERNAME, DOCKER_PASSWORD, DOCKER_EMAIL)

create_docker_registry_secret("dockerhub-creds", namespace, base64_encoded_docker_config)

# apply_k8s_buildkit_config("test", "test", bucket_name, get_aws_account_id(), ecr_repo_url)
