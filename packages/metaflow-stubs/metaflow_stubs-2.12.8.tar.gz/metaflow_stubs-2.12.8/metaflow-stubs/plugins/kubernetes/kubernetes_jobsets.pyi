##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.12.8                                                             #
# Generated on 2024-07-16T15:51:55.438867                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.metaflow_current
    import metaflow.exception

current: metaflow.metaflow_current.Current

class MetaflowException(Exception, metaclass=type):
    def __init__(self, msg = "", lineno = None):
        ...
    def __str__(self):
        ...
    ...

UBF_CONTROL: str

UBF_TASK: str

KUBERNETES_JOBSET_GROUP: str

KUBERNETES_JOBSET_VERSION: str

class KubernetesJobsetException(metaflow.exception.MetaflowException, metaclass=type):
    ...

def k8s_retry(deadline_seconds = 60, max_backoff = 32):
    ...

class JobsetStatus(tuple, metaclass=type):
    @staticmethod
    def __new__(_cls, control_pod_failed, control_exit_code, control_pod_status, control_started, control_completed, worker_pods_failed, workers_are_suspended, workers_have_started, all_jobs_are_suspended, jobset_finished, jobset_failed, status_unknown, jobset_was_terminated, some_jobs_are_running):
        """
        Create new instance of JobsetStatus(control_pod_failed, control_exit_code, control_pod_status, control_started, control_completed, worker_pods_failed, workers_are_suspended, workers_have_started, all_jobs_are_suspended, jobset_finished, jobset_failed, status_unknown, jobset_was_terminated, some_jobs_are_running)
        """
        ...
    def __repr__(self):
        """
        Return a nicely formatted representation string
        """
        ...
    def __getnewargs__(self):
        """
        Return self as a plain tuple.  Used by copy and pickle.
        """
        ...
    ...

class RunningJobSet(object, metaclass=type):
    def __init__(self, client, name, namespace, group, version):
        ...
    def __repr__(self):
        ...
    def kill(self):
        ...
    @property
    def id(self):
        ...
    @property
    def is_done(self):
        ...
    @property
    def status(self):
        ...
    @property
    def has_succeeded(self):
        ...
    @property
    def has_failed(self):
        ...
    @property
    def is_running(self):
        ...
    @property
    def _jobset_was_terminated(self):
        ...
    @property
    def is_waiting(self):
        ...
    @property
    def reason(self):
        ...
    @property
    def _jobset_is_completed(self):
        ...
    @property
    def _jobset_has_failed(self):
        ...
    ...

class TaskIdConstructor(object, metaclass=type):
    @classmethod
    def jobset_worker_id(cls, control_task_id: str):
        ...
    @classmethod
    def join_step_task_ids(cls, num_parallel):
        """
        Called within the step decorator to set the `flow._control_mapper_tasks`.
        Setting these allows the flow to know which tasks are needed in the join step.
        We set this in the `task_pre_step` method of the decorator.
        """
        ...
    @classmethod
    def argo(cls):
        ...
    ...

def get_control_job(client, job_spec, jobset_main_addr, subdomain, port = None, num_parallel = None, namespace = None, annotations = None) -> dict:
    ...

def get_worker_job(client, job_spec, job_name, jobset_main_addr, subdomain, control_task_id = None, worker_task_id = None, replicas = 1, port = None, num_parallel = None, namespace = None, annotations = None) -> dict:
    ...

class KubernetesJobSet(object, metaclass=type):
    def __init__(self, client, name = None, job_spec = None, namespace = None, num_parallel = None, annotations = None, labels = None, port = None, task_id = None, **kwargs):
        ...
    def execute(self):
        ...
    ...

