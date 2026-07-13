# -*- coding: utf-8 -*-
"""B2 全量 步驟2：淺階梯重驗。dir3 上 greedy/oneply/twoply(候選池修正版)
循環賽（含鏡像自對局），看單調性是否恢復。

沿用輪1 b2_pilot 的 seed 約定（同輪1 SEED_BASE=20260705+2*1000、cell_no 編號
與 n_games_for 降規模規則完全相同），唯一差異＝twoply 策略本身已換成候選池
修正版（policies.py 的 TwoPly，第一層/第二層候選皆「top-K=3 ∪ 強制納入
pass+pass」）。恢復與否都續跑全量，但需在報告分開解讀。

單進程；單局超時 120s 記不可行並提前結束該格。
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import b2_common as B

SEED_BASE = 20260705 + 2 * 1000  # 沿用輪1 b2_pilot 實驗號 2 的 seed 約定
DIRECTION = 3
TIMEOUT_S = 120

DEPTH_POLICY = {
    'depth0_greedy': 'greedy_damage',
    'depth1_oneply': 'oneply',
    'depth2_twoply': 'twoply',
}
DEPTHS = ['depth0_greedy', 'depth1_oneply', 'depth2_twoply']


def n_games_for(a, b):
    if 'depth2_twoply' in (a, b):
        return 20, True  # 降規模、沿用輪1標明
    return 40, False


def run_pair(a, b, cell_no):
    n_games, reduced = n_games_for(a, b)
    pol_a, pol_b = DEPTH_POLICY[a], DEPTH_POLICY[b]
    wins = {0: 0, 1: 0}
    draws = 0
    infeasible = False
    n_done = 0
    lengths = []
    for i in range(n_games):
        seed = SEED_BASE + 3000 + cell_no * 1000 + i
        fm = i % 2
        rec, dt, timed_out = B.timed_play_one(DIRECTION, pol_a, pol_b, seed,
                                              first_mover=fm,
                                              timeout_s=TIMEOUT_S)
        if timed_out:
            infeasible = True
            break
        n_done += 1
        lengths.append(rec.rounds)
        if rec.winner is None:
            draws += 1
        else:
            wins[rec.winner] += 1
    decisive = wins[0] + wins[1]
    a_winrate = wins[0] / decisive if decisive else float('nan')
    return {
        'a': a, 'b': b, 'n_requested': n_games, 'n_done': n_done,
        'reduced_sample': reduced, 'infeasible': infeasible,
        'a側勝': wins[0], 'b側勝': wins[1], '平局': draws,
        '判定局數': decisive, 'a對b勝率_判定局': a_winrate,
        '長度中位': B.median(lengths) if lengths else float('nan'),
    }


def main():
    out = []
    cell_no = 0
    for a in DEPTHS:
        for b in DEPTHS:
            t0 = time.time()
            cell = run_pair(a, b, cell_no)
            cell['secs'] = round(time.time() - t0, 2)
            out.append(cell)
            print('[%s vs %s] n=%d(降規模=%s) a勝率(判定局)=%.3f 判定局=%d '
                  '平局=%d（%.1fs）' % (
                      a, b, cell['n_done'], cell['reduced_sample'],
                      cell['a對b勝率_判定局'], cell['判定局數'], cell['平局'],
                      cell['secs']))
            cell_no += 1
        # 每方向（此處單方向 dir3）跑完所有 b 就落一次盤，斷點可續
        res_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                               '..', 'results'))
        os.makedirs(res_dir, exist_ok=True)
        with open(os.path.join(res_dir, 'ladder_r2.json'), 'w',
                  encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
    return out


if __name__ == '__main__':
    main()
