##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.12.8                                                             #
# Generated on 2024-07-16T15:51:55.382046                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.metaflow_current
    import metaflow.exception

def namespace(ns: typing.Optional[str]) -> typing.Optional[str]:
    """
    Switch namespace to the one provided.
    
    This call has a global effect. No objects outside this namespace
    will be accessible. To access all objects regardless of namespaces,
    pass None to this call.
    
    Parameters
    ----------
    ns : str, optional
        Namespace to switch to or None to ignore namespaces.
    
    Returns
    -------
    str, optional
        Namespace set (result of get_namespace()).
    """
    ...

class CommandException(metaflow.exception.MetaflowException, metaclass=type):
    ...

class MetaflowException(Exception, metaclass=type):
    def __init__(self, msg = "", lineno = None):
        ...
    def __str__(self):
        ...
    ...

DECOSPECS: str

DEFAULT_DATASTORE: str

DEFAULT_ENVIRONMENT: str

DEFAULT_EVENT_LOGGER: str

DEFAULT_METADATA: str

DEFAULT_MONITOR: str

DEFAULT_PACKAGE_SUFFIXES: str

current: metaflow.metaflow_current.Current

LOG_SOURCES: list

DATASTORES: list

ENVIRONMENTS: list

LOGGING_SIDECARS: dict

METADATA_PROVIDERS: list

MONITOR_SIDECARS: dict

class PyLint(object, metaclass=type):
    def __init__(self, fname):
        ...
    def has_pylint(self):
        ...
    def run(self, logger = None, warnings = False, pylint_config = []):
        ...
    ...

def validate_tags(tags, existing_tags = None):
    """
    Raises MetaflowTaggingError if invalid based on these rules:
    
    Tag set size is too large. But it's OK if tag set is not larger
    than an existing tag set (if provided).
    
    Then, we validate each tag.  See validate_tag()
    """
    ...

UBF_CONTROL: str

UBF_TASK: str

ERASE_TO_EOL: str

HIGHLIGHT: str

INDENT: str

LOGGER_TIMESTAMP: str

LOGGER_COLOR: str

LOGGER_BAD_COLOR: str

def echo_dev_null(*args, **kwargs):
    ...

def echo_always(line, **kwargs):
    ...

def logger(body = "", system_msg = False, head = "", bad = False, timestamp = True, nl = True):
    ...

def config_merge_cb(ctx, param, value):
    ...

def common_run_options(func):
    ...

def write_file(file_path, content):
    ...

def before_run(obj, tags, decospecs):
    ...

def print_metaflow_exception(ex):
    ...

def print_unknown_exception(ex):
    ...

class CliState(object, metaclass=type):
    def __init__(self, flow):
        ...
    ...

def main(flow, args = None, handle_exceptions = True, entrypoint = None):
    ...

