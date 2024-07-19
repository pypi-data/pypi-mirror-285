import unittest
from datetime import datetime, timedelta
from langfuse.api.resources.commons.types import Trace

from olangfuse import OpenLangfuse


class OpenLangfuseTest(unittest.TestCase):
    open_langfuse = OpenLangfuse()

    def dowload_traces(self):
        time_start = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
        time_end = datetime.now().strftime("%d/%m/%Y")
        traces = self.open_langfuse.download_traces(
            time_start=time_start,
            time_end=time_end,
        )
        return traces

    def test_download_traces(self):
        traces = self.dowload_traces()
        self.assertIsNotNone(traces)
        self.assertTrue(len(traces) > 0)

    def test_update_traces(self):
        traces = self.dowload_traces()[0]
        new_trace_body = {}
        for key in traces.dict().keys():
            if key not in Trace.__fields__:
                continue
            new_trace_body[key] = getattr(traces, key)
        new_trace_body["name"] = "new_trace_name_test"
        new_trace = Trace(**new_trace_body)
        self.open_langfuse.update_traces([traces], [new_trace])

    def test_delete_traces(self):
        traces = self.dowload_traces()[0]
        trace_ids = traces.id
        self.open_langfuse.delete_traces([trace_ids], traces.projectId)
        traces = self.dowload_traces()[0]
        self.assertTrue(traces.id != trace_ids)


if __name__ == "__main__":
    unittest.main()
