import json
import queue
import threading
import time

import logging
import traceback
import uuid

from relationalai.util.keys import get_key

# Don't insert these as attrs since they get their own columns
FILTER_ATTRS = {
    "event",
    "span",
    "id",
    "parent_id",
    "start_time",
    "start_timestamp",
    "end_time",
    "end_timestamp",
    "elapsed",
}

class SnowflakeLogger(logging.Handler):
    """
    This is a logging handler that inserts spans directly into a Snowflake table.

    It uses a queue and a worker thread to buffer spans and then insert them in batches.
    """
    
    def __init__(self, snowflake_conn, sleep_interval_s=2):
        super().__init__()
        self.trace_id = uuid.uuid4()
        self.snowflake_conn = snowflake_conn
        self.queue = queue.Queue()
        self.is_shut_down = False
        self.sleep_interval_s = sleep_interval_s
        self.worker_thread = threading.Thread(target=self._consume_loop)
        self.worker_thread.start()
        self.open_spans = {} # only accessed from worker thread
        print('snowflake logger started with trace id', self.trace_id)
    
    def emit(self, record):
        if record.msg["event"] in ("span_start", "span_end"):
            self.queue.put(record.msg)
    
    def _consume_loop(self):
        while True:
            while not self.queue.empty():
                try:
                    batch = self._get_batch()
                    self._send_batch(batch)
                except Exception as e:
                    print('snowflake logger error:', e)
                    traceback.print_exc()
            if self.is_shut_down:
                return
            time.sleep(self.sleep_interval_s)
    
    def _get_batch(self):
        batch = []
        try:
            while True:
                item = self.queue.get_nowait()
                batch.append(item)
        except queue.Empty:
            pass
        return batch
    
    def _send_batch(self, batch):
        if not batch:
            return
        
        inserts = []
    
        for event in batch:
            if event["event"] == "span_start":
                span = event["span"]
                self.open_spans[str(span.id)] = span
            elif event["event"] == "span_end":
                span = self.open_spans.pop(event["id"])
                # assemble attributes
                filtered_attrs = {}
                for k, v in span.attrs.items():
                    if k not in FILTER_ATTRS:
                        filtered_attrs[k] = v
                for k, v in event["end_attrs"].items():
                    if k not in FILTER_ATTRS:
                        filtered_attrs[k] = v
                # get key
                span_key = get_key(span)
                # add to batch
                inserts.append({
                    "id": str(span.id),
                    "parent_id": None if span.parent is None else str(span.parent.id),
                    "trace_id": str(self.trace_id),
                    "key": str(span_key) if span_key is not None else None,
                    "type": span.type,
                    "start_ts": span.start_timestamp,
                    "finish_ts": span.end_timestamp,
                    "attrs": json.dumps(filtered_attrs, default=default_serialize),
                })
        # execute
        if inserts:
            self.snowflake_conn.cursor().executemany(
                """
                INSERT INTO spans_raw (id, parent_id, trace_id, type, key, start_ts, finish_ts, attrs)
                VALUES (%(id)s, %(parent_id)s, %(trace_id)s, %(type)s, %(key)s, %(start_ts)s, %(finish_ts)s, %(attrs)s)
                """,
                inserts,
            )

    
    def shut_down(self):
        self.is_shut_down = True
        print('snowflake logger: waiting to shut down...')
        self.worker_thread.join()
        print('snowflake logger: shut down')

def default_serialize(obj):
    return '<skipped>'
