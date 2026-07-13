# -*- coding: utf-8 -*-
"""B4 演化漏洞搜索：純方向二 v1.1 線性基因策略。

基因 w（12 維）+ epsilon 探索率。決策：對每個合法 pair 算特徵分
s = w·f(pair,state)，取最高分（ε 機率隨機合法）。特徵全部從既有引擎介面讀，
不改引擎。

特徵向量 f（12 維，索引與說明）：
  0 期望淨傷（_expected_pair_damage，與 greedy 同一把尺）
  1 自身受擊曝險（施行後敵方能否打我，1=會被打中→取負向，特徵存 -1/0）
  2 與敵距離變化（after-before，正值＝拉開距離）
  3 資源球最短距離變化（正值＝更接近資源）
  4 是否拾取資源（0/1）
  5 是否佈陷阱（0/1）
  6 是否位移敵人（推/拉命中，0/1，近似：pair 含 16/17 號晶片能力面且命中）
  7 移動面被選次數（0/1/2，含晶片移動面與核心移動行動）
  8 能力面被選次數（0/1/2，晶片能力面）
  9 pass 數（0/1/2）
  10 距安全網回合數的倒數 1/(1+remain)（remain=safety_net_turn-round_no，越接近
     安全網此值越大——拖延型基因會給高權重，用來測「爬頂」）
  11 bias（恒為 1）

介面對齊 policies.Policy：choose_actions(st, side, rng, engine)。
"""
import random

from core import Action, manhattan, range_can_reach
from policies import (_apply_pair_sim, _expected_pair_damage,
                       _enemy_min_distance_after, _enemy_can_hit_me_next,
                       _decision_seed, _sub_rng, _pair_move_count,
                       _auto_target)

N_FEATURES = 12


def _resource_min_dist(pos, resource_cells):
    if not resource_cells:
        return 99
    return min(manhattan(pos, c) for c in resource_cells)


def _pair_uses_ability_face(pair):
    n = 0
    for a in pair:
        if a.kind == '晶片' and a.face == '能力':
            n += 1
    return n


def _pair_is_pass_count(pair):
    return sum(1 for a in pair if a.kind == 'pass')


def _pair_picks_up_resource(st, side, pair, engine, rng):
    """近似：施行後本方是否比施行前多了資源顆數。"""
    before = st.resources[side]
    dup, _ = _apply_pair_sim(engine, st, side, pair, rng)
    after = dup.resources[side]
    return 1 if after > before else 0


def _pair_lays_trap(pair):
    for a in pair:
        if a.kind == '晶片' and a.face == '能力' and a.chip_id == 18:
            return 1
    return 0


def _pair_displaces_enemy(st, side, pair, engine, rng):
    """近似：施行前後敵方位置是否改變（推/拉命中的代理，晶片16/17）。"""
    foe = 1 - side
    before = st.units[foe].pos if st.units[foe] else None
    dup, _ = _apply_pair_sim(engine, st, side, pair, rng)
    after = dup.units[foe].pos if dup.units[foe] and dup.units[foe].alive else before
    if before is None or after is None:
        return 0
    return 1 if before != after else 0


def extract_features(st, side, pair, engine, rng, samples):
    """回傳長度 N_FEATURES 的 list[float]。"""
    ds = _decision_seed(rng)
    me = st.units[side]
    foe_side = 1 - side
    foe = st.units[foe_side]
    dist_before = manhattan(me.pos, foe.pos) if (me and foe) else 0

    sub0 = _sub_rng(ds, pair, 0)
    dmg = _expected_pair_damage(engine, st, side, pair, sub0, samples)

    sub1 = _sub_rng(ds, pair, 1)
    dist_after = _enemy_min_distance_after(engine, st, side, pair, sub1)
    dist_delta = (dist_after - dist_before) if dist_after < 90 else 0

    sub2 = _sub_rng(ds, pair, 2)
    risky = _enemy_can_hit_me_next(engine, st, side, pair, sub2)
    exposure = -1.0 if risky else 0.0

    res_before = _resource_min_dist(me.pos, st.resource_cells) if me else 99
    sub3 = _sub_rng(ds, pair, 3)
    dup3, _ = _apply_pair_sim(engine, st, side, pair, sub3)
    me_after = dup3.units[side]
    res_after = (_resource_min_dist(me_after.pos, dup3.resource_cells)
                 if me_after and me_after.alive else 99)
    res_delta = 0
    if res_before < 90 and res_after < 90:
        res_delta = res_before - res_after   # 正值＝更接近

    sub4 = _sub_rng(ds, pair, 4)
    picked = _pair_picks_up_resource(st, side, pair, engine, sub4)

    trapped = _pair_lays_trap(pair)

    sub5 = _sub_rng(ds, pair, 5)
    displaced = _pair_displaces_enemy(st, side, pair, engine, sub5)

    move_n = _pair_move_count(pair)
    ability_n = _pair_uses_ability_face(pair)
    pass_n = _pair_is_pass_count(pair)

    remain = max(0, st.config.safety_net_turn - st.round_no)
    net_proximity = 1.0 / (1.0 + remain)

    return [
        dmg, exposure, float(dist_delta), float(res_delta),
        float(picked), float(trapped), float(displaced),
        float(move_n), float(ability_n), float(pass_n),
        net_proximity, 1.0,
    ]


class EvoPolicy(object):
    """線性權重演化基因策略。name 依 genome 動態命名以利日誌辨識。"""
    name = 'evo_dir2'

    def __init__(self, weights, epsilon=0.05, samples=None, tag=None):
        assert len(weights) == N_FEATURES
        self.w = list(weights)
        self.epsilon = epsilon
        self.samples = samples
        self.tag = tag or 'evo'

    def choose_actions(self, st, side, rng, engine):
        first_comp = None
        if (st.config.first_turn_comp == '一行動'
                and st.round_no == 1 and side == st.first_mover):
            first_comp = '一行動'
        pairs = engine.legal_action_pairs(st, side, first_comp)
        if self.epsilon > 0 and rng.random() < self.epsilon:
            return list(rng.choice(pairs))
        samples = self.samples or max(1, st.config.expect_samples // 2 or 1)
        best = None
        best_score = None
        for pair in pairs:
            feat = extract_features(st, side, pair, engine, rng, samples)
            score = sum(wi * fi for wi, fi in zip(self.w, feat))
            if best_score is None or score > best_score:
                best_score = score
                best = pair
        return list(best)
