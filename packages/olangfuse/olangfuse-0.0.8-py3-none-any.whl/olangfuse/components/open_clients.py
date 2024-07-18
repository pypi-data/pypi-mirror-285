import httpx
import datetime
from typing import Optional, List
from langfuse.request import LangfuseClient
from langfuse.api.client import FernLangfuse
from langfuse.task_manager import TaskManager
from langfuse.api.core import SyncClientWrapper
from langfuse.client import StateType, StatefulTraceClient
from langfuse.api.resources.score.client import ScoreClient
from langfuse.api.resources.datasets.client import DatasetsClient
from langfuse.api.resources.commons.types import Trace, TraceWithDetails
from langfuse.api.resources.dataset_items.client import DatasetItemsClient

from olangfuse.components.open_traces import OpenTraceClient
from olangfuse.utils import get_client_custom_params, compare_date


class OpenStatefulTraceClient(StatefulTraceClient):
    """Class for handling stateful operations of traces in the Langfuse system. Inherits from StatefulClient.

    Attributes:
        client (FernLangfuse): Core interface for Langfuse API interaction.
        state_type (StateType): Type of the stateful entity (observation or trace).
        trace_id (str): The trace ID associated with this client.
        task_manager (TaskManager): Manager for handling asynchronous tasks.
        id (str): Unique identifier of the trace.
        timestamp: dt.datetime
        name: typing.Optional[str] = None
        input: typing.Optional[typing.Any] = None
        output: typing.Optional[typing.Any] = None
        session_id: typing.Optional[str] = pydantic.Field(alias="sessionId", default=None)
        release: typing.Optional[str] = None
        version: typing.Optional[str] = None
        user_id: typing.Optional[str] = pydantic.Field(alias="userId", default=None)
        metadata: typing.Optional[typing.Any] = None
        tags: typing.Optional[typing.List[str]] = None
        public: typing.Optional[bool] = pydantic.Field(
            default=None, description="Public traces are accessible via url without login"
        )
    """

    def __init__(
        self,
        client: FernLangfuse,
        id: str,
        trace_id: str,
        task_manager: TaskManager,
        state_type: Optional[StateType] = StateType.TRACE,
        **kwargs
    ):
        super().__init__(client=client, id=id, state_type=state_type, trace_id=trace_id, task_manager=task_manager)
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.dict_attr = kwargs
        self.dict_attr["id"] = id

    def dict(self):
        return self.dict_attr


class FernLangfuseClient(FernLangfuse):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client_wrapper = SyncClientWrapper(**kwargs, httpx_client=httpx.Client(**get_client_custom_params()))
        self.trace = OpenTraceClient(client_wrapper=self._client_wrapper)
        self.score = ScoreClient(client_wrapper=self._client_wrapper)
        self.datasets = DatasetsClient(client_wrapper=self._client_wrapper)
        self.dataset_items = DatasetItemsClient(client_wrapper=self._client_wrapper)

    def get_traces(
        self,
        user_id: Optional[str] = None,
        name: Optional[str] = None,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        page: int = 1,
        **kwargs
    ) -> List[TraceWithDetails]:
        """
        Retrieves traces based on the given parameters.

        Args:
            user_id (str): The ID of the user who created the traces.
            name (str): The name of the trace.
            time_start (str): The start time of the trace. (Format: 'dd/mm/yyyy')
            time_end (str): The end time of the trace. (Format: 'dd/mm/yyyy')
            page (int): The page number.
            **kwargs: Additional query parameters.

        Returns:
            List[StatefulTraceClient]: The list of traces.
        """
        if isinstance(time_start, str):
            time_start = datetime.datetime.fromisoformat("-".join(reversed(time_start.split("/"))) + " 00:00:00+00:00")
        traces = self.trace.list(
            page=page, limit=100, order_by="timestamp.desc", user_id=user_id, name=name, from_timestamp=time_start
        )
        data = []

        for trace in traces.data:
            trace_time = trace.timestamp.strftime("%d/%m/%Y")
            if time_end and compare_date(time_end, trace_time) > 0:
                return data
            if user_id and trace.user_id != user_id:
                continue
            if name and trace.name != name:
                continue
            data.append(trace)

        if traces.meta.page < traces.meta.total_pages - 1:
            data.extend(self.get_traces(user_id, name, time_start, time_end, page=page + 1, **kwargs))

        return data

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
        self.trace.delete(trace_ids, project_id=project_id, batch_size=len(trace_ids))

    def update_traces(
        self, traces: List[OpenStatefulTraceClient], trace_bodies: List[Trace], task_manager: TaskManager
    ):
        """
        Updates traces.

        Args:
            traces_ids (List[OpenStatefulTraceClient]): The list of stateful trace clients.
            **kwargs: Trace body used for updating.
        """
        for trace, trace_body in zip(traces, trace_bodies):
            trace.update(**trace_body.dict())
            trace = OpenStatefulTraceClient(
                client=self, trace_id=trace.id, task_manager=task_manager, **trace_body.dict()
            )


class OpenLangfuseClient(LangfuseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._session = httpx.Client(**get_client_custom_params())
