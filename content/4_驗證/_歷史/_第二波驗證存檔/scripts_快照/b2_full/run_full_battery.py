# -*- coding: utf-8 -*-
"""B2 全量 步驟3：3方向 × {greedy, oneply, twoply修} × 9配對/方向、
每配對 n=100。v1.1 檔位、先手輪替、seed 約定＝
20260706 + 方向×10000 + 配對號×100 + 局號。

dir1 的 9 配對優先起跑（含 oneply，佔全量約75%耗時）、每配對完成即落
json（斷點可續）。單進程、前景執行、無 multiprocessing。

方向 2 用 make_dir2_v11_config（含 resource_enabled=True、resource_rate=2，
沿用 b2_common 既有函式，無需另建）；方向 1 用 make_dir1_v11_config
（HP47/安全網基值3步幅3，B2 先導既有函式，本檔沿用不重算數值）。

每局同時計算最小逐局特徵，事後餵給 metrics.py 算 B6 四指標與勝率/長度。

【修正記錄】首次全量電池 dir2 用了 b2_common.build_dir2_game 的預設防禦原型
（proto_a='游擊'閃8盾15、proto_b='壁壘'場10盾25——不對稱，壁壘明顯更硬），
導致 dir2 全部9配對呈現「side0（不論策略/先手）幾乎從未獲勝」的假象（round1
A6 報告已明訂：純策略勝率電池一律用『鏡像原型（游擊/游擊）』隔離防禦不對稱，
不對稱原型只用於『對位健康』類實驗）。已改為呼叫 timed_play_one 時對 dir2
顯式傳入 dir2_proto_a=dir2_proto_b='游擊'（鏡像），dir2 需整批重跑。
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import b2_common as B

SEED_BASE = 20260706
POLICIES = ['greedy_damage', 'oneply', 'twoply']
DIRECTIONS_ORDER = [1, 3, 2]  # dir1 優先起跑（規格：dir1 oneply 配對佔75%耗時）

RES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                       'results'))
os.makedirs(RES_DIR, exist_ok=True)

TIMEOUT_S = 120
N_PER_PAIR = 100

# 先導 p90（single-game wallclock，供偏離監看比對，見 b2_pilot 報告步驟2/4）
PILOT_P90 = {
    (1, 'greedy_damage'): 0.1060, (1, 'oneply'): 18.3293, (1, 'twoply'): 0.2781,
    (3, 'greedy_damage'): 0.0322, (3, 'oneply'): 0.9997, (3, 'twoply'): 0.1095,
    (2, 'greedy_damage'): 0.0833, (2, 'oneply'): 3.6109, (2, 'twoply'): 0.2688,
}


def pair_index(direction):
    """(a, b) 依 POLICIES×POLICIES 排序，回傳配對號（0-8）。"""
    idx = 0
    out = []
    for a in POLICIES:
        for b in POLICIES:
            out.append((idx, a, b))
            idx += 1
    return out


def result_path(direction):
    return os.path.join(RES_DIR, 'full_battery_dir%d.json' % direction)


def load_existing(direction):
    p = result_path(direction)
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_existing(direction, data):
    p = result_path(direction)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run_cell(direction, a, b, pair_no):
    """跑一個配對 n=100，回傳逐局精簡紀錄＋彙總。"""
    wins = {0: 0, 1: 0}
    draws = 0
    lengths = []
    times = []
    infeasible_count = 0
    game_recs_min = []   # 精簡逐局資料：winner/rounds/hp_by_round/log 摘要
    for i in range(N_PER_PAIR):
        seed = SEED_BASE + direction * 10000 + pair_no * 100 + i
        fm = i % 2
        t0 = time.time()
        rec, dt, timed_out = B.timed_play_one(direction, a, b, seed,
                                              first_mover=fm,
                                              timeout_s=TIMEOUT_S,
                                              dir2_proto_a='游擊',
                                              dir2_proto_b='游擊')
        times.append(dt)
        if timed_out:
            infeasible_count += 1
            continue
        lengths.append(rec.rounds)
        if rec.winner is None:
            draws += 1
        else:
            wins[rec.winner] += 1
        game_recs_min.append({
            'seed': seed, 'first_mover': fm, 'winner': rec.winner,
            'rounds': rec.rounds, 'reason': rec.reason,
            'safety_net_triggered': rec.safety_net_triggered,
            'final_hp': rec.final_hp,
            'hp_by_round': rec.hp_by_round,
            'log': [e for e in rec.log
                    if e.get('event') in ('換角', '強制換入', '自攻', '晶片能力',
                                          '領航員能力攻擊', '安全網')],
        })
    decisive = wins[0] + wins[1]
    a_winrate = wins[0] / decisive if decisive else float('nan')
    return {
        'direction': direction, 'a': a, 'b': b, 'pair_no': pair_no,
        'n_requested': N_PER_PAIR, 'n_done': len(times) - infeasible_count,
        'infeasible_count': infeasible_count,
        'a側勝': wins[0], 'b側勝': wins[1], '平局': draws,
        '判定局數': decisive, 'a對b勝率_判定局': a_winrate,
        '長度中位': B.median(lengths) if lengths else float('nan'),
        '單局秒數_中位': B.median(times), '單局秒數_p90': B.percentile(times, 90),
        'games': game_recs_min,
    }


def check_pilot_deviation(direction, a, b, cell):
    """dir1 oneply 配對優先起跑時的偏離監看：對照先導 p90，偏離3倍即標警。"""
    warn = []
    for pol in (a, b):
        key = (direction, pol)
        if key in PILOT_P90 and PILOT_P90[key] > 0:
            ratio = cell['單局秒數_p90'] / PILOT_P90[key]
            if ratio >= 3.0:
                warn.append('%s p90=%.4fs 為先導p90(%.4fs)的%.1f倍（>=3倍偏離警戒）'
                            % (pol, cell['單局秒數_p90'], PILOT_P90[key], ratio))
    return warn


def main():
    all_warnings = []
    t_start = time.time()
    for direction in DIRECTIONS_ORDER:
        existing = load_existing(direction)
        pairs = pair_index(direction)
        print('\n===== 方向%d：%d 配對 =====' % (direction, len(pairs)))
        for pair_no, a, b in pairs:
            key = '%s_vs_%s' % (a, b)
            if key in existing:
                print('[dir%d %s] 已有結果，跳過（斷點續跑）' % (direction, key))
                continue
            t0 = time.time()
            cell = run_cell(direction, a, b, pair_no)
            cell['secs'] = round(time.time() - t0, 2)
            existing[key] = cell
            save_existing(direction, existing)   # 每配對完成即落 json
            print('[dir%d %s vs %s] n完成=%d a勝率(判定)=%.3f 判定局=%d '
                  '平局=%d 長度中位=%.1f 單局p90=%.3fs（%.1fs）' % (
                      direction, a, b, cell['n_done'],
                      cell['a對b勝率_判定局'], cell['判定局數'], cell['平局'],
                      cell['長度中位'], cell['單局秒數_p90'], cell['secs']))
            if direction == 1 and 'oneply' in (a, b):
                warns = check_pilot_deviation(direction, a, b, cell)
                for w in warns:
                    msg = '[偏離警戒][dir%d %s]：%s' % (direction, key, w)
                    print(msg)
                    all_warnings.append(msg)
    total_secs = time.time() - t_start
    print('\n全量電池總耗時 %.1f 秒 ≈ %.2f 小時' % (total_secs, total_secs / 3600))
    if all_warnings:
        print('\n=== 偏離警戒彙總 ===')
        for w in all_warnings:
            print(w)
    with open(os.path.join(RES_DIR, 'full_battery_meta.json'), 'w',
              encoding='utf-8') as f:
        json.dump({'total_secs': total_secs, 'warnings': all_warnings},
                  f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
