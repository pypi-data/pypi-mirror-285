##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.12.8                                                             #
# Generated on 2024-07-16T15:51:55.378633                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.runner.metaflow_runner

class Runner(object, metaclass=type):
    def __init__(self, flow_file: str, show_output: bool = True, profile: typing.Optional[str] = None, env: typing.Optional[typing.Dict] = None, cwd: typing.Optional[str] = None, **kwargs):
        ...
    def __enter__(self) -> metaflow.runner.metaflow_runner.Runner:
        ...
    def __aenter__(self) -> metaflow.runner.metaflow_runner.Runner:
        ...
    def _Runner__get_executing_run(self, tfp_runner_attribute, command_obj):
        ...
    def run(self, **kwargs) -> metaflow.runner.metaflow_runner.ExecutingRun:
        """
        Blocking execution of the run. This method will wait until
        the run has completed execution.
        
        Parameters
        ----------
        **kwargs : Any
            Additional arguments that you would pass to `python myflow.py` after
            the `run` command, in particular, any parameters accepted by the flow.
        
        Returns
        -------
        ExecutingRun
            ExecutingRun containing the results of the run.
        """
        ...
    def resume(self, **kwargs):
        """
        Blocking resume execution of the run.
        This method will wait until the resumed run has completed execution.
        
        Parameters
        ----------
        **kwargs : Any
            Additional arguments that you would pass to `python ./myflow.py` after
            the `resume` command.
        
        Returns
        -------
        ExecutingRun
            ExecutingRun containing the results of the resumed run.
        """
        ...
    def async_run(self, **kwargs) -> metaflow.runner.metaflow_runner.ExecutingRun:
        """
        Non-blocking execution of the run. This method will return as soon as the
        run has launched.
        
        Note that this method is asynchronous and needs to be `await`ed.
        
        Parameters
        ----------
        **kwargs : Any
            Additional arguments that you would pass to `python myflow.py` after
            the `run` command, in particular, any parameters accepted by the flow.
        
        Returns
        -------
        ExecutingRun
            ExecutingRun representing the run that was started.
        """
        ...
    def async_resume(self, **kwargs):
        """
        Non-blocking resume execution of the run.
        This method will return as soon as the resume has launched.
        
        Note that this method is asynchronous and needs to be `await`ed.
        
        Parameters
        ----------
        **kwargs : Any
            Additional arguments that you would pass to `python myflow.py` after
            the `resume` command.
        
        Returns
        -------
        ExecutingRun
            ExecutingRun representing the resumed run that was started.
        """
        ...
    def __exit__(self, exc_type, exc_value, traceback):
        ...
    def __aexit__(self, exc_type, exc_value, traceback):
        ...
    def cleanup(self):
        """
        Delete any temporary files created during execution.
        """
        ...
    ...

DEFAULT_DIR: str

class NBRunnerInitializationError(Exception, metaclass=type):
    ...

def get_current_cell(ipython):
    ...

def format_flowfile(cell):
    """
    Formats the given cell content to create a valid Python script that can be executed as a Metaflow flow.
    """
    ...

class NBRunner(object, metaclass=type):
    def __init__(self, flow, show_output: bool = True, profile: typing.Optional[str] = None, env: typing.Optional[typing.Dict] = None, base_dir: str = "/tmp", **kwargs):
        ...
    def nbrun(self, **kwargs):
        """
        Blocking execution of the run. This method will wait until
        the run has completed execution.
        
        Note that in contrast to `run`, this method returns a
        `metaflow.Run` object directly and calls `cleanup()` internally
        to support a common notebook pattern of executing a flow and
        retrieving its results immediately.
        
        Parameters
        ----------
        **kwargs : Any
            Additional arguments that you would pass to `python myflow.py` after
            the `run` command, in particular, any parameters accepted by the flow.
        
        Returns
        -------
        Run
            A `metaflow.Run` object representing the finished run.
        """
        ...
    def nbresume(self, **kwargs):
        """
        Blocking resuming of a run. This method will wait until
        the resumed run has completed execution.
        
        Note that in contrast to `resume`, this method returns a
        `metaflow.Run` object directly and calls `cleanup()` internally
        to support a common notebook pattern of executing a flow and
        retrieving its results immediately.
        
        Parameters
        ----------
        **kwargs : Any
            Additional arguments that you would pass to `python myflow.py` after
            the `resume` command.
        
        Returns
        -------
        Run
            A `metaflow.Run` object representing the resumed run.
        """
        ...
    def run(self, **kwargs):
        """
        Runs the flow.
        """
        ...
    def resume(self, **kwargs):
        """
        Resumes the flow.
        """
        ...
    def async_run(self, **kwargs):
        """
        Non-blocking execution of the run. This method will return as soon as the
        run has launched. This method is equivalent to `Runner.async_run`.
        
        Note that this method is asynchronous and needs to be `await`ed.
        
        
        Parameters
        ----------
        **kwargs : Any
            Additional arguments that you would pass to `python myflow.py` after
            the `run` command, in particular, any parameters accepted by the flow.
        
        Returns
        -------
        ExecutingRun
            ExecutingRun representing the run that was started.
        """
        ...
    def async_resume(self, **kwargs):
        """
        Non-blocking execution of the run. This method will return as soon as the
        run has launched. This method is equivalent to `Runner.async_resume`.
        
        Note that this method is asynchronous and needs to be `await`ed.
        
        Parameters
        ----------
        **kwargs : Any
            Additional arguments that you would pass to `python myflow.py` after
            the `run` command, in particular, any parameters accepted by the flow.
        
        Returns
        -------
        ExecutingRun
            ExecutingRun representing the run that was started.
        """
        ...
    def cleanup(self):
        """
        Delete any temporary files created during execution.
        
        Call this method after using `async_run` or `async_resume`. You don't
        have to call this after `nbrun` or `nbresume`.
        """
        ...
    ...

