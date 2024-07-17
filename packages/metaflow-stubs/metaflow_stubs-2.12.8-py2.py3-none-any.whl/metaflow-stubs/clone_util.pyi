##################################################################################
#                       Auto-generated Metaflow stub file                        #
# MF version: 2.12.8                                                             #
# Generated on 2024-07-16T15:51:55.380662                                        #
##################################################################################

from __future__ import annotations


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

def clone_task_helper(flow_name, clone_run_id, run_id, step_name, clone_task_id, task_id, flow_datastore, metadata_service, origin_ds_set = None, attempt_id = 0):
    ...

