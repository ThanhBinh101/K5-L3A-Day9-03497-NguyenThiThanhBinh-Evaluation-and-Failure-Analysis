"""Collect isolated failure traces without changing any supplied variant or Lab8 file."""
from pathlib import Path
import json
import os
import sys
root = Path(__file__).resolve().parents[1]
os.chdir(root/'src')
sys.path.insert(0,str(root/'src'))
from lab8.shapes import SHAPES
from lab9.variant_agent import make_shape
from lab9.trace_case import investigate
cases = [('FM-01','leaky_trace','C-001'), ('FM-02','ignore_denied','C-007'),
         ('FM-03','ticket_trust','C-002'), ('FM-04','sum_parts','C-014'),
         ('FM-05','pre_deducted','C-014'), ('FM-06','stale_clause','C-006'),
         ('FM-07','sibling_refund','C-010'), ('FM-08','misreport','C-008')]
out = []
for fm,bug,claim in cases:
    name = f'evidence_{bug}'
    SHAPES[name] = make_shape(name, {'no_override',bug})
    out.append((fm,bug,claim,investigate(name,claim,11)))
out.append(('FM-09','fixed_scope_control','C-005',investigate('fixed','C-005',11)))
(root/'docs/trace_evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('wrote docs/trace_evidence.json')
