import os
from langfuse import Langfuse
from typing import Optional, List
from langfuse.task_manager import TaskManager
from langfuse.version import __version__ as version
from langfuse.api.resources.commons.types import Trace

from olangfuse.utils import (
    TIME_OUT,
    FLUSH_AT,
    FLUSH_INTERVAL,
    MAX_RETRIES,
    THREADS,
    SDK_NAME,
    PUBLIC_KEY,
    SECRET_KEY,
    BASE_URL,
)

from olangfuse.components import FernLangfuseClient, OpenLangfuseClient, OpenStatefulTraceClient


class OpenLangfuse(Langfuse):
    def __init__(self):
        self.base_url = BASE_URL
        super().__init__(public_key=PUBLIC_KEY, secret_key=SECRET_KEY, host=self.base_url, timeout=TIME_OUT)
        self.client = FernLangfuseClient(
            base_url=self.base_url,
            username=PUBLIC_KEY,
            password=SECRET_KEY,
            x_langfuse_sdk_name=SDK_NAME,
            x_langfuse_sdk_version=version,
            x_langfuse_public_key=PUBLIC_KEY,
        )
        self.task_manager = TaskManager(
            threads=THREADS,
            flush_at=FLUSH_AT,
            flush_interval=FLUSH_INTERVAL,
            max_retries=MAX_RETRIES,
            client=OpenLangfuseClient(
                public_key=PUBLIC_KEY,
                secret_key=SECRET_KEY,
                base_url=self.base_url,
                version=version,
                timeout=TIME_OUT,
                session=None,
            ),
            public_key=PUBLIC_KEY,
            sdk_name=SDK_NAME,
            sdk_version=version,
            sdk_integration="default",
        )

    def download_traces(
        self,
        user_id: Optional[str] = None,
        name: Optional[str] = None,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        page: int = 1,
    ) -> List[OpenStatefulTraceClient]:
        """
        Retrieves traces based on the given parameters.

        Args:
            user_id (str): The ID of the user who created the traces.
            name (str): The name of the trace.
            time_start (str): The start time of the trace. (Format: 'dd/mm/yyyy')
            time_end (str): The end time of the trace. (Format: 'dd/mm/yyyy')
            page (int): The page number.

        Returns:
            List[StatefulTraceClient]: The list of traces.
        """
        traces = self.client.get_traces(user_id=user_id, name=name, time_start=time_start, time_end=time_end, page=page)
        traces = [
            OpenStatefulTraceClient(
                client=self.client, trace_id=trace.id, task_manager=self.task_manager, **trace.dict()
            )
            for trace in traces
        ]
        return traces

    def delete_traces(
        self,
        trace_ids: List[str],
        project_id: str,
    ):
        """
        Deletes traces based on the given trace IDs.

        Args:
            trace_ids (List[str]): The list of trace IDs.
            project_id (str): The ID of the project.
        """
        self.client.delete_traces(trace_ids, project_id=project_id)

    def update_traces(
        self,
        traces: List[OpenStatefulTraceClient],
        trace_bodies: List[Trace],
    ):
        """
        Updates traces based on the given trace IDs.

        Args:
            traces (List[OpenStatefulTraceClient]): The list of traces.
        """
        self.client.update_traces(traces, trace_bodies, self.task_manager)
