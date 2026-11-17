"""Offline classifier calibration and paired statistics; FAIL is positive."""
from collections.abc import Sequence
from math import comb, isfinite
from numbers import Integral

POS = "FAIL"


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    if len(human) != len(judge) or not human:
        raise ValueError("labels must be nonempty and paired")
    out = dict(tp=0, fp=0, fn=0, tn=0)
    for h, j in zip(human, judge):
        if h not in ("PASS", "FAIL") or j not in ("PASS", "FAIL"):
            raise ValueError("expected PASS/FAIL labels")
        out['tp' if h == POS and j == POS else 'fn' if h == POS else 'fp' if j == POS else 'tn'] += 1
    return out


def precision_recall(human, judge):
    c = confusion(human, judge)
    return (c['tp'] / (c['tp'] + c['fp']) if c['tp'] + c['fp'] else 0.0,
            c['tp'] / (c['tp'] + c['fn']) if c['tp'] + c['fn'] else 0.0)


def cohen_kappa(human, judge):
    c = confusion(human, judge)
    n = sum(c.values())
    observed = (c['tp'] + c['tn']) / n
    expected = ((c['tp'] + c['fn']) * (c['tp'] + c['fp']) +
                (c['tn'] + c['fp']) * (c['tn'] + c['fn'])) / n**2
    if expected == 1:
        raise ValueError("undefined kappa")
    return (observed - expected) / (1 - expected)


def rogan_gladen(observed_rate, sensitivity, specificity):
    if any(not isfinite(x) or not 0 <= x <= 1 for x in (observed_rate, sensitivity, specificity)):
        raise ValueError("rates must lie in [0,1]")
    denominator = sensitivity + specificity - 1
    if denominator <= 0:
        raise ValueError("judge must be better than chance")
    return max(0.0, min(1.0, (observed_rate + specificity - 1) / denominator))


def paired_bootstrap(a, b, *, n_resamples=1000, rng=2027, confidence=0.95):
    import numpy as np
    from scipy.stats import bootstrap
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.ndim != 1 or b.ndim != 1 or len(a) != len(b) or not len(a):
        raise ValueError("nonempty paired vectors required")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("finite observations required")
    if n_resamples < 1 or not 0 < confidence < 1:
        raise ValueError("invalid bootstrap parameters")
    delta = float(np.mean(a - b))
    if np.all(a - b == a[0] - b[0]):
        return delta, delta, delta
    result = bootstrap((a, b), lambda x, y, axis: np.mean(x - y, axis=axis), paired=True,
                       method='percentile', n_resamples=n_resamples, confidence_level=confidence,
                       rng=np.random.default_rng(rng))
    return delta, float(result.confidence_interval.low), float(result.confidence_interval.high)


def _validate(n, c, k):
    if any(isinstance(v, bool) or not isinstance(v, Integral) for v in (n, c, k)) or not (n >= 1 and 0 <= c <= n and 1 <= k <= n):
        raise ValueError("require integers n>=1, 0<=c<=n, 1<=k<=n")


def pass_at_k(n, c, k):
    _validate(n, c, k)
    return 1 - comb(n - c, k) / comb(n, k)


def pass_hat_k(n, c, k):
    _validate(n, c, k)
    return comb(c, k) / comb(n, k)
