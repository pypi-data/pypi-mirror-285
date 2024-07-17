##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.12.8                                                             #
# Generated on 2024-07-16T15:51:55.420993                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.decorators

EXT_PKG: str

class MetaDatum(tuple, metaclass=type):
    @staticmethod
    def __new__(_cls, field, value, type, tags):
        """
        Create new instance of MetaDatum(field, value, type, tags)
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

INFO_FILE: str

class CondaStepDecorator(metaflow.decorators.StepDecorator, metaclass=type):
    def __init__(self, attributes = None, statically_defined = False):
        ...
    def step_init(self, flow, graph, step, decos, environment, flow_datastore, logger):
        ...
    def runtime_init(self, flow, graph, package, run_id):
        ...
    def runtime_task_created(self, task_datastore, task_id, split_index, input_paths, is_cloned, ubf_context):
        ...
    def task_pre_step(self, step_name, task_datastore, meta, run_id, task_id, flow, graph, retry_count, max_retries, ubf_context, inputs):
        ...
    def runtime_step_cli(self, cli_args, retry_count, max_user_code_retries, ubf_context):
        ...
    def runtime_finished(self, exception):
        ...
    ...

class CondaFlowDecorator(metaflow.decorators.FlowDecorator, metaclass=type):
    def __init__(self, attributes = None, statically_defined = False):
        ...
    def flow_init(self, flow, graph, environment, flow_datastore, metadata, logger, echo, options):
        ...
    ...

