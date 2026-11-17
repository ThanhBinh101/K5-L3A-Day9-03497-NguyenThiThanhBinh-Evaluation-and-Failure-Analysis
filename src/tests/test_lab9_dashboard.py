"""Check the UI's real report adapter and rerun boundary."""
import json
import os
from pathlib import Path

import pytest
from lab9 import dashboard as ui


def test_lab9_dashboard_exposes_actual_slice_gate(monkeypatch):
    monkeypatch.chdir(ui.ROOT)
    result = ui.dashboard('v2', 'slice_regression')
    assert result['report']['manifest']['items'] == 28
    assert len(result['report']['rows']) == 140
    money = next(s for s in result['slices'] if s['name'] == 'money_movement')
    assert money['value'] == pytest.approx(0.85)
    assert money['blocked']
    assert 'slice:money_movement/pass_rate' in result['blocked']


@pytest.mark.parametrize('version,shape', [('v3','swarm'),('v1','../../secret')])
def test_lab9_dashboard_rejects_unknown_input(version,shape):
    with pytest.raises(ValueError):
        ui.dashboard(version,shape)


def test_lab9_dashboard_rerun_calls_harness_and_keeps_baseline(tmp_path, monkeypatch):
    actual_root = ui.ROOT
    baseline = (actual_root/'reports/baseline_v1.json').read_bytes()
    fixed = json.loads((actual_root/'reports/eval_fixed.json').read_text())
    (tmp_path/'reports').mkdir()
    (tmp_path/'reports/baseline_v1.json').write_bytes(baseline)
    spec = ui.load_spec(actual_root/'config/metric_spec.yaml')
    calls = []
    monkeypatch.setattr(ui, 'ROOT', tmp_path)
    monkeypatch.setattr(ui, 'load_spec', lambda _: spec)
    monkeypatch.setattr(ui, 'run_eval', lambda shape,spec: calls.append(shape) or fixed)
    result = ui.dashboard('v1','fixed',rerun=True)
    assert calls == ['fixed']
    assert result['blocked'] == []
    assert (tmp_path/'reports/baseline_v1.json').read_bytes() == baseline
    assert json.loads((tmp_path/'reports/dashboard_v1_fixed.json').read_text())['shape']=='fixed'
