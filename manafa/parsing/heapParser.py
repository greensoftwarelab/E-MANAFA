"""Per-class Java heap statistics from a Perfetto java_hprof (heap graph) trace."""

from perfetto.trace_processor import TraceProcessor

# Per heap dump and class: instance count, shallow size (the objects' own bytes) and
# retained size (what collecting them would free, from the dominator tree). An instance
# dominated by another instance of its own class (a list or tree node) is skipped, so a
# linked structure's subtree is not counted once per node.
HEAP_QUERY = """
SELECT o.graph_sample_ts AS dump_ts, c.name AS class_name,
       COUNT(*) AS instance_count, SUM(o.self_size) AS shallow_bytes,
       SUM(IIF(p.type_id IS o.type_id, 0, d.dominated_size_bytes)) AS retained_bytes
FROM heap_graph_dominator_tree d
JOIN heap_graph_object o ON o.id = d.id
JOIN heap_graph_class c ON o.type_id = c.id
LEFT JOIN heap_graph_object p ON p.id = d.idom_id
GROUP BY dump_ts, class_name
ORDER BY dump_ts
"""


def parse_heap_trace(trace_file):
    """parses a heap graph trace into per-class series, one value per dump, oldest first.
    Args:
        trace_file: path of the Perfetto trace.
    Returns:
        dict: {'dump_timestamps': [...], 'classes': {name: {'instance_count': [...],
        'shallow_bytes': [...], 'retained_bytes': [...]}}}. A class absent from a dump is 0 there.
    """
    tp = TraceProcessor(trace=trace_file)
    try:
        tp.query("INCLUDE PERFETTO MODULE android.memory.heap_graph.dominator_tree")
        rows = [r for r in tp.query(HEAP_QUERY) if r.class_name is not None]
    finally:
        tp.close()
    dumps = sorted({r.dump_ts for r in rows})
    index = {ts: i for i, ts in enumerate(dumps)}
    classes = {}
    for r in rows:
        c = classes.setdefault(r.class_name, {k: [0] * len(dumps) for k in ('instance_count', 'shallow_bytes', 'retained_bytes')})
        i = index[r.dump_ts]
        c['instance_count'][i] = r.instance_count
        c['shallow_bytes'][i] = r.shallow_bytes
        c['retained_bytes'][i] = r.retained_bytes
    return {'dump_timestamps': dumps, 'classes': classes}
