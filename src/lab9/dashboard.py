"""Local evaluation dashboard. From src: python -m lab9.dashboard."""
from __future__ import annotations

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, urlparse

from lab9 import gate, stats, variants
from lab9.eval import load_spec, per_item, run_eval

ROOT = Path(__file__).resolve().parents[1]
UI = Path(__file__).with_name('ui')
SHAPES = ('swarm', 'fixed', 'honest_refactor', 'seeded_regression', 'slice_regression', 'flaky_regression')
LOCK = Lock()


def dashboard(version='v2', shape='slice_regression', *, rerun=False):
    if version not in ('v1', 'v2') or shape not in SHAPES:
        raise ValueError('Phiên bản hoặc biến thể không hợp lệ.')
    spec = load_spec(ROOT / 'config' / ('metric_spec.yaml' if version == 'v1' else 'metric_spec_v2.yaml'))
    base = json.loads((ROOT / 'reports' / f'baseline_{version}.json').read_text())
    path = ROOT / 'reports' / f'dashboard_{version}_{shape}.json'
    if not rerun and not path.exists():
        candidate = ROOT / 'reports' / ('eval_slice_regression.json' if shape == 'slice_regression' else f'eval_{shape}.json')
        if shape == 'swarm':
            candidate = ROOT / 'reports' / f'baseline_{version}.json'
        if candidate.exists():
            existing = json.loads(candidate.read_text())
            if existing['manifest']['eval_set_sha'] == base['manifest']['eval_set_sha']:
                report = existing
            else:
                report = None
        else:
            report = None
    elif not rerun:
        report = json.loads(path.read_text())
    else:
        report = None
    if report is None:
        # The harness uses relative config/data paths and trace filenames. Serialize runs.
        with LOCK:
            variants.register()
            report = run_eval(shape, spec)
            path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    blocked, lines = gate.check(report, base, spec)
    slices = []
    for rule in spec.get('slices', []):
        a = per_item(report, rule['metric'], rule['name'])
        b = per_item(base, rule['metric'], rule['name'])
        slices.append({**rule, 'value': sum(a.values()) / len(a) if a else None,
                       'baseline': sum(b.values()) / len(b) if b else None, 'items': len(a),
                       'blocked': f"slice:{rule['name']}/{rule['metric']}" in blocked})
    a, b = per_item(report, 'pass_rate'), per_item(base, 'pass_rate')
    keys = sorted(a.keys() & b.keys())
    delta, low, high = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys])
    return {'report': report, 'baseline': base, 'spec': spec, 'blocked': blocked, 'gate_lines': lines,
            'slices': slices, 'comparison': {'delta': delta, 'low': low, 'high': high}}


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, mime='application/json; charset=utf-8'):
        body = body.encode() if isinstance(body, str) else body
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def api(self, rerun=False):
        query = parse_qs(urlparse(self.path).query)
        try:
            result = dashboard(query.get('version', ['v2'])[0], query.get('shape', ['slice_regression'])[0], rerun=rerun)
            self.send(200, json.dumps(result, ensure_ascii=False, allow_nan=False))
        except ValueError as exc:
            self.send(400, json.dumps({'error': str(exc)}, ensure_ascii=False))
        except Exception as exc:
            self.send(500, json.dumps({'error': f'Không thể tải đánh giá: {exc}'}, ensure_ascii=False))

    def do_GET(self):
        route = urlparse(self.path).path
        if route == '/api/dashboard':
            return self.api()
        files = {'/': ('index.html', 'text/html; charset=utf-8'),
                 '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                 '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if route in files:
            name, mime = files[route]
            return self.send(200, (UI / name).read_bytes(), mime)
        if route == '/api/evidence':
            return self.send(200, (ROOT.parent / 'docs/trace_evidence.json').read_bytes())
        self.send(404, json.dumps({'error': 'Không tìm thấy nội dung.'}))

    def do_POST(self):
        # Browser requests from another origin must not trigger evaluations.
        origin = self.headers.get('Origin')
        if origin and origin != f'http://{self.headers.get("Host")}':
            return self.send(403, json.dumps({'error': 'Origin không hợp lệ.'}))
        if urlparse(self.path).path == '/api/run':
            return self.api(rerun=True)
        self.send(404, '{}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8099)
    args = parser.parse_args()
    os.chdir(ROOT)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Day 9 dashboard: http://127.0.0.1:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
