# -*- coding: utf-8 -*-
"""終代 top-3 基因型對四基線（含 random_legal）n=200 覆核。"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'round1', 'work',
                                'b6_engine_v2'))

from evolve import fitness, gen_seed, N_PER_GEN  # noqa: E402

ALL_BASELINES = ['greedy_damage', 'turtle', 'positional', 'random_legal']


def verify_one(weights, tag, n_games=200, samples=4):
    """對四基線各自算勝率（先後手輪替、平局折半）。"""
    from evolve import play_one
    out = {}
    for bname in ALL_BASELINES:
        total = 0.0
        cnt = 0
        per_side = n_games // 2
        base_seed = (20260706 + 9000 + hash(tag + bname) % 100000)
        for i in range(per_side):
            score, _ = play_one(weights, bname, True, base_seed * 1000 + i,
                                samples=samples)
            total += score
            cnt += 1
        for i in range(per_side):
            score, _ = play_one(weights, bname, False,
                                base_seed * 1000 + 100000 + i,
                                samples=samples)
            total += score
            cnt += 1
        out[bname] = total / cnt if cnt else 0.0
    return out


if __name__ == '__main__':
    ckpt = json.load(open(os.path.join(HERE, 'checkpoint.json'), encoding='utf-8'))
    pop = ckpt['pop']
    top3 = pop[:3]
    n_games = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    results = []
    for idx, w in enumerate(top3):
        t0 = time.time()
        res = verify_one(w, 'top%d' % idx, n_games=n_games, samples=4)
        dt = time.time() - t0
        print('[top%d] %s (%.1fs)' % (idx, res, dt))
        results.append({'rank': idx, 'genome': w, 'winrates': res, 'wall_s': dt})
    with open(os.path.join(HERE, 'top3_verify.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
