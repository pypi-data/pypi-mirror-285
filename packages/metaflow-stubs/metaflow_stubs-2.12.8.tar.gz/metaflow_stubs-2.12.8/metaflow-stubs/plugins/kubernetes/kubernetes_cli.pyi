##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.12.8                                                             #
# Generated on 2024-07-16T15:51:55.444012                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow._vendor.click.types
    import metaflow.decorators
    import metaflow.exception

class JSONTypeClass(metaflow._vendor.click.types.ParamType, metaclass=type):
    def convert(self, value, param, ctx):
        ...
    def __str__(self):
        ...
    def __repr__(self):
        ...
    ...

METAFLOW_EXIT_DISALLOW_RETRY: int

class CommandException(metaflow.exception.MetaflowException, metaclass=type):
    ...

def sync_local_metadata_from_datastore(metadata_local_dir, task_ds):
    ...

UBF_CONTROL: str

UBF_TASK: str

DATASTORE_LOCAL_DIR: str

KUBERNETES_LABELS: str

TASK_LOG_SOURCE: str

class Kubernetes(object, metaclass=type):
    def __init__(self, datastore, metadata, environment):
        ...
    def launch_job(self, **kwargs):
        ...
    def create_jobset(self, job_spec = None, run_id = None, step_name = None, task_id = None, namespace = None, env = None, num_parallel = None, port = None, annotations = None, labels = None):
        ...
    def create_job_object(self, flow_name, run_id, step_name, task_id, attempt, user, code_package_sha, code_package_url, code_package_ds, step_cli, docker_image, docker_image_pull_policy, service_account = None, secrets = None, node_selector = None, namespace = None, cpu = None, gpu = None, gpu_vendor = None, disk = None, memory = None, use_tmpfs = None, tmpfs_tempdir = None, tmpfs_size = None, tmpfs_path = None, run_time_limit = None, env = None, persistent_volume_claims = None, tolerations = None, labels = None, shared_memory = None, port = None, name_pattern = None, num_parallel = None):
        ...
    def create_k8sjob(self, job):
        ...
    def wait(self, stdout_location, stderr_location, echo = None):
        ...
    ...

class KubernetesKilledException(metaflow.exception.MetaflowException, metaclass=type):
    ...

def parse_kube_keyvalue_list(items: typing.List[str], requires_both: bool = True):
    ...

class KubernetesException(metaflow.exception.MetaflowException, metaclass=type):
    ...

class KubernetesDecorator(metaflow.decorators.StepDecorator, metaclass=type):
    def __init__(self, attributes = None, statically_defined = False):
        ...
    def step_init(self, flow, graph, step, decos, environment, flow_datastore, logger):
        ...
    def package_init(self, flow, step_name, environment):
        ...
    def runtime_init(self, flow, graph, package, run_id):
        ...
    def runtime_task_created(self, task_datastore, task_id, split_index, input_paths, is_cloned, ubf_context):
        ...
    def runtime_step_cli(self, cli_args, retry_count, max_user_code_retries, ubf_context):
        ...
    def task_pre_step(self, step_name, task_datastore, metadata, run_id, task_id, flow, graph, retry_count, max_retries, ubf_context, inputs):
        ...
    def task_finished(self, step_name, flow, graph, is_task_ok, retry_count, max_retries):
        ...
    ...

