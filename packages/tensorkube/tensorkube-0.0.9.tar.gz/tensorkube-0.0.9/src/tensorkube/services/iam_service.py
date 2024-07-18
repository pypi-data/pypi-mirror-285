import json

import boto3
from botocore.exceptions import ClientError
from pkg_resources import resource_filename

from tensorkube.constants import REGION


def create_mountpoint_iam_policy(policy_name, bucket_name, region=REGION):
    policy_file_path = resource_filename('tensorkube', 'configurations/aws_configs/mountpoint_policy.json')
    with open(policy_file_path, 'r') as f:
        policy = json.load(f)
    for statement in policy['Statement']:
        statement['Resource'] = [r.replace('USER_BUCKET', bucket_name) for r in statement['Resource']]

    iam = boto3.client('iam', region_name=region)
    sts = boto3.client('sts')
    try:
        # Check if the IAM policy already exists
        account_id = sts.get_caller_identity()['Account']
        policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
        iam.get_policy(PolicyArn=policy_arn)
        print(f"IAM policy {policy_name} already exists. Skipping creation.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print(f"IAM policy {policy_name} does not exist. Proceeding with creation.")
            response = iam.create_policy(PolicyName=policy_name, PolicyDocument=json.dumps(policy), )
            print(f"IAM policy {policy_name} created successfully.")
            return response
        else:
            print(f"An error occurred: {e}")
            raise e


def create_s3_csi_driver_role(account_no: str, role_name: str, oidc_issuer_url: str, namespace: str,
                              service_account_name: str):
    oidc_issuer = oidc_issuer_url[8:]
    region = oidc_issuer.split('.')[2]
    trust_policy_file_path = resource_filename('tensorkube',
                                               'configurations/aws_configs/aws_s3_csi_driver_trust_policy.json')
    with open(trust_policy_file_path, 'r') as f:
        trust_policy = json.load(f)
    trust_policy['Statement'][0]['Principal']['Federated'] = 'arn:aws:iam::{}:oidc-provider/{}'.format(account_no,
                                                                                                       oidc_issuer)
    trust_policy['Statement'][0]['Condition']['StringEquals'] = {
        "{}:sub".format(oidc_issuer): "system:serviceaccount:{}:{}".format(namespace, service_account_name),
        "{}:aud".format(oidc_issuer): "sts.amazonaws.com"}

    iam = boto3.client('iam', region_name=region)

    try:
        # Check if the IAM role already exists
        iam.get_role(RoleName=role_name)
        print(f"IAM role {role_name} already exists. Skipping creation.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print(f"IAM role {role_name} does not exist. Proceeding with creation.")
            response = iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy), )
            print(f"IAM role {role_name} created successfully.")
            return response
        else:
            print(f"An error occurred: {e}")
            raise e


def attach_role_policy(account_no, policy_name, role_name, region=REGION):
    client = boto3.client('iam', region_name=region)
    response = client.attach_role_policy(PolicyArn='arn:aws:iam::{}:policy/{}'.format(account_no, policy_name),
                                         RoleName=role_name, )
    return response


def detach_role_policy(account_no, role_name, policy_name, region=REGION):
    client = boto3.client('iam', region_name=region)
    response = client.detach_role_policy(PolicyArn='arn:aws:iam::{}:policy/{}'.format(account_no, policy_name),
                                         RoleName=role_name, )
    return response


def delete_role(role_name, region=REGION):
    client = boto3.client('iam', region_name=region)
    response = client.delete_role(RoleName=role_name)
    return response


def delete_policy(account_no, policy_name, region=REGION):
    client = boto3.client('iam', region_name=region)
    response = client.delete_policy(PolicyArn='arn:aws:iam::{}:policy/{}'.format(account_no, policy_name))
    return response


def delete_iam_role(role_name):
    iam_client = boto3.client('iam')
    attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']

    # Detach policies
    for policy in attached_policies:
        iam_client.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
        print(f"Detached policy {policy['PolicyArn']} from role {role_name}")

    # Delete the role
    iam_client.delete_role(RoleName=role_name)
    print(f"IAM Role {role_name} deleted")
