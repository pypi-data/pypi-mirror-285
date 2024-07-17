##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.12.8                                                             #
# Generated on 2024-07-16T15:51:55.423253                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.decorators
    import metaflow.metaflow_current
    import metaflow.plugins.parallel_decorator

current: metaflow.metaflow_current.Current

class ParallelDecorator(metaflow.decorators.StepDecorator, metaclass=type):
    def __init__(self, attributes = None, statically_defined = False):
        ...
    def runtime_step_cli(self, cli_args, retry_count, max_user_code_retries, ubf_context):
        ...
    def step_init(self, flow, graph, step_name, decorators, environment, flow_datastore, logger):
        ...
    def task_decorate(self, step_func, flow, graph, retry_count, max_user_code_retries, ubf_context):
        ...
    def setup_distributed_env(self, flow):
        ...
    ...

class PytorchParallelDecorator(metaflow.plugins.parallel_decorator.ParallelDecorator, metaclass=type):
    def task_decorate(self, step_func, flow, graph, retry_count, max_user_code_retries, ubf_context):
        ...
    def setup_distributed_env(self, flow):
        ...
    ...

def setup_torch_distributed(master_port = None):
    """
    Set up environment variables for PyTorch's distributed (DDP).
    """
    ...

