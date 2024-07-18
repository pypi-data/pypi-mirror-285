import time
from threading import Thread
from typing import List

import click
import yaml
from kubernetes import client, config, utils, watch
from kubernetes.client import ApiTypeError, ApiException
from pkg_resources import resource_filename

from tensorkube.constants import NAMESPACE, REGION, PodStatus, BUILD_TOOL, DEFAULT_NAMESPACE


def create_namespace(namespace_name):
    config.load_kube_config()
    namespace = client.V1Namespace()
    namespace.metadata = client.V1ObjectMeta(name=namespace_name)
    v1 = client.CoreV1Api()
    v1.create_namespace(body=namespace)


def create_docker_registry_secret(secret_name: str, namespace: str, base64_encoded_dockerconfigjson: str):
    config.load_kube_config()
    v1 = client.CoreV1Api()

    secret = client.V1Secret()
    secret.api_version = "v1"
    secret.kind = "Secret"
    secret.metadata = client.V1ObjectMeta(name=secret_name, namespace=namespace)
    secret.type = "kubernetes.io/dockerconfigjson"
    secret.data = {".dockerconfigjson": base64_encoded_dockerconfigjson}

    v1.create_namespaced_secret(namespace=namespace, body=secret)


def create_aws_secret(credentials, namespace: str = DEFAULT_NAMESPACE):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    secret_name = "aws-secret"

    secret = client.V1Secret()
    secret.metadata = client.V1ObjectMeta(name=secret_name)
    secret.string_data = {"AWS_ACCESS_KEY_ID": credentials.access_key, "AWS_SECRET_ACCESS_KEY": credentials.secret_key,
                          "AWS_SESSION_TOKEN": credentials.token}

    try:
        # Check if the secret already exists
        existing_secret = v1.read_namespaced_secret(name=secret_name, namespace=namespace)
        # If the secret exists, update it
        v1.replace_namespaced_secret(name=secret_name, namespace=namespace, body=secret)
        print(f"Secret {secret_name} updated successfully in namespace {namespace}.")
    except ApiException as e:
        if e.status == 404:
            # Secret does not exist, create it
            v1.create_namespaced_secret(namespace=namespace, body=secret)
            print(f"Secret {secret_name} created successfully in namespace {namespace}.")
        else:
            print(f"An error occurred: {e}")
            raise e


def delete_aws_secret(namespace: str = DEFAULT_NAMESPACE):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    try:
        v1.read_namespaced_secret(name="aws-secret", namespace=namespace)
    except client.ApiException as e:
        if e.status == 404:
            return
        else:
            raise
    v1.delete_namespaced_secret(name="aws-secret", namespace=namespace)


def create_build_pv_and_pvc(bucket_name: str, namespace: str = DEFAULT_NAMESPACE, region: str = REGION):
    config.load_kube_config()

    pv_config_file_path = resource_filename('tensorkube', 'configurations/build_configs/pv.yaml')
    pvc_config_file_path = resource_filename('tensorkube', 'configurations/build_configs/pvc.yaml')
    with open(pv_config_file_path) as f:
        pv = yaml.safe_load(f)
    with open(pvc_config_file_path) as f:
        pvc = yaml.safe_load(f)

    pv['spec']['mountOptions'] = ["allow-delete", "region {}".format(region)]
    pv['spec']['csi']['volumeAttributes']['bucketName'] = bucket_name
    pv['metadata']['namespace'] = namespace

    pvc['metadata']['namespace'] = namespace

    k8s_client = client.ApiClient()
    v1 = client.CoreV1Api()

    pv_name = pv['metadata']['name']
    pvc_name = pvc['metadata']['name']

    try:
        # Check if the PV already exists
        v1.read_persistent_volume(name=pv_name)
        print(f"PersistentVolume {pv_name} already exists. Skipping creation.")
    except ApiException as e:
        if e.status == 404:
            utils.create_from_dict(k8s_client, pv)
            print(f"PersistentVolume {pv_name} created successfully.")
        else:
            print(f"An error occurred while checking PersistentVolume: {e}")
            raise e

    try:
        # Check if the PVC already exists
        v1.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=namespace)
        print(f"PersistentVolumeClaim {pvc_name} already exists in namespace {namespace}. Skipping creation.")
    except ApiException as e:
        if e.status == 404:
            # PVC does not exist, proceed to create
            k8s_client = client.ApiClient()
            utils.create_from_dict(k8s_client, pvc)
            print(f"PersistentVolumeClaim {pvc_name} created successfully in namespace {namespace}.")
        else:
            print(f"An error occurred while checking PersistentVolumeClaim: {e}")
            raise e


def apply_k8s_buildkit_config(sanitised_project_name: str, image_tag: str, region: str = REGION):
    config.load_kube_config()

    buildkit_config_file_path = resource_filename('tensorkube', 'configurations/build_configs/buildkit.yaml')
    with open(buildkit_config_file_path) as f:
        buildkit_config = yaml.safe_load(f)

    buildkit_config['metadata']['name'] = 'buildkit-{}'.format(sanitised_project_name)
    buildkit_config['spec']['template']['spec']['containers'][0]['env'][0]['value'] = region

    buildkit_config['spec']['template']['spec']['containers'][0]['command'] = ["/bin/sh", "-c", f"""
        mkdir -p /data/cache
        mkdir -p /test/tars/{sanitised_project_name} /mnt/efs/images/{sanitised_project_name}/{image_tag}/rootfs /test/tars/{sanitised_project_name} /test/images/{sanitised_project_name}/rootfs
        time buildctl-daemonless.sh build\
            --frontend dockerfile.v0\
            --local context=/data/build/{sanitised_project_name}\
            --local dockerfile=/data/build/{sanitised_project_name}\
            --output type=tar,dest=/test/tars/{sanitised_project_name}/{sanitised_project_name}-{image_tag}.tar
        echo "Extracting rootfs from tar file"
        time tar -xf /test/tars/{sanitised_project_name}/{sanitised_project_name}-{image_tag}.tar -C /test/images/{sanitised_project_name}/rootfs --checkpoint=1000 --checkpoint-action=echo="Extracted #%u: %T"
        echo "Extracted rootfs from tar file"
        echo "Uploading rootfs to NFS"
        cd /test/images/{sanitised_project_name}/rootfs
        find . -type d | split -l 5000 - batch_dir_
        find . -type f | split -l 5000 - batch_file_
        find . -type l | split -l 5000 - batch_link_

        total_batches=$(ls batch_* | wc -l)
        processed_batches=0
        total_time=0

        process_batches() {{
            local batch_type=$1
            for batch_file in batch_${{batch_type}}_*; do
                start_time=$(date +%s)
                
                if [ "$batch_type" == "dir" ]; then
                    cat $batch_file | parallel -j 15 mkdir -p /mnt/efs/images/{sanitised_project_name}/{image_tag}/rootfs/{{}}
                elif [ "$batch_type" == "file" ]; then
                    cat $batch_file | parallel -j 15 cp --parents {{}} /mnt/efs/images/{sanitised_project_name}/{image_tag}/rootfs/
                elif [ "$batch_type" == "link" ]; then
                    cat $batch_file | parallel -j 15 cp --parents -P {{}} /mnt/efs/images/{sanitised_project_name}/{image_tag}/rootfs/
                fi
                
                end_time=$(date +%s)
                batch_time=$((end_time - start_time))
                total_time=$((total_time + batch_time))
                processed_batches=$((processed_batches + 1))
                remaining_batches=$((total_batches - processed_batches))
                avg_time_per_batch=$((total_time / processed_batches))
                estimated_remaining_time=$((avg_time_per_batch * remaining_batches))
                
                echo "Processed batch $processed_batches/$total_batches. Remaining: $remaining_batches. Time for this batch: $batch_time seconds. Estimated remaining time: $estimated_remaining_time seconds."
                rm $batch_file
            done
        }}

        process_batches "dir"
        process_batches "file"
        process_batches "link"
        echo "Uploaded rootfs to NFS" """]

    k8s_client = client.ApiClient()
    utils.create_from_dict(k8s_client, buildkit_config)
    click.echo('Deployed a Buildkit image')


def apply_image_cleanup_job(sanitised_project_name: str, image_tags: List[str]):
    config.load_kube_config()

    cleanup_config_file_path = resource_filename('tensorkube', 'configurations/build_configs/efs_cleanup_pod.yaml')
    with open(cleanup_config_file_path) as f:
        cleanup_config = yaml.safe_load(f)
    cleanup_config['metadata']['name'] = 'cleanup-{}'.format(sanitised_project_name)
    cleanup_config['spec']['template']['spec']['containers'][0]['command'] = ["/bin/sh", "-c"]
    cleanup_config['spec']['template']['spec']['containers'][0]['args'] = [" && ".join(
        [f"echo 'Deleting image tag {tag}' && rm -rf /mnt/efs/images/{sanitised_project_name}/{tag}" for tag in
         image_tags] + ["echo 'Deletion completed'"])]
    k8s_client = client.ApiClient()
    utils.create_from_dict(k8s_client, cleanup_config)
    click.echo('Deployed a delete config job')


def get_build_job_pod_name(sanitised_project_name: str, namespace: str = NAMESPACE):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace=namespace)
    for pod in pods.items:
        if pod.metadata.name.startswith("{}-{}".format(BUILD_TOOL, sanitised_project_name)):
            return pod.metadata.name
    return None


def check_pod_status(pod_name, namespace):
    # Load kube config
    config.load_kube_config()

    # Create a Kubernetes API client
    v1 = client.CoreV1Api()

    # Get the status of the pod
    pod_status = v1.read_namespaced_pod_status(name=pod_name, namespace=namespace)

    # Return the status of the pod
    return pod_status.status.phase


def find_and_delete_old_build_job(job_name: str, namespace: str = DEFAULT_NAMESPACE):
    config.load_kube_config()
    v1 = client.BatchV1Api()
    jobs = v1.list_namespaced_job(namespace=namespace)
    for job in jobs.items:
        if job.metadata.name == job_name:
            v1.delete_namespaced_job(name=job.metadata.name, namespace=namespace)
            return True

    return True


def start_streaming_pod(pod_name, namespace, status=None, container_name=None):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    # Create a stream to the pod
    # Initialize the Watch class
    watch_client = watch.Watch()
    # Stream events until the pod is ready
    print(f"Streaming events for pod {pod_name} in namespace {namespace}")
    for event in watch_client.stream(v1.list_namespaced_event, namespace=namespace):
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        if event['object'].involved_object.kind == 'Pod' and event['object'].involved_object.name == pod_name:
            print("Event: %s %s" % (event['type'], event['object'].message))
        if pod.status.phase != 'Pending':
            break

    print(f"Streaming logs for pod {pod_name} in namespace {namespace}")

    try:
        for event in watch_client.stream(v1.read_namespaced_pod_log, name=pod_name, namespace=namespace, follow=True,
                                         container=container_name):
            click.echo(event)
            if status:
                pod = v1.read_namespaced_pod_status(name=pod_name, namespace=namespace)
                if status.value == pod.status.phase:
                    print(f"Pod {pod_name} has reached {status.value} state")
                    return
    except client.ApiException as e:
        if e.status == 404:
            print(f"Pod {pod_name} not found in namespace {namespace}")
        else:
            raise
    except KeyboardInterrupt:
        print("Log streaming stopped by user")
        return
    except ApiTypeError as e:
        print(f"An error occurred while streaming logs for pod {pod_name} in namespace {namespace}")
        print(e)
        return
    except Exception as e:
        print(f"An unexpected error occurred for pod {pod_name} in namespace {namespace}")
        print(e)
        raise


def start_streaming_service(service_name, namespace):
    # Load kube config
    config.load_kube_config()

    # Create a Kubernetes API client
    v1 = client.CoreV1Api()

    # Stream the service status
    try:
        while True:
            pods = v1.list_namespaced_pod(namespace, label_selector=f'serving.knative.dev/service={service_name}')
            if pods.items:
                print(f"Pods scheduled for service {service_name}: {[pod.metadata.name for pod in pods.items]}")
                break
            time.sleep(5)
        # Start streaming the logs from the pod
        for pod in pods.items:
            thread = Thread(target=start_streaming_pod,
                            args=(pod.metadata.name, namespace, PodStatus.RUNNING, 'user-container'))
            thread.start()
    except client.ApiException as e:
        if e.status == 404:
            print(f"Service {service_name} not found in namespace {namespace}")
        else:
            raise
    except KeyboardInterrupt:
        print("Service status streaming stopped by user")
        return
    except Exception as e:
        print("An unexpected error occurred for service status streaming")
        raise


def check_nodes_ready(label_selector):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    ready_nodes = []
    nodes = v1.list_node(label_selector=label_selector).items
    for node in nodes:
        for condition in node.status.conditions:
            if condition.type == "Ready" and condition.status == "True":
                ready_nodes.append(node.metadata.name)
    return len(ready_nodes) == len(nodes), ready_nodes


def evict_pods_from_node(node_name):
    config.load_kube_config()
    core_api = client.CoreV1Api()
    pods = core_api.list_pod_for_all_namespaces(field_selector=f'spec.nodeName={node_name}').items
    for pod in pods:
        if pod.metadata.owner_references and any(owner.kind == "DaemonSet" for owner in pod.metadata.owner_references):
            continue
        eviction = client.V1Eviction(
            metadata=client.V1ObjectMeta(name=pod.metadata.name, namespace=pod.metadata.namespace))
        retry_attempts = 0
        max_retries = 5
        backoff_delay = 1  # Start with 1 second delay
        while retry_attempts < max_retries:
            try:
                core_api.create_namespaced_pod_eviction(name=pod.metadata.name, namespace=pod.metadata.namespace,
                                                        body=eviction)
                print(f"Evicting pod {pod.metadata.name} from node {node_name}.")
                break  # Eviction successful, break out of the retry loop
            except ApiException as e:
                if e.status == 429:  # Too Many Requests
                    print(
                        f"Rate limit exceeded when evicting pod {pod.metadata.name}: {e}. Retrying in {backoff_delay} seconds...")
                    time.sleep(backoff_delay)
                    backoff_delay *= 2  # Exponential backoff
                    retry_attempts += 1
                else:
                    print(f"Exception when evicting pod {pod.metadata.name}: {e}")
                    break  # Break on any other exception
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break
        if retry_attempts == max_retries:
            print(f"Failed to evict pod {pod.metadata.name} after {max_retries} attempts.")


def drain_and_delete_node(node_name):
    core_api = client.CoreV1Api()
    # Cordon the node
    body = {"spec": {"unschedulable": True}}
    core_api.patch_node(node_name, body)
    click.echo(f"Cordoned node {node_name}")

    # Evict all pods from the node
    evict_pods_from_node(node_name)
    click.echo(f"All pods evicted from node {node_name}")

    # delete the node
    core_api.delete_node(node_name)


def get_nodes_not_using_bottlerocket(ec2_node_class_label):
    config.load_kube_config()
    v1 = client.CoreV1Api()

    # List all nodes
    nodes = v1.list_node().items

    filtered_nodes = []
    for node in nodes:
        labels = node.metadata.labels
        os_image = node.status.node_info.os_image

        # Check if the node belongs to the specified EC2NodeClass
        if labels.get('karpenter.sh/nodepool') == ec2_node_class_label:
            # Check if the node is using Bottlerocket AMI
            if 'bottlerocket' not in os_image.lower():
                filtered_nodes.append(node.metadata.name)

    return filtered_nodes


def delete_pv_using_name(pv_name: str):
    config.load_kube_config()
    v1 = client.CoreV1Api()

    timeout = 60  # Timeout in seconds
    start_time = time.time()

    try:
        v1.delete_persistent_volume(name=pv_name)
        while time.time() - start_time < timeout:
            try:
                v1.read_persistent_volume(name=pv_name)
                print(f"Waiting for PV {pv_name} to be deleted...")
                time.sleep(5)  # Wait for 5 seconds before checking again
            except ApiException as e:
                if e.status == 404:
                    print(f"PersistentVolume {pv_name} successfully deleted.")
                    return
                else:
                    raise
        print(f"Timeout reached while waiting for PV {pv_name} to be deleted.")
    except client.exceptions.ApiException as e:
        if e.status == 404:
            print(f"PersistentVolume {pv_name} not found")
        else:
            raise e


def delete_pvc_using_name_and_namespace(pvc_name: str, namespace: str):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    timeout = 60  # Timeout in seconds
    start_time = time.time()
    try:
        v1.delete_namespaced_persistent_volume_claim(name=pvc_name, namespace=namespace)
        while time.time() - start_time < timeout:
            try:
                v1.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=namespace)
                print(f"Waiting for PVC {pvc_name} to be deleted...")
                time.sleep(5)  # Wait for 5 seconds before checking again
            except ApiException as e:
                if e.status == 404:
                    print(f"PersistentVolumeClaim {pvc_name} successfully deleted from namespace {namespace}.")
                    return
                else:
                    raise
        print(f"Timeout reached while waiting for PVC {pvc_name} to be deleted.")
    except client.exceptions.ApiException as e:
        if e.status == 404:
            print(f"PersistentVolumeClaim {pvc_name} not found in namespace {namespace}")
        else:
            raise e


def check_pvc_exists_by_name(claim_name, namespace):
    # Load the Kubernetes configuration
    config.load_kube_config()

    # Create an instance of the CoreV1Api
    v1 = client.CoreV1Api()

    try:
        # Attempt to read the specified PVC in the given namespace
        v1.read_namespaced_persistent_volume_claim(name=claim_name, namespace=namespace)
        return True  # PVC exists
    except ApiException as e:
        if e.status == 404:
            return False  # PVC does not exist
        else:
            print(f"An error occurred: {e}")
            raise e


def get_image_tags_to_delete(sanitised_project_name: str, service_name: str, namespace: str):
    config.load_kube_config()
    k8s_client = client.CustomObjectsApi()
    click.echo(f"Cleaning up old image tags for project {sanitised_project_name}, service {service_name}.")
    group = "serving.knative.dev"
    version = "v1"
    plural = "revisions"

    # List all revisions for the service
    # Define the label selector string based on the service name
    label_selector = f"serving.knative.dev/service={service_name}"

    # Use the label selector in the list_namespaced_custom_object call to directly filter revisions
    service_revisions = \
        k8s_client.list_namespaced_custom_object(group, version, namespace, plural, label_selector=label_selector)[
            'items']

    # Sort all revisions by configurationGeneration in descending order
    all_revisions_sorted = sorted(service_revisions, key=lambda x: int(
        x['metadata']['labels']['serving.knative.dev/configurationGeneration']), reverse=True)

    # Identify all "Ready" revisions
    ready_revisions = [rev for rev in all_revisions_sorted if any(
        cond['type'] == 'Ready' and cond['status'] == 'True' for cond in rev['status']['conditions'])]

    # Find the index of the latest "Ready" revision
    if ready_revisions:
        latest_ready_revision = ready_revisions[0]
        latest_ready_index = all_revisions_sorted.index(latest_ready_revision)
    else:
        latest_ready_index = -1

    # Determine active revisions
    active_revisions = ready_revisions[:3]  # Last three "Ready" revisions
    if latest_ready_index != -1:
        active_revisions += all_revisions_sorted[:latest_ready_index]  # Any newer revisions

    # Find the index for slicing stale revisions
    if len(ready_revisions) >= 3:
        third_last_ready_index = all_revisions_sorted.index(ready_revisions[2])
    else:
        third_last_ready_index = latest_ready_index

    # Determine stale revisions, ensuring last three "Ready" revisions are not included
    stale_revisions = all_revisions_sorted[third_last_ready_index + 1:] if third_last_ready_index != -1 else []

    image_tags_to_delete = []

    for rev in stale_revisions:
        # check if this exists yaml_dict['spec']['template']['metadata']['annotations']['image_tag'] = image_tag
        if rev['metadata']['annotations'] and 'image_tag' in rev['metadata']['annotations']:
            image_tags_to_delete.append(rev['metadata']['annotations']['image_tag'])
            click.echo(f'Queuing revision {rev["metadata"]["name"]} for deletion')
        else:
            print(f'No image tag found for revision {rev["metadata"]["name"]}')
        try:
            # Delete the revision
            k8s_client.delete_namespaced_custom_object(group=group, version=version, namespace=namespace, plural=plural,
                                                       name=rev['metadata']['name'], body=client.V1DeleteOptions()
                                                       # You can customize this if needed
                                                       )
        except client.exceptions.ApiException as e:
            print(f"Failed to delete revision {rev['metadata']['name']}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while deleting revision {rev['metadata']['name']}: {e}")

    return image_tags_to_delete
