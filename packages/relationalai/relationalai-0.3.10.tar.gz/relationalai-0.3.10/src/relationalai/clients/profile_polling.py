import logging
import threading
import time
import traceback

from relationalai import debugging

PROFILE_POLL_SLEEP_S = 1.5

class TransactionEventsFeedbackHandler(logging.Handler):
    def __init__(self, resources):
        super().__init__()
        self.resources = resources
    
    def emit(self, record):
        if (isinstance(record.msg, dict) and
            record.msg["event"] == "span_start"):
            span = record.msg["span"]
            if span.type == "wait" and span.parent.type == "transaction":
                # spawn a thread to poll for profile events
                thread = threading.Thread(
                    target=self._poll_profile_events,
                    args=(record.msg["span"].attrs["txn_id"],),
                )
                thread.start()
                # wait for thread?
    
    def _poll_profile_events(self, txn_id):
        continuation_token = ''
        while True:
            try:
                resp = self.resources.get_transaction_events(txn_id, continuation_token)
                
                debugging.event('profile_events', txn_id=txn_id, profile_events=resp['events'])
                
                continuation_token = resp['continuation_token']
                # Empty continuation token indicates that we've reached the end of the stream.
                if continuation_token == '':
                    break
                time.sleep(PROFILE_POLL_SLEEP_S)
            except Exception as e:
                debugging.error(e)
                print('Error polling profile events:', e)
                traceback.print_exc()
