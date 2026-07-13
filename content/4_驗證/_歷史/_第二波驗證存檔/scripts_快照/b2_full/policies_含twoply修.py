# -*- coding: utf-8 -*-
"""DIGO_EXE 策略套件（共用五策略，契約 §三）。

Policy 介面：choose_actions(state, side, rng, engine) -> [Action, Action]
  一律經 engine.legal_action_pairs / legal_actions 取合法選項，策略不自算合法性。

五策略：
  random_legal   合法隨機
  greedy_damage  最大化本回合期望傷害
  turtle         最大化與敵距離與防禦、僅打零風險目標（會真的走位）
  positional     最大化下回合射程覆蓋與機動（會真的走位）
  oneply         枚舉自己兩行動組合、對手回應抽樣，取期望最優

turtle 與 positional 必須真的會走位——本檔用「模擬施行行動組合、看走位後盤面」
評分，走位帶來的距離/覆蓋改善會反映在分數，因此位移動作會被選中。
期望值抽樣一律用傳入 rng 的固定序列（可重現）。
"""
from core import (Action, resolve_attack, cells_hit, enumerate_targets,
                  range_can_reach, row_dist, col_dist, manhattan, advance_dir,
                  own_rows)


# ==================================================================
# 共用工具
# ==================================================================

def _apply_pair_sim(engine, st, side, pair, rng):
    """在複本上施行一組（≤2）行動，回傳 (複本, 本方造成的傷害)。"""
    dup = st.sim_clone()
    used = set()
    dealt = 0
    for act in pair:
        if act.category() != 'pass':
            if act.category() in used:
                continue
            used.add(act.category())
        dealt += engine.apply_action(dup, side, act, rng)
        if dup.units[1 - side] is None or not dup.units[1 - side].alive:
            break
    return dup, dealt


def _damage_is_deterministic(st, target_side):
    """對 target_side 造成的傷害是否無亂數（→ 一次施行即精確）。

    傷害唯一亂數源＝機率制閃避且目標有閃避值。行動施行不觸發抽牌洗牌，
    故其餘皆確定。方向一 3對3 也只一名上場，判上場者即可。
    """
    if st.config.dodge_mode != '機率制':
        return True
    u = st.units[target_side]
    if u is None:
        return True
    return u.evasion == 0


def _expected_pair_damage(engine, st, side, pair, rng, samples):
    """對一組行動抽樣估計期望造成傷害（含亂數閃避影響）。

    確定性情形（目標無機率制閃避）只施行一次，省抽樣。
    """
    if _damage_is_deterministic(st, 1 - side):
        _, dealt = _apply_pair_sim(engine, st, side, pair, rng)
        return float(dealt)
    total = 0.0
    for _ in range(samples):
        _, dealt = _apply_pair_sim(engine, st, side, pair, rng)
        total += dealt
    return total / samples


def _enemy_min_distance_after(engine, st, side, pair, rng):
    """施行 pair 後，本方單位與敵方單位的曼哈頓距離（越大越安全）。"""
    dup, _ = _apply_pair_sim(engine, st, side, pair, rng)
    me = dup.units[side]
    foe = dup.units[1 - side]
    if me is None or foe is None or not me.alive or not foe.alive:
        return 99
    return manhattan(me.pos, foe.pos)


def _enemy_can_hit_me_next(engine, st, side, pair, rng):
    """粗估：施行 pair 後，敵方自身攻擊是否命中我（近似風險）。"""
    dup, _ = _apply_pair_sim(engine, st, side, pair, rng)
    me = dup.units[side]
    foe = dup.units[1 - side]
    if me is None or foe is None or not me.alive or not foe.alive:
        return False
    rk, rp, dmg, hits = foe.navi_attack
    spec = (rk, rp) if rp is not None else (rk,)
    my_pos = {side: me.pos}
    return range_can_reach(foe.pos, 1 - side, spec, _auto_target(spec, foe.pos, 1 - side, my_pos), my_pos)


def _auto_target(spec, att_pos, att_side, enemy_positions):
    """幫需要 target 的範圍挑第一個能命中的瞄準點（近似）。"""
    from core import enumerate_targets as _et
    tgs = _et(att_pos, att_side, spec, enemy_positions)
    return tgs[0] if tgs else None


def _my_coverage_after(engine, st, side, pair, rng):
    """施行 pair 後，本方手牌＋自攻在下一步能覆蓋的敵方格數（射程覆蓋代理）。"""
    dup, _ = _apply_pair_sim(engine, st, side, pair, rng)
    me = dup.units[side]
    foe = dup.units[1 - side]
    if me is None or foe is None or not me.alive or not foe.alive:
        return 0
    enemy_pos = {1 - side: foe.pos}
    covered = 0
    # 自攻
    rk, rp, d, h = me.navi_attack
    spec = (rk, rp) if rp is not None else (rk,)
    if range_can_reach(me.pos, side, spec, _auto_target(spec, me.pos, side, enemy_pos), enemy_pos):
        covered += 1
    # 手牌能力面攻擊
    for cid in set(dup.hands[side]):
        chip = engine.chips[cid]
        ab = chip.ability_face
        if ab['type'] != 'attack':
            continue
        rspec = ab['range']
        if range_can_reach(me.pos, side, rspec, _auto_target(rspec, me.pos, side, enemy_pos), enemy_pos):
            covered += 1
    return covered


# ==================================================================
# 策略類
# ==================================================================

class Policy(object):
    name = 'base'

    def choose_actions(self, st, side, rng, engine):
        raise NotImplementedError


class RandomLegal(Policy):
    name = 'random_legal'

    def choose_actions(self, st, side, rng, engine):
        first_comp = None
        if (st.config.first_turn_comp == '一行動'
                and st.round_no == 1 and side == st.first_mover):
            first_comp = '一行動'
        pairs = engine.legal_action_pairs(st, side, first_comp)
        return list(rng.choice(pairs))


class GreedyDamage(Policy):
    """最大化本回合期望傷害；平手時偏好保留移動/位置（挑距離較大者）。"""
    name = 'greedy_damage'

    def choose_actions(self, st, side, rng, engine):
        first_comp = None
        if (st.config.first_turn_comp == '一行動'
                and st.round_no == 1 and side == st.first_mover):
            first_comp = '一行動'
        pairs = engine.legal_action_pairs(st, side, first_comp)
        samples = max(1, st.config.expect_samples)
        ds = _decision_seed(rng)
        best = None
        best_key = None
        for pair in pairs:
            # 用固定衍生 rng 讓每 pair 抽樣序列一致、可重現
            sub = _sub_rng(ds, pair)
            dmg = _expected_pair_damage(engine, st, side, pair, sub, samples)
            dist = _enemy_min_distance_after(engine, st, side, pair, _sub_rng(ds, pair, 1))
            key = (round(dmg, 3), dist)
            if best_key is None or key > best_key:
                best_key = key
                best = pair
        return list(best)


class Turtle(Policy):
    """最大化與敵距離與防禦、僅打零風險目標。真的會走位（拉開距離得分）。"""
    name = 'turtle'

    def choose_actions(self, st, side, rng, engine):
        first_comp = None
        if (st.config.first_turn_comp == '一行動'
                and st.round_no == 1 and side == st.first_mover):
            first_comp = '一行動'
        pairs = engine.legal_action_pairs(st, side, first_comp)
        samples = max(1, st.config.expect_samples // 2 or 1)
        ds = _decision_seed(rng)
        best = None
        best_key = None
        for pair in pairs:
            sub = _sub_rng(ds, pair)
            dmg = _expected_pair_damage(engine, st, side, pair, sub, samples)
            dist = _enemy_min_distance_after(engine, st, side, pair, _sub_rng(ds, pair, 1))
            # 零風險目標：施行後敵方是否能打到我
            risky = _enemy_can_hit_me_next(engine, st, side, pair, _sub_rng(ds, pair, 2))
            # 只在零風險時把傷害計入（僅打零風險目標）
            safe_dmg = dmg if not risky else 0.0
            has_heal = _pair_uses_heal(engine, pair)
            # 排序鍵：優先無風險 > 距離大 > 有回復 > 順帶傷害
            key = (0 if risky else 1, dist, 1 if has_heal else 0, round(safe_dmg, 3))
            if best_key is None or key > best_key:
                best_key = key
                best = pair
        return list(best)


class Positional(Policy):
    """最大化下回合射程覆蓋與機動；真的會走位（覆蓋提升得分）。"""
    name = 'positional'

    def choose_actions(self, st, side, rng, engine):
        first_comp = None
        if (st.config.first_turn_comp == '一行動'
                and st.round_no == 1 and side == st.first_mover):
            first_comp = '一行動'
        pairs = engine.legal_action_pairs(st, side, first_comp)
        samples = max(1, st.config.expect_samples // 2 or 1)
        ds = _decision_seed(rng)
        best = None
        best_key = None
        for pair in pairs:
            sub = _sub_rng(ds, pair)
            dmg = _expected_pair_damage(engine, st, side, pair, sub, samples)
            cover = _my_coverage_after(engine, st, side, pair, _sub_rng(ds, pair, 1))
            mobility = _pair_move_count(pair)
            # 有立即傷害先拿；否則追求覆蓋與機動
            key = (round(dmg, 3), cover, mobility)
            if best_key is None or key > best_key:
                best_key = key
                best = pair
        return list(best)


class OnePly(Policy):
    """枚舉自己兩行動組合、對手回應抽樣，取期望最優。

    價值＝（本回合造成傷害）−（對手最佳回應對我造成的期望傷害）。
    對手回應用抽樣枚舉：對每個我方 pair，模擬到對手手上，枚舉對手 pair 取其
    最大化『對我傷害』的一組，抽樣估期望。樣本數＝config.oneply_samples。
    """
    name = 'oneply'

    def choose_actions(self, st, side, rng, engine):
        first_comp = None
        if (st.config.first_turn_comp == '一行動'
                and st.round_no == 1 and side == st.first_mover):
            first_comp = '一行動'
        pairs = engine.legal_action_pairs(st, side, first_comp)
        n_opp = max(1, st.config.oneply_samples)
        ds = _decision_seed(rng)
        best = None
        best_val = None
        for pair in pairs:
            val = self._pair_value(engine, st, side, pair, ds, n_opp)
            # 平手偏好較高機動與覆蓋（避免退化成站樁）
            tie = _pair_move_count(pair) + _my_coverage_after(
                engine, st, side, pair, _sub_rng(ds, pair, 9)) * 0.1
            key = (round(val, 3), round(tie, 3))
            if best_val is None or key > best_val:
                best_val = key
                best = pair
        return list(best)

    def _pair_value(self, engine, st, side, pair, ds, n_opp):
        """價值＝我方造成傷害（抽樣期望）− 對手最佳回應對我造成傷害（抽樣期望）。

        兩段隨機源分開估：
          1) 我方傷害：抽 n_opp 次我方 pair 施行，取平均。
          2) 對手回應：在『代表性後態』（單次施行）上，枚舉對手 pair、各以
             少量抽樣估其對我期望傷害，取最大——此枚舉每個我方 pair 只做一次，
             把成本從 O(pairs·samples·opppairs) 降到 O(pairs·(samples+opppairs·k))。
        """
        foe_side = 1 - side
        # 我方傷害：確定性（對手無機率制閃避）只跑一次
        if _damage_is_deterministic(st, foe_side):
            rep_state, my_exp = _apply_pair_sim(engine, st, side, pair,
                                                _sub_rng(ds, pair, 100))
            my_exp = float(my_exp)
        else:
            my_dmg_total = 0.0
            rep_state = None
            for s in range(n_opp):
                sub = _sub_rng(ds, pair, 100 + s)
                dup, my_dealt = _apply_pair_sim(engine, st, side, pair, sub)
                my_dmg_total += my_dealt
                if s == 0:
                    rep_state = dup   # 代表性後態
            my_exp = my_dmg_total / n_opp
        # 對手回應：代表態上已倒＝對我 0
        if (rep_state.units[foe_side] is None
                or not rep_state.units[foe_side].alive):
            return my_exp
        opp_exp = self._opp_best_response(engine, rep_state, foe_side, ds, pair)
        return my_exp - opp_exp

    def _opp_best_response(self, engine, dup, foe_side, ds, my_pair):
        """對手枚舉自己的 pair，取對我期望傷害最大者。每 opp pair 抽少量樣本。

        對手打的是我（side = 1-foe_side）。若我無機率制閃避→確定性、單次即精確。
        """
        opp_pairs = engine.legal_action_pairs(dup, foe_side, None)
        my_side = 1 - foe_side
        deterministic = _damage_is_deterministic(dup, my_side)
        k = 1 if deterministic else 8
        best = 0.0
        for oi, opair in enumerate(opp_pairs):
            if deterministic:
                sub = _sub_rng(ds, my_pair, 500 + oi * 31)
                _, dealt = _apply_pair_sim(engine, dup, foe_side, opair, sub)
                avg = float(dealt)
            else:
                tot = 0.0
                for j in range(k):
                    sub = _sub_rng(ds, my_pair, 500 + oi * 31 + j)
                    _, dealt = _apply_pair_sim(engine, dup, foe_side, opair, sub)
                    tot += dealt
                avg = tot / k
            if avg > best:
                best = avg
        return best


# ==================================================================
# 輔助：可重現子 rng、pair 特徵
# ==================================================================

def _decision_seed(rng):
    """在一個決策開始時，從主 rng 取『一個』整數當本決策的基底種子。

    只呼叫一次 rng.getrandbits，因此對主 rng 的推進量固定（與候選 pair 數無關），
    整局可重現不受策略枚舉分支影響。各 pair 的子 rng 再由此基底混 pair 簽章衍生。
    """
    return rng.getrandbits(63)


def _sub_rng(decision_seed, pair, salt=0):
    """由本決策基底種子＋pair 內容＋salt 衍生可重現子 rng。

    純函式：同 (decision_seed, pair, salt) 恒得同序列，且不觸碰主 rng。
    """
    import random as _r
    mixed = (decision_seed * 1000003) ^ (hash((_pair_signature(pair), salt))
                                         & 0x7fffffffffffffff)
    return _r.Random(mixed & 0x7fffffffffffffff)


def _pair_signature(pair):
    sig = []
    for a in pair:
        sig.append((a.kind, a.dst, a.chip_id, a.face, a.target, a.subkind))
    return tuple(sig)


def _pair_move_count(pair):
    n = 0
    for a in pair:
        if a.kind == '移動':
            n += 1
        elif a.kind == '晶片' and a.face == '移動':
            n += 1
    return n


def _pair_uses_heal(engine, pair):
    for a in pair:
        if a.kind == '晶片' and a.face == '能力':
            ab = engine.chips[a.chip_id].ability_face
            if ab['type'] in ('heal', 'shield_reset'):
                return True
    return False


def _is_pass_pair(pair):
    return len(pair) == 2 and all(a.category() == 'pass' for a in pair)


def _topk_with_pass(scored_pairs, k):
    """輪2 候選池修正：靜態傷害前 K ∪ 強制納入 pass+pass（K 實際上限 K+1）。

    scored_pairs：[(score, pair), …]，已含全部合法 pair 的靜態分數。
    回傳：前 K 名 pair 清單；若 pass+pass 不在前 K 內且存在於候選集中，
    額外併入（故實際回傳筆數上限 K+1，若 pass+pass 本就落在前 K 內則仍為 K）。
    """
    ordered = sorted(scored_pairs, key=lambda x: x[0], reverse=True)
    top = ordered[:k]
    if any(_is_pass_pair(p) for _, p in top):
        return top
    for score, pair in ordered[k:]:
        if _is_pass_pair(pair):
            return top + [(score, pair)]
    # 候選集中根本沒有 pass+pass（例：first_comp 限一行動）→ 維持原 top-k
    return top


class TwoPly(Policy):
    """B2 全量：對自己整回合行動組合取靜態估值前 K ∪ 強制納入 pass+pass，
    對每個再枚舉對手回應的靜態估值前 K ∪ 強制納入 pass+pass，取 minimax 期望
    （雙層前瞻）。

    估值器沿用 GreedyDamage 同一把尺（本回合期望造成傷害，_expected_pair_damage），
    不新設計權重——差別只在「往下多看一層對手最佳回應」。

    輪2 候選池修正（主幹裁決 2026-07-06 00:06，取代輪1 先導版純 top-K）：
    先導版第一層剪枝只用「本方造成傷害」篩選候選，天生排除「傷害=0 但淨值
    可能更優」的 pass+pass；診斷見 round1 報告_B2先導.md 步驟3——深度提升出
    現非單調（twoply 輸給 oneply、甚至輸給 greedy）的根因正是候選集裡沒有
    pass 選項可選。修正：兩層候選池都改「靜態傷害前 K=3 ∪ 強制納入
    pass+pass」，K 實際上限因而是 4（pass+pass 若本來就在 top-3 內則仍是 3）。

    流程（K=config.extra['twoply_k']，預設 3）：
      1. 列出我方合法 pair，逐一用 greedy 估值器估「我造成傷害」，取前 K，
         再強制併入 pass+pass（若不在前 K 內）。
      2. 對每個候選 pair，實際施行到複本（sim_clone），得到「我方本回合實傷」
         與對手側後態。
      3. 在後態上列出對手合法 pair，逐一用同一 greedy 估值器（對手視角）估
         「對手造成傷害」，取前 K，同樣強制併入 pass+pass。
      4. 對這些對手回應候選，實際施行、取對手真實造成傷害的最大值（對手選
         對我最不利者＝我方淨值的下界，minimax）。
      5. 我方淨值 ＝ 我方本回合實傷 − 對手最佳回應實傷；取淨值最大的我方
         pair。平手時比照 GreedyDamage 用距離做 tie-break。

    成本：O(|我方pairs|·靜態估值) + O((K+1)·(|對手pairs|·靜態估值 +
    (K+1)·實際施行))，仍遠比 OnePly（對每個我方 pair 都做對手抽樣枚舉）收斂。
    """
    name = 'twoply'

    def choose_actions(self, st, side, rng, engine):
        first_comp = None
        if (st.config.first_turn_comp == '一行動'
                and st.round_no == 1 and side == st.first_mover):
            first_comp = '一行動'
        pairs = engine.legal_action_pairs(st, side, first_comp)
        k = max(1, int(st.config.extra.get('twoply_k', 3)))
        samples = max(1, st.config.expect_samples)
        ds = _decision_seed(rng)

        # ---- 第一層：對我方 pair 做靜態估值，取前 K ∪ 強制納入 pass+pass ----
        scored = []
        for pair in pairs:
            sub = _sub_rng(ds, pair, 1000)
            dmg = _expected_pair_damage(engine, st, side, pair, sub, samples)
            scored.append((dmg, pair))
        top_my = _topk_with_pass(scored, k)

        best_pair = None
        best_val = None
        for rank, (my_static_dmg, pair) in enumerate(top_my):
            sub = _sub_rng(ds, pair, 2000 + rank)
            dup, my_dealt = _apply_pair_sim(engine, st, side, pair, sub)
            foe_side = 1 - side
            foe_unit = dup.units[foe_side]
            if foe_unit is None or not foe_unit.alive:
                # 我方已致勝：淨值＝我方實傷（對手無回應）
                net = float(my_dealt)
            else:
                opp_best = self._opp_best_of_topk(engine, dup, foe_side, side,
                                                   ds, pair, k, samples)
                net = float(my_dealt) - opp_best
            dist = _enemy_min_distance_after(engine, st, side, pair,
                                             _sub_rng(ds, pair, 3000))
            key = (round(net, 3), dist)
            if best_val is None or key > best_val:
                best_val = key
                best_pair = pair
        return list(best_pair)

    def _opp_best_of_topk(self, engine, dup, foe_side, my_side, ds, my_pair,
                          k, samples):
        """在對手後態上，用同一 greedy 估值器選對手前 K 候選 ∪ 強制納入
        pass+pass，實際施行取對我造成傷害的最大值（對手 minimax 選擇）。"""
        opp_pairs = engine.legal_action_pairs(dup, foe_side, None)
        scored = []
        for opair in opp_pairs:
            sub = _sub_rng(ds, my_pair, 4000 + hash(_pair_signature(opair))
                           % 100000)
            dmg = _expected_pair_damage(engine, dup, foe_side, opair, sub,
                                        samples)
            scored.append((dmg, opair))
        top_opp = _topk_with_pass(scored, k)
        best = 0.0
        for rank, (opp_static_dmg, opair) in enumerate(top_opp):
            sub = _sub_rng(ds, my_pair, 5000 + rank)
            _, dealt = _apply_pair_sim(engine, dup, foe_side, opair, sub)
            if dealt > best:
                best = float(dealt)
        return best


# 策略登記表（名稱 -> 類）
SHARED_POLICIES = {
    'random_legal': RandomLegal,
    'greedy_damage': GreedyDamage,
    'turtle': Turtle,
    'positional': Positional,
    'oneply': OnePly,
    'twoply': TwoPly,
}


def make_policy(name):
    return SHARED_POLICIES[name]()
