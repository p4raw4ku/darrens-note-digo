# -*- coding: utf-8 -*-
"""B2 全量：把 run_full_battery.py 落的 json（精簡 GameRecord dict）轉回可餵
metrics.py 既有函式（advantage_series/comeback_rate/tension_metrics/
safety_net_decisive_rate）的物件，彙總出各配對 B6 四指標＋深度報酬曲線。

JSON 序列化會把 hp_by_round 內層 dict 的 int key（0/1）變成字串，這裡讀回
時轉正；log 事件的 side/round 本來就是 int，json 往返不受影響。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
ENGINE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                          'engine'))
sys.path.insert(0, ENGINE_DIR)

import metrics as M  # noqa: E402
import b2_common as B  # noqa: E402

RES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                       'results'))


class _FakeRecord(object):
    __slots__ = ('winner', 'rounds', 'turns', 'log', 'safety_net_triggered',
                'first_mover', 'final_hp', 'hp_by_round', 'reason')

    def __init__(self, d):
        self.winner = d['winner']
        self.rounds = d['rounds']
        self.turns = d.get('turns', d['rounds'])
        self.log = d['log']
        self.safety_net_triggered = d['safety_net_triggered']
        self.first_mover = d['first_mover']
        self.reason = d.get('reason')
        self.final_hp = {int(k): v for k, v in d['final_hp'].items()}
        self.hp_by_round = [(rd, {int(k): v for k, v in hp.items()})
                            for rd, hp in d['hp_by_round']]


def load_direction(direction):
    p = os.path.join(RES_DIR, 'full_battery_dir%d.json' % direction)
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def cell_records(cell):
    return [_FakeRecord(g) for g in cell['games']]


POLICIES = ['greedy_damage', 'oneply', 'twoply']
DEPTH_RANK = {'greedy_damage': 0, 'oneply': 1, 'twoply': 2}
DEPTH_LABEL = {'greedy_damage': 'depth0_greedy', 'oneply': 'depth1_oneply',
              'twoply': 'depth2_twoply'}


def summarize_direction(direction):
    data = load_direction(direction)
    out = {}
    for key, cell in data.items():
        recs = cell_records(cell)
        comeback = M.comeback_rate(recs)
        tension = M.tension_metrics(recs)
        safety = M.safety_net_decisive_rate(recs)
        length = M.game_length_stats(recs)
        out[key] = {
            'a': cell['a'], 'b': cell['b'],
            'a對b勝率_判定局': cell['a對b勝率_判定局'],
            '判定局數': cell['判定局數'], '平局': cell['平局'],
            '長度中位': cell['長度中位'],
            '翻盤率': comeback,
            '張力三量': tension,
            '安全網決定率': safety,
        }
    return out


def depth_reward_curve(direction_summary):
    """深度報酬曲線：depth k+1 對 depth k 的勝率序列（同方向內）。"""
    curve = []
    order = ['greedy_damage', 'oneply', 'twoply']
    for i in range(len(order) - 1):
        lo, hi = order[i], order[i + 1]
        key = '%s_vs_%s' % (hi, lo)
        if key in direction_summary:
            curve.append({
                'depth_low': DEPTH_LABEL[lo], 'depth_high': DEPTH_LABEL[hi],
                'hi對lo勝率': direction_summary[key]['a對b勝率_判定局'],
                '判定局數': direction_summary[key]['判定局數'],
            })
    return curve


def change_navi_analysis(direction, data):
    """dir1 專屬：換角頻率、換角回合與最終勝負相關（觀察性、非讀心增量）。"""
    if direction != 1:
        return None
    out = {}
    for key, cell in data.items():
        if 'twoply' not in (cell['a'], cell['b']):
            continue
        recs = cell_records(cell)
        stats = M.change_navi_stats(recs)
        # 換角回合 vs 最終勝負：分別統計「換角較多的一方」是否較常獲勝
        # （觀察性相關、非因果）。
        corr_hits = 0
        corr_total = 0
        first_change_round_winner = []
        first_change_round_loser = []
        for r in recs:
            if r.winner is None:
                continue
            c = {0: 0, 1: 0}
            first_rd = {0: None, 1: None}
            for e in r.log:
                if e.get('event') == '換角':
                    s = e.get('side')
                    if s is None:
                        continue
                    c[s] += 1
                    if first_rd[s] is None:
                        first_rd[s] = e.get('round')
            corr_total += 1
            more_changer = 0 if c[0] > c[1] else (1 if c[1] > c[0] else None)
            if more_changer is not None and more_changer == r.winner:
                corr_hits += 1
            w, l = r.winner, 1 - r.winner
            if first_rd[w] is not None:
                first_change_round_winner.append(first_rd[w])
            if first_rd[l] is not None:
                first_change_round_loser.append(first_rd[l])
        out[key] = {
            '換角頻率統計': stats,
            '換角較多方即勝方_比例': (corr_hits / corr_total) if corr_total
                                else float('nan'),
            '判定局數': corr_total,
            '勝方首次換角回合_中位': (B.median(first_change_round_winner)
                                if first_change_round_winner else float('nan')),
            '敗方首次換角回合_中位': (B.median(first_change_round_loser)
                                if first_change_round_loser else float('nan')),
        }
    return out


def main():
    result = {}
    for direction in (1, 2, 3):
        p = os.path.join(RES_DIR, 'full_battery_dir%d.json' % direction)
        if not os.path.exists(p):
            print('dir%d 結果尚未產生，略過' % direction)
            continue
        data = load_direction(direction)
        if len(data) < 9:
            print('dir%d 尚未跑滿9配對（現有%d），仍先彙總已完成部分'
                 % (direction, len(data)))
        summary = summarize_direction(direction)
        curve = depth_reward_curve(summary)
        change_navi = change_navi_analysis(direction, data)
        result['dir%d' % direction] = {
            '配對彙總': summary, '深度報酬曲線': curve,
            '換角觀察分析': change_navi,
        }
    out_path = os.path.join(RES_DIR, 'battery_analysis.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print('寫入', out_path)
    for dkey, dval in result.items():
        print('\n=====', dkey, '深度報酬曲線 =====')
        for c in dval['深度報酬曲線']:
            print('  %s -> %s: 勝率=%.3f（判定局=%d）' % (
                c['depth_low'], c['depth_high'], c['hi對lo勝率'],
                c['判定局數']))


if __name__ == '__main__':
    main()
