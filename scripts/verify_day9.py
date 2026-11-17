"""Run from repository root with .venv/bin/python scripts/verify_day9.py."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
src = root / 'src'
commands = [
 ('lab9.smoke', 0),
 ('lab9.evalset --check', 0),
 ('lab9.evalset --v2 --check', 0),
 ('pytest -q -o addopts=', 0),
 ('lab9.judge --csv data/eval/judge_tone_public.csv --audit 5', 0),
 ('lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5', 1),
 ('lab9.eval --shape swarm --out reports/eval_pr.json', 0),
 ('lab9.ci_check --pr reports/eval_pr.json --baseline reports/baseline_v1.json', 0),
 ('lab9.gate --pr reports/eval_pr.json --baseline reports/baseline_v1.json', 0),
 ('lab9.eval --shape fixed', 0),
 ('lab9.gate --pr reports/eval_fixed.json --baseline reports/baseline_v1.json', 0),
 ('lab9.eval --shape seeded_regression', 0),
 ('lab9.gate --pr reports/eval_seeded_regression.json --baseline reports/baseline_v1.json', 1),
 ('lab9.mutation --detect', 0),
 ('lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json', 0),
 ('lab9.mutation --spec config/metric_spec_v2.yaml --aa 66,77,88,99,110', 0),
 ('lab9.eval --shape slice_regression --spec config/metric_spec_v2.yaml', 0),
 ('lab9.traps --pr reports/eval_slice_regression.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml', 0),
]
for trap in ('evaluator_errors_as_nan','dropped_failing_rows','cherry_picked_seeds','loosened_spec'):
    spec = f'reports/traps/{trap}.spec.yaml --base-spec config/metric_spec_v2.yaml' if trap == 'loosened_spec' else 'config/metric_spec_v2.yaml'
    commands.append((f'lab9.gate --pr reports/traps/{trap}.json --baseline reports/baseline_v2.json --spec {spec}',1))
log = []
failed = []
for command, expected in commands:
    print(f'Running {command}', flush=True)
    run = subprocess.run([sys.executable, '-m', *command.split()], cwd=src, capture_output=True, text=True)
    log.append(f'$ python -m {command}\n{run.stdout}{run.stderr}\nexit={run.returncode}; expected={expected}\n')
    if run.returncode != expected:
        failed.append(command)
    print(run.stdout[-1200:], flush=True)
(src/'reports').mkdir(exist_ok=True)
(src/'reports/verification.txt').write_text('\n'.join(log), encoding='utf-8')
print('FAILED: '+str(failed) if failed else 'ALL CHECKS PASSED (including expected rejection exits)')
sys.exit(bool(failed))
