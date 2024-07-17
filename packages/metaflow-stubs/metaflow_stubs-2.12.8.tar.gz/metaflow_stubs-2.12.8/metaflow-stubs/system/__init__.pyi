##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.12.8                                                             #
# Generated on 2024-07-16T15:51:55.379556                                        #
##################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import metaflow.monitor
    import typing
    import metaflow.event_logger

class SystemMonitor(object, metaclass=type):
    def __init__(self):
        ...
    def __del__(self):
        ...
    def update_context(self, context: typing.Dict[str, typing.Any]):
        """
        Update the global context maintained by the system monitor.
        
        Parameters
        ----------
        context : Dict[str, Any]
            A dictionary containing the context to update.
        """
        ...
    def init_system_monitor(self, flow_name: str, monitor: "metaflow.monitor.NullMonitor"):
        ...
    @property
    def monitor(self) -> typing.Optional["metaflow.monitor.NullMonitor"]:
        ...
    def measure(self, name: str):
        """
        Context manager to measure the execution duration and counter of a block of code.
        
        Parameters
        ----------
        name : str
            The name to associate with the timer and counter.
        
        Yields
        ------
        None
        """
        ...
    def count(self, name: str):
        """
        Context manager to increment a counter.
        
        Parameters
        ----------
        name : str
            The name of the counter.
        
        Yields
        ------
        None
        """
        ...
    def gauge(self, gauge: "metaflow.monitor.Gauge"):
        """
        Log a gauge.
        
        Parameters
        ----------
        gauge : metaflow.monitor.Gauge
            The gauge to log.
        """
        ...
    ...

class SystemLogger(object, metaclass=type):
    def __init__(self):
        ...
    def __del__(self):
        ...
    def update_context(self, context: typing.Dict[str, typing.Any]):
        """
        Update the global context maintained by the system logger.
        
        Parameters
        ----------
        context : Dict[str, Any]
            A dictionary containing the context to update.
        """
        ...
    def init_system_logger(self, flow_name: str, logger: "metaflow.event_logger.NullEventLogger"):
        ...
    @property
    def logger(self) -> typing.Optional["metaflow.event_logger.NullEventLogger"]:
        ...
    def log_event(self, level: str, module: str, name: str, payload: typing.Optional[typing.Any] = None):
        """
        Log an event to the event logger.
        
        Parameters
        ----------
        level : str
            Log level of the event. Can be one of "info", "warning", "error", "critical", "debug".
        module : str
            Module of the event. Usually the name of the class, function, or module that the event is being logged from.
        name : str
            Name of the event. Used to qualify the event type.
        payload : Optional[Any], default None
            Payload of the event. Contains the event data.
        """
        ...
    ...

