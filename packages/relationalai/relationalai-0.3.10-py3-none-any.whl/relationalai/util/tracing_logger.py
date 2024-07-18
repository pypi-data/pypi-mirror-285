import logging
from typing import Dict, List

from relationalai.debugging import Span
from relationalai.util.keys import get_key

ATTR_ALLOW_LIST = {
    'transaction': {'txn_id'},
    'wait': {'txn_id'},
}

class TracingLogger(logging.Handler):
    """
    This logger prints spans to stdout as they start and finish.
    """
    
    def __init__(self):
        super().__init__()
        self.open_spans = {}

    def emit(self, record):
        if isinstance(record.msg, dict):
            msg = record.msg
            if msg['event'] == 'span_start':
                span = msg['span']
                self.open_spans[str(span.id)] = span
                path = get_path(span)
                attrs = get_attributes(span.type, span.attrs)
                print('start', format_key_path(path), attrs)
            elif msg['event'] == 'span_end':
                span = self.open_spans.pop(msg['id'])
                path = get_path(span)
                attrs = get_attributes(span.type, msg['end_attrs'])
                attrs['elapsed_s'] = (span.end_timestamp - span.start_timestamp).total_seconds()
                print('  end', format_key_path(path), attrs)


def get_path(span: Span) -> List[Span]:
    path = []
    cur = span
    while cur is not None:
        path.append(cur)
        cur = cur.parent
    path.reverse()
    return path

def get_attributes(span_type: str, attrs: Dict):
    out = {}
    allowed_attributes = ATTR_ALLOW_LIST.get(span_type, set())
    for attr in allowed_attributes:
        if attr in attrs:
            out[attr] = attrs[attr]
    return out

def format_span(span: Span):
    key = get_key(span)
    if key is None:
        return span.type
    return f"{span.type}({key})"

def format_key_path(path: List[Span]):
    return '.'.join([format_span(span) for span in path])
