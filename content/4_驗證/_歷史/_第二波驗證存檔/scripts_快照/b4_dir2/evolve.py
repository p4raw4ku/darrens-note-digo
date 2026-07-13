# -*- coding: utf-8 -*-
"""B4 演化漏洞搜索主程式（純方向二 v1.1）。

族群 24、菁英 4、錦標賽選擇 3、交叉均勻、突變 sigma=0.2（逐維高斯）。
適應度＝對基線混合池（greedy_damage/turtle/positional 各 1/3，先後手輪替，
平局折半）勝率，每個體每代 n=60。

seed 約定：20260706 + 7000 + 世代*100 + 個體號。

斷點：每代完成即落 json（round3/work/b4_dir2/checkpoint.json）。
"""
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', 'round1', 'work',
                 'b6_engine_v2')))

from core import GameConfig
from setups import build
from policies import make_policy
from evo_policy import EvoPolicy, N_FEATURES

HERE = os.path.dirname(os.path.abspath(__file__))
CKPT_PATH = os.path.join(HERE, 'checkpoint.json')

POP_SIZE = 24
ELITE = 4
TOURNEY_K = 3
MUT_SIGMA = 0.2
EPSILON = 0.05
BASELINES = ['greedy_damage', 'turtle', 'positional']
N_PER_GEN = 60   # 每個體每代對戰局數（分攤到 3 基線 x 先後手）

SEED_BASE = 20260706 + 7000


def gen_seed(gen, indiv):
    return SEED_BASE + gen * 100 + indiv


def make_base_cfg(seed):
    return GameConfig(
        direction=2, hp=100, first_turn_comp='一行動', dodge_mode='機率制',
        field_overload='關', safety_net_turn=15, max_turns=60, seed=seed,
        oneply_samples=30, expect_samples=30)


def _clone_cfg(cfg, seed):
    return GameConfig(
        direction=cfg.direction, hp=cfg.hp,
        first_turn_comp=cfg.first_turn_comp, dodge_mode=cfg.dodge_mode,
        field_overload=cfg.field_overload, safety_net_turn=cfg.safety_net_turn,
        max_turns=cfg.max_turns, seed=seed,
        oneply_samples=cfg.oneply_samples, expect_samples=cfg.expect_samples,
        hand_limit=cfg.hand_limit, draw_per_turn=cfg.draw_per_turn,
        starting_hand=cfg.starting_hand, extra=dict(cfg.extra))


def play_one(weights, baseline_name, evo_is_first, seed, samples=None):
    cfg = _clone_cfg(make_base_cfg(seed), seed)
    eng, setup = build(2, cfg, proto_a='游擊', proto_b='壁壘')
    evo_pol = EvoPolicy(weights, epsilon=EPSILON, samples=samples)
    base_pol = make_policy(baseline_name)
    if evo_is_first:
        rec = eng.play(cfg, setup, evo_pol, base_pol)
        evo_side = 0
    else:
        rec = eng.play(cfg, setup, base_pol, evo_pol)
        evo_side = 1
    if rec.winner is None:
        return 0.5, rec
    return (1.0 if rec.winner == evo_side else 0.0), rec


def fitness(weights, gen, indiv, n_games=N_PER_GEN, samples=None,
            return_records=False):
    """對三基線混合池、先後手輪替，平局折半。"""
    per_cell = max(1, n_games // (len(BASELINES) * 2))
    total = 0.0
    count = 0
    records = []
    base_seed = gen_seed(gen, indiv)
    i = 0
    for bname in BASELINES:
        for evo_first in (True, False):
            for k in range(per_cell):
                seed = base_seed * 1000 + i
                i += 1
                score, rec = play_one(weights, bname, evo_first, seed,
                                      samples=samples)
                total += score
                count += 1
                if return_records:
                    records.append((bname, evo_first, seed, score, rec))
    return total / count if count else 0.0, records


def random_genome(rng):
    return [rng.gauss(0, 1.0) for _ in range(N_FEATURES)]


def mutate(w, rng, sigma=MUT_SIGMA):
    return [wi + rng.gauss(0, sigma) for wi in w]


def crossover(w1, w2, rng):
    return [w1[i] if rng.random() < 0.5 else w2[i] for i in range(N_FEATURES)]


def tournament_select(pop_scored, rng, k=TOURNEY_K):
    cand = rng.sample(pop_scored, k)
    cand.sort(key=lambda x: -x[1])
    return cand[0][0]


def save_checkpoint(state):
    with open(CKPT_PATH, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_checkpoint():
    if os.path.exists(CKPT_PATH):
        with open(CKPT_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def run_evolution(n_gens, n_games_per_gen, samples, log_fn=print):
    rng = random.Random(20260706)
    ckpt = load_checkpoint()
    if ckpt is not None:
        pop = ckpt['pop']
        start_gen = ckpt['next_gen']
        history = ckpt['history']
        log_fn('[續跑] 從第 %d 代繼續（已有 %d 代歷史）' % (start_gen, len(history)))
    else:
        pop = [random_genome(rng) for _ in range(POP_SIZE)]
        start_gen = 0
        history = []

    for gen in range(start_gen, n_gens):
        t0 = time.time()
        scored = []
        for idx, w in enumerate(pop):
            fit, _ = fitness(w, gen, idx, n_games=n_games_per_gen,
                             samples=samples)
            scored.append((w, fit))
        scored.sort(key=lambda x: -x[1])
        best_fit = scored[0][1]
        avg_fit = sum(s[1] for s in scored) / len(scored)
        # 多樣性量測：權重向量歐氏距離的平均（粗量）
        div = _diversity(scored)
        dt = time.time() - t0
        history.append({'gen': gen, 'best_fit': best_fit, 'avg_fit': avg_fit,
                        'diversity': div, 'wall_s': dt,
                        'best_genome': scored[0][0]})
        log_fn('[gen %d] best=%.3f avg=%.3f div=%.3f wall=%.1fs'
              % (gen, best_fit, avg_fit, div, dt))

        # 產生下一代
        elites = [w for w, f in scored[:ELITE]]
        next_pop = [list(w) for w in elites]
        while len(next_pop) < POP_SIZE:
            p1 = tournament_select(scored, rng)
            p2 = tournament_select(scored, rng)
            child = crossover(p1, p2, rng)
            child = mutate(child, rng)
            next_pop.append(child)
        pop = next_pop

        save_checkpoint({'pop': pop, 'next_gen': gen + 1, 'history': history})

    return history, pop, scored


def _diversity(scored):
    ws = [w for w, f in scored]
    n = len(ws)
    if n < 2:
        return 0.0
    tot = 0.0
    cnt = 0
    for i in range(n):
        for j in range(i + 1, n):
            d = sum((ws[i][k] - ws[j][k]) ** 2 for k in range(N_FEATURES)) ** 0.5
            tot += d
            cnt += 1
    return tot / cnt if cnt else 0.0


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--gens', type=int, default=10)
    ap.add_argument('--games', type=int, default=N_PER_GEN)
    ap.add_argument('--samples', type=int, default=6)
    ap.add_argument('--timing-only', action='store_true')
    args = ap.parse_args()

    if args.timing_only:
        t0 = time.time()
        fit, _ = fitness(random_genome(random.Random(1)), 0, 0,
                         n_games=args.games, samples=args.samples)
        dt = time.time() - t0
        print('單代單個體 fitness 耗時 %.2fs（fit=%.3f, games=%d）'
             % (dt, fit, args.games))
        print('推估單代（族群 %d）壁鐘 ~%.1fs' % (POP_SIZE, dt * POP_SIZE))
    else:
        run_evolution(args.gens, args.games, args.samples)
