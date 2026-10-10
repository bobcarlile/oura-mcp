#!/usr/bin/env python3
"""Seeded, offline trend feasibility study; run from any directory with Python.

Only stdlib and the real oura_mcp.method module. Test generator function ASTs
are loaded verbatim without importing pytest or executing the test suite.
No source, thresholds, data files, or test generators are modified.
"""
from __future__ import annotations

import ast
import datetime as dt
import math
from pathlib import Path
import random
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from oura_mcp import method as M

SEED = 20261008
NULL_REPS = 2000
POWER_REPS = 1000
# Predeclared screening tolerance: about 5%, allowing Monte Carlo uncertainty.
# Stricter than the existing tests' 7%; not a claim of exact size control.
MAX_FALSE_ALARM = 0.06
WINDOWS = (60, 90, 180)
TRENDS = ('OLS', 'OLS effective-n', 'HAC', 'History slope')
COMPARES = ('Compare halves', 'Compare last14')
BASE = 739000


def generators(filename, names):
    tree = ast.parse((ROOT / 'tests' / filename).read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == set(names)
    namespace = dict(math=math, random=random, dt=dt, BASE=BASE)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, 'exec'), namespace)
    return namespace


C = generators('test_compare.py', ('_ar1', '_days'))
R = generators('test_relate.py', ('_ar1', '_days', '_weekend', '_null'))
# rho=.5 occurs in relate's real-relation generator; .4 in compare's weekday
# test. Both are included along with every calibration rho from compare.
SCENARIOS = [(f'AR {rho:g}', rho, 0.0, gap)
             for rho in (0.0, 0.3, 0.4, 0.5, 0.65, 0.8) for gap in (0.0, 0.3)]
SCENARIOS += [(name, rho, amp, gap)
              for name, rho, amp in [('Weekday C', 0.4, 1.0), ('Weekday R', 0.65, 1.5)]
              for gap in (0.0, 0.3)]


def draw(n, scenario, rng):
    name, rho, amp, gap = scenario
    if name == 'Weekday R':
        # Includes precisely the original shared mask and RNG consumption.
        days, _ = R['_null']('weekly', 120 + n, rng, gap)
    else:
        values = C['_ar1'](120 + n, rho, rng)
        if amp:
            values = R['_weekend'](values, amp)
        days = C['_days'](BASE, values)
        days = [d for d in days if rng.random() >= gap]
    boundary = dt.date.fromordinal(BASE + 120).isoformat()
    return ([d for d in days if d[0] < boundary],
            [d for d in days if d[0] >= boundary])


def decision(slope, variance, df):
    if variance <= 0 or df < 1:
        return 'cannot_tell'
    return ('outside_noise' if abs(slope) > M.t_critical(df) * math.sqrt(variance)
            else 'within_noise')


def trend_results(days, history, n):
    count = len(days)
    if count < M.MIN_DAYS:
        return dict.fromkeys(TRENDS, 'cannot_tell')
    x = [dt.date.fromisoformat(d).toordinal() - BASE - 120 for d, _ in days]
    y = [v for _, v in days]
    xm, ym = sum(x) / count, sum(y) / count
    xc = [v - xm for v in x]
    sxx = sum(v * v for v in xc)
    slope = sum(a * (b - ym) for a, b in zip(xc, y)) / sxx
    residual = [b - ym - slope * a for a, b in zip(xc, y)]
    s2 = sum(e * e for e in residual) / (count - 2)
    result = {'OLS': decision(slope, s2 / sxx, count - 2)}
    # Calendar-lag Newey-West sandwich, not observation-lag compression.
    # Fixed common bandwidth floor(4*(N/100)^(2/9)); HC1 finite-sample factor.
    bandwidth = max(1, math.floor(4 * (n / 100) ** (2 / 9)))
    score = dict(zip(x, (a * e for a, e in zip(xc, residual))))
    meat = sum(v * v for v in score.values())
    for lag in range(1, bandwidth + 1):
        cross = sum(v * score.get(day - lag, 0.0) for day, v in score.items())
        meat += 2 * (1 - lag / (bandwidth + 1)) * cross
    result['HAC'] = decision(slope, meat * count / (count - 2) / sxx**2, count - 2)
    if len(history) < M.MIN_HISTORY or len(M.consecutive_pairs(history)) < M.MIN_PAIRS:
        result.update(dict.fromkeys(('OLS effective-n', 'History slope'), 'cannot_tell'))
        return result
    rho = M.lag1(history)
    shrink = (1 - rho) / (1 + rho)
    effective = count * shrink
    result['OLS effective-n'] = decision(slope, s2 / sxx / shrink, effective - 2)
    # Optional fourth candidate: same OLS slope, variance from the preceding
    # history (avoids downward residual variance bias after fitting a slope).
    # Long-run AR(1) variance bound, conservative for positive rho and gaps.
    hv = [v for _, v in history]
    hm = sum(hv) / len(hv)
    hvar = sum((v - hm)**2 for v in hv) / (len(hv) - 1)
    df = min(effective, len(hv) * shrink) - 2
    result['History slope'] = decision(slope, hvar / sxx / shrink, df)
    return result


def evaluate(days, history, n, methods):
    result = {}
    if any(m in TRENDS for m in methods):
        result.update(trend_results(days, history, n))
    for name, split in [('Compare halves', n // 2), ('Compare last14', n - 14)]:
        boundary = dt.date.fromordinal(BASE + 120 + split).isoformat()
        a = [d for d in days if d[0] < boundary]
        b = [d for d in days if d[0] >= boundary]
        result[name] = M.compare_series(a, b, history)['verdict']
    return {name: result[name] for name in methods}


def accumulate(counts, result):
    for name, verdict in result.items():
        counts[name][0] += verdict == 'outside_noise'
        counts[name][1] += verdict == 'cannot_tell'
        counts[name][2] += 1


def cell(count, conditional=False):
    hits, cannot, total = count
    denominator = total - cannot if conditional else total
    rate = f'{100 * hits / denominator:.1f}' if denominator else 'NA'
    return f'{rate} / {100 * cannot / total:.1f}'


def table(headers, rows):
    print('| ' + ' | '.join(map(str, headers)) + ' |')
    print('|' + '|'.join('---' for _ in headers) + '|')
    for row in rows:
        print('| ' + ' | '.join(map(str, row)) + ' |')
    print()


def main():
    started = time.perf_counter()
    methods = TRENDS + COMPARES
    null = {}
    for n in WINDOWS:
        for j, scenario in enumerate(SCENARIOS):
            rng = random.Random(SEED + 10000 * n + j)
            counts = {m: [0, 0, 0] for m in methods}
            for _ in range(NULL_REPS):
                history, days = draw(n, scenario, rng)
                accumulate(counts, evaluate(days, history, n, methods))
            null[n, j] = counts
        print(f'Null window {n} complete', file=sys.stderr, flush=True)
    survivors = {n: tuple(m for m in TRENDS if all(
        null[n,j][m][2] > null[n,j][m][1] and
        null[n,j][m][0] / (null[n,j][m][2] - null[n,j][m][1]) <= MAX_FALSE_ALARM
        for j in range(len(SCENARIOS)))) for n in WINDOWS}
    print(f'Seed {SEED}; null reps/cell {NULL_REPS}; power reps/cell {POWER_REPS}.')
    print('Null cells: false alarms among answered / cannot_tell among all (%).\n')
    for n in WINDOWS:
        print(f'### Null: {n} days\n')
        table(('Noise', 'Missing', *methods), [
            (s[0], f'{s[3]:.0%}', *(cell(null[n, j][m], True) for m in methods))
            for j, s in enumerate(SCENARIOS)])
    for n in WINDOWS:
        print(f'Surviving trends at {n} days (every null cell <=6%): '
              + (', '.join(survivors[n]) or 'none') + '.\n')
    print('### Null ranges across all stationary scenarios\n')
    table(('Days', *methods), [(n, *(
        f'{min(null[n,j][m][0]/(null[n,j][m][2]-null[n,j][m][1])*100 for j in range(len(SCENARIOS))):.1f}–'
        f'{max(null[n,j][m][0]/(null[n,j][m][2]-null[n,j][m][1])*100 for j in range(len(SCENARIOS))):.1f}'
        for m in methods)) for n in WINDOWS])
    power = {}
    for n in WINDOWS:
        selected = survivors[n] + COMPARES
        for j, scenario in enumerate(SCENARIOS):
            rng = random.Random(SEED + 9000000 + 10000 * n + j)
            for effect in (0.5, 1.0, 2.0):
                power[n, j, effect] = {m: [0, 0, 0] for m in selected}
            for _ in range(POWER_REPS):
                history, days = draw(n, scenario, rng)
                sd = 1 / math.sqrt(1 - scenario[1]**2)
                for effect in (0.5, 1.0, 2.0):
                    drift = [(d, v + effect * sd *
                              (dt.date.fromisoformat(d).toordinal() - BASE - 120) / (n - 1))
                             for d, v in days]
                    accumulate(power[n, j, effect], evaluate(drift, history, n, selected))
        print(f'Power window {n} complete', file=sys.stderr, flush=True)
    print('Power cells: outside_noise / cannot_tell among ALL simulations (%).\n')
    for n in WINDOWS:
        selected = survivors[n] + COMPARES
        print(f'### Power average: {n} days, equal weight to 16 scenarios\n')
        table(('Days', 'Total drift (SD)', *selected), [
            (n, effect, *(cell([sum(power[n,j,effect][m][k] for j in range(len(SCENARIOS)))
                                 for k in range(3)]) for m in selected))
            for effect in (0.5, 1.0, 2.0)])
    for n in WINDOWS:
        selected = survivors[n] + COMPARES
        print(f'### Power detail: {n} days\n')
        table(('Noise', 'Missing', 'Drift (SD)', *selected), [
            (s[0], f'{s[3]:.0%}', effect, *(cell(power[n,j,effect][m]) for m in selected))
            for j, s in enumerate(SCENARIOS) for effect in (0.5, 1.0, 2.0)])
    print(f'Measured wall-clock runtime: {time.perf_counter() - started:.3f} seconds.', flush=True)


if __name__ == '__main__':
    main()
