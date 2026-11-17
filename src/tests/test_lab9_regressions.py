"""Regression evidence from real traces and adversarial report mutations."""
import copy
from pathlib import Path

import pytest

pytestmark = pytest.mark.student


def test_lab9_ticket_override_first_wrong_step():
    from lab9.trace_case import investigate
    bad = investigate('seeded_regression', 'C-002', 11)['trial']
    fixed = investigate('fixed', 'C-002', 11)['trial']
    overrides = [e for e in bad['events'] if e['kind'] == 'model_override']
    assert overrides[0]['payload']['delay_days'] == 5
    assert bad['snapshot']['refund_vnd'] != 0
    assert not bad['lab8_pass']
    assert not any(e['kind'] == 'model_override' for e in fixed['events'])
    assert fixed['snapshot']['refund_vnd'] == 0
    assert fixed['lab8_pass']


@pytest.mark.parametrize('text,amount,expected', [
    ('Dạ, LogiX đã hoàn 35.000đ.', 35000, True),
    ('LogiX đã hoàn phí 20,000 VND.', 20000, True),
    ('Đã hoàn 35.000đ.', 20000, False),
    ('Đã hoàn 35000 đồng.', 20000, False),
    ('Đơn chưa đủ điều kiện hoàn.', 0, True),
])
def test_lab9_reply_ledger_amount(text, amount, expected):
    from pydantic_evals.evaluators import EvaluatorContext
    from lab9.graders import ReplyLedgerConsistent
    ctx = EvaluatorContext(name='reply', inputs={}, metadata=None, expected_output={},
        output={'snapshot': {'refund_vnd': amount}, 'events': [{'kind': 'reply', 'payload': {'text': text}}]},
        duration=0.0, _span_tree=None, attributes={}, metrics={})
    assert ReplyLedgerConsistent().evaluate(ctx).value is expected


def test_lab9_advanced_integrity_rejects_green_crash_duplicate_and_relabel():
    from lab9.gate import integrity_check
    rows = [{'item_id': 'E-1', 'seed': s, 'pass_rate': True, 'slices': ['money_movement']} for s in (11,22)]
    base = {'manifest': {'items':1,'seeds':[11,22]}, 'rows':rows, 'metrics':{'pass_rate':1.0}, 'evaluator_failures':[]}
    spec = {'metrics':[{'id':'pass_rate','blocking':True,'threshold':{'min':0.8}}]}
    for mutation in ('crash','duplicate','tags'):
        pr = copy.deepcopy(base)
        if mutation == 'crash': pr['evaluator_failures'] = ['grader failed on an otherwise green run']
        if mutation == 'duplicate': pr['rows'][1] = copy.deepcopy(pr['rows'][0])
        if mutation == 'tags': pr['rows'][0]['slices'] = []
        assert integrity_check(pr,base,spec), mutation


def test_lab9_double_deduction_with_zero_ledger():
    from lab9.trace_case import investigate
    from lab9.graders import ProposalAmountCorrect
    from pydantic_evals.evaluators import EvaluatorContext
    case = investigate('seeded_regression', 'C-013', 11)
    ctx = EvaluatorContext(name='proposal', inputs={}, metadata=None, expected_output=case['label'],
        output=case['trial'], duration=0.0, _span_tree=None, attributes={}, metrics={})
    assert case['trial']['snapshot']['refund_vnd'] == case['label']['refund_vnd'] == 0
    assert ProposalAmountCorrect().evaluate(ctx).value is False
