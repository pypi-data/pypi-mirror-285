from relationalai.debugging import Span

# For a given span name, the attribute to use as its key.
SPAN_KEYS = {
    'test': 'name',
    'benchmark': 'name',
    'run': 'idx',
    'query': 'tag',
}

def get_key(span: 'Span'):
    type = span.type
    if type in SPAN_KEYS:
        key = SPAN_KEYS[type]
        return span.attrs[key]
    return None
