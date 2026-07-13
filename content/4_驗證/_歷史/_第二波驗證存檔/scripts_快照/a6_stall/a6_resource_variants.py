# -*- coding: utf-8 -*-
"""A6 Part2：資源四變體——開關式 mixin，不新增四份引擎副本。

四變體全部只覆寫 Dir2OverlayEngine 的既有掛點（hook_start_turn／
hook_resource_pickup／use_resource_cost2／use_resource_cost3／
_do_attack 前置），不動 core.py／setups.py／dir2.py 本身；用
`st.config.extra['resource_variant']` 這支旗標選擇行為，預設
None＝維持 dir2.py 原行為（基準組）。

變體定義（規格 A6 Part2 一字不差）：
  V1 效果減半：費2/費3 兩個既有效果（下一擊次數+1、立即抽2張）數值減半。
    抽2張→抽1張（乾淨整除）；「次數+1」離散、減半改用「50%機率生效」
    表達同一件事（期望效果=0.5次命中，與抽牌減半同一種「一半」定義）。
    50%判定用該側決策衍生 rng（deterministic sub-rng，不動主 rng 序列，
    可重現）。
  V2 雙方自動獲取：關掉走位誘因（撿取判定形同虛設——場上不再生成資源球，
    hook_start_turn 直接跳過生成），改成每2回合（沿用共用資源週期）雙方
    各自動 +1 顆資源效果——「隔離『誘因』與『資源量』」：資源總量與基準組
    同節奏累積，但不再需要走位去撿、也沒有球可撿。
  V3 只加速不解鎖：資源不再購買「下一擊次數+1」或「抽2張」，改成單一效果
    「本回合行動點+1」（多打一個行動，行動類別限制不變、含攻擊或移動皆可）
    ——不解鎖任何原本沒有的能力/加傷，只讓本回合『多做一件事』。費用沿用
    3（原費3的抽牌位階），舊費2/費3介面停用（resources 消耗＝3，效果換掉）。
  V4 撿取有代價：拾取資源那一刻起，到「拾取者的下一次自己回合結束」為止，
    該側防禦值（護盾與力場，非閃避——閃避的機率/確定性削減在攻擊發起方
    結算路徑，與『被打』的防禦量無關，此代理只動「扛傷」的兩項）打七五折
    （-25%＝防禦有效值打75%，護盾上限與力場數值即時打75%、期間結束後
    全額恢復）——模擬「暴露位置」的風險代理，報告標明為代理量，非官方
    機制的忠實模擬。
"""
import random

from dir2 import Dir2OverlayEngine


def _variant(st):
    return st.config.extra.get('resource_variant')


def _decision_seed_local(st, side, salt):
    """本模組自有的、與策略 rng 隔離的確定性子種子（V1 的機率判定用）。"""
    base = (st.config.seed << 20) ^ (st.round_no << 8) ^ (side << 4) ^ salt
    return random.Random(base & 0x7fffffffffffffff)


class StepAdjustableSafetyNetMixin(object):
    """逐字複製 v11_calibrate.py 的同名 mixin（不 import 該檔——它拉了
    multiprocessing/search_v1/exploit_dir1 等大量依賴，A6 只需要這一個
    純函式覆寫，直接複製比 import 整個校準檔更乾淨、diff 更小）。

    覆寫 apply_safety_net：安全網模式讀 extra['安全網模式']（'遞增'／
    '固定'，預設'固定'向後相容 core.py 原行為）、基值讀 extra['安全網基值']
    （預設10）、遞增步幅讀 extra['安全網步幅']（預設5）——v1.1 全域檔
    （安全網起點15・模式遞增・基值10・步幅5）必須靠此 mixin 才會真的生效，
    否則 core.Engine.apply_safety_net 只有寫死的固定-10（無視 extra 旗標，
    這是本檔開發過程中發現並修正的一個真實 bug，見 tests_a6.py 對應回歸
    測試）。"""

    def apply_safety_net(self, st):
        base = st.config.extra.get('安全網基值')
        if base is None:
            base = 10
        step_size = st.config.extra.get('安全網步幅')
        if step_size is None:
            step_size = 5
        mode = st.config.extra.get('安全網模式', '固定')
        if st.round_no < st.config.safety_net_turn:
            return False
        if mode == '遞增':
            step = st.round_no - st.config.safety_net_turn
            damage = base + step_size * step
        else:
            damage = base
        triggered = False
        for side in (0, 1):
            u = st.units[side]
            if u is None or not u.alive:
                continue
            if st.damage_this_turn[side] > 0:
                continue
            u.hp -= damage
            triggered = True
            if u.hp <= 0:
                self._check_unit_down(st, side)
        if triggered:
            st.log.append({'event': '安全網', 'round': st.round_no,
                           'damage': damage})
        return triggered


class ResourceVariantEngine(StepAdjustableSafetyNetMixin, Dir2OverlayEngine):
    """四變體開關式引擎；resource_variant is None 時與 Dir2OverlayEngine
    （疊加安全網遞增 mixin）完全等價（回歸測試核對，見 tests_a6.py）。"""

    # ---------------- V2：雙方自動獲取（隔離誘因/資源量）----------------
    def hook_start_turn(self, st, side):
        variant = _variant(st)
        if variant == 'V2':
            # 場上不再生成資源球（誘因歸零）；改成固定節奏雙方各 +1。
            if st.config.extra.get('resource_enabled', True) is False:
                return
            rate = st.config.extra.get('資源週期', 2)
            if side == st.first_mover and st.round_no % rate == 0:
                for s in (0, 1):
                    if st.resources[s] < 5:
                        st.resources[s] += 1
                st.log.append({'event': 'V2自動獲取', 'round': st.round_no})
            return
        super(ResourceVariantEngine, self).hook_start_turn(st, side)

    # ---------------- V4：拾取後防禦力衰減視窗 ----------------
    def hook_resource_pickup(self, st, side, unit):
        variant = _variant(st)
        if variant != 'V4':
            super(ResourceVariantEngine, self).hook_resource_pickup(
                st, side, unit)
            return
        picked = (unit.pos in st.resource_cells)
        super(ResourceVariantEngine, self).hook_resource_pickup(st, side, unit)
        if picked:
            # 記錄：該側從現在起到「其下一次回合結束」防禦力打75%。
            # 用 extra 存到期回合（該側下一次自己回合結束的 round_no）。
            key = '_v4_penalty_until_%d' % side
            # 下一次自己回合結束＝目前 round（若對手還沒走完本回合、本回合
            # 結束時已含自己），保守取「本回合」與「下一回合」皆生效一輪
            # （即時生效到下一次自己回合結束，至少涵蓋本回合剩餘與下一輪）：
            st.config.extra[key] = st.round_no + 1
            st.log.append({'event': 'V4暴露懲罰啟動', 'side': side,
                           '到回合': st.round_no + 1, 'round': st.round_no})

    def _v4_active(self, st, side):
        if _variant(st) != 'V4':
            return False
        until = st.config.extra.get('_v4_penalty_until_%d' % side)
        return until is not None and st.round_no <= until

    def _do_attack(self, st, side, spec, target, dmg, hits, rng):
        """V4：若『被攻擊方』正處於暴露懲罰視窗，臨時把護盾/力場打75%
        （結算後還原），不改變 resolve_attack 本身、只在呼叫前後暫調
        defender 欄位——確定性、可逆、不影響其他變體/基準組路徑。"""
        enemy_side = 1 - side
        if not self._v4_active(st, enemy_side):
            return super(ResourceVariantEngine, self)._do_attack(
                st, side, spec, target, dmg, hits, rng)
        from core import cells_hit
        idxs = cells_hit(st.units[side].pos, side, spec, target,
                        st.enemy_positions(side))
        saved = {}
        for enemy_idx in idxs:
            u = st.units[enemy_idx]
            if u is None:
                continue
            saved[enemy_idx] = (u.field, u.shield_max, u.shield_cur)
            u.field = u.field * 0.75
            u.shield_max = u.shield_max * 0.75
            u.shield_cur = min(u.shield_cur, u.shield_max)
        try:
            return super(ResourceVariantEngine, self)._do_attack(
                st, side, spec, target, dmg, hits, rng)
        finally:
            for enemy_idx, (f, smax, scur) in saved.items():
                u = st.units[enemy_idx]
                if u is None:
                    continue
                # 護盾當前值：若戰鬥中已變化（被打穿/回滿），還原「相對變化量」
                # 而非直接覆寫絕對值——用差量法：先算戰鬥中 shield_cur 相對
                # 懲罰版 shield_max 的比例，還原到原始 shield_max 的等比例。
                if smax > 0:
                    ratio = (u.shield_cur / u.shield_max) if u.shield_max > 0 \
                        else 0.0
                else:
                    ratio = 1.0 if u.shield_cur > 0 else 0.0
                u.field = f
                u.shield_max = smax
                u.shield_cur = ratio * smax if smax > 0 else 0

    # ---------------- V1：效果減半 / V3：只加速不解鎖 ----------------
    def use_resource_cost2(self, st, side):
        variant = _variant(st)
        if variant == 'V3':
            return False   # V3 只留費3→加速一條路徑，費2 介面停用
        if variant == 'V1':
            if st.resources[side] < 2:
                return False
            st.resources[side] -= 2
            roll = _decision_seed_local(st, side, 101).random()
            applied = roll < 0.5   # 效果減半＝50%機率生效（期望值=半次命中）
            if applied:
                st.config.extra['_hits_bonus_pending_%d' % side] = True
            st.log.append({'event': '費2資源', 'side': side, 'V1生效': applied,
                           'round': st.round_no})
            return True
        return super(ResourceVariantEngine, self).use_resource_cost2(st, side)

    def use_resource_cost3(self, st, side, rng):
        variant = _variant(st)
        if variant == 'V3':
            # V3：費3 的效果整個換掉——不再抽牌，改「本回合行動點+1」，
            # 不解鎖任何新能力/加傷。ResourceAware.decide_resource_use 在
            # resources>=3 時呼叫的正是這個介面，天然對應「費3→加速」。
            if st.resources[side] < 3:
                return False
            st.resources[side] -= 3
            st.config.extra['_extra_action_pending_%d' % side] = True
            st.log.append({'event': 'V3加速資源', 'side': side,
                           'round': st.round_no})
            return True
        if variant == 'V1':
            if st.resources[side] < 3:
                return False
            st.resources[side] -= 3
            self.draw(st, side, 1, rng)   # 抽2張→抽1張（效果減半）
            st.log.append({'event': '費3資源', 'side': side,
                           'round': st.round_no})
            return True
        return super(ResourceVariantEngine, self).use_resource_cost3(st, side,
                                                                     rng)

    # ---------------- V3：本回合多給一個行動槽 ----------------
    def take_turn(self, st, side, policy, rng):
        variant = _variant(st)
        if variant != 'V3':
            return super(ResourceVariantEngine, self).take_turn(
                st, side, policy, rng)
        # V3：在標準流程之後，若本回合有「加速」生效旗標，額外再給一個
        # 行動機會（用同一個 policy 對『已用掉兩類』之外的剩餘類別選一次）。
        st.side_to_move = side
        st.actions_this_turn = []
        self.hook_start_turn(st, side)
        self.draw(st, side, st.config.draw_per_turn, rng)

        decide = getattr(policy, 'decide_resource_use', None)
        if decide is not None:
            decide(st, side, rng, self, timing='before')

        first_comp_limit = None
        if (st.config.first_turn_comp == '一行動'
                and st.round_no == 1 and side == st.first_mover):
            first_comp_limit = '一行動'

        actions = policy.choose_actions(st, side, rng, self)
        actions = self._sanitize_actions(st, side, actions, first_comp_limit)

        used = set()
        dealt_total = 0
        for act in actions:
            if act.category() != 'pass':
                used.add(act.category())
            dealt_total += self.apply_action(st, side, act, rng)
            st.actions_this_turn.append(act)
            if st.units[1 - side] is None or not st.units[1 - side].alive:
                break

        if decide is not None:
            decide(st, side, rng, self, timing='after')

        # ---- V3 加速：若本回合已消耗費3宣告加速，追加一個行動 ----
        accel_key = '_extra_action_pending_%d' % side
        if (st.config.extra.get(accel_key) and
                (st.units[1 - side] is not None and
                 st.units[1 - side].alive)):
            st.config.extra[accel_key] = False
            chosen = self._choose_single_extra(st, side, policy, rng, used)
            if chosen is not None:
                dealt_total += self.apply_action(st, side, chosen, rng)
                st.actions_this_turn.append(chosen)
                st.log.append({'event': 'V3加速行動', 'side': side,
                               'round': st.round_no})

        st.damage_this_turn[side] = dealt_total
        self.hook_end_turn(st, side)
        return dealt_total

    def _choose_single_extra(self, st, side, policy, rng, used):
        """V3 加速：用 legal_action_pairs(first_comp_limit='一行動') 讓
        policy 現有的 choose_actions 介面（本來就會處理『一行動』限制的
        first_comp_limit 分支）重新選一次，取其第一個非 pass 行動、且
        類別不在 used 內者。與策略介面完全相容，不需新增策略方法。"""
        # 暫時單獨呼叫 choose_actions，用 first_comp_limit 強制單行動：
        # 大部分策略類（policies.py 五策略＋dir2.ResourceAware/Blind）都是
        # 靠 engine.legal_action_pairs(st, side, first_comp) 這個參數決定
        # 要不要限縮成單行動，本函式直接複製該分支的效果。
        pairs = self.legal_action_pairs(st, side, '一行動')
        # 排除已用過類別（可能因加速獨立於原本兩行動而已用掉的類別）
        pairs = [p for p in pairs
                if p[0].category() == 'pass' or p[0].category() not in used]
        if not pairs:
            return None
        # 複用 policy 對這組 pairs 的偏好：多數策略內部重新呼叫
        # legal_action_pairs，這裡改成直接傳一份「假 engine view」不現實；
        # 退而求其次，用 greedy 期望淨傷排序（與 classify.py 同一把尺）
        # 選最佳單行動——這是 V3 專屬的加速行動選擇邏輯，非重新定義策略。
        from a6_classify import _pair_has_attack
        from policies import _expected_pair_damage, _decision_seed, _sub_rng
        ds = _decision_seed(rng)
        best = None
        best_val = -1.0
        for pair in pairs:
            if _pair_has_attack(self, pair):
                sub = _sub_rng(ds, pair)
                val = _expected_pair_damage(self, st, side, pair, sub,
                                            max(1, st.config.expect_samples))
            else:
                val = 0.0
            if val > best_val:
                best_val = val
                best = pair[0]
        if best is None or best.category() == 'pass':
            # 沒有攻擊可加碼：加速行動當前情境沒有額外攻擊價值，選第一個
            # 非 pass 的合法單行動（如移動/佈局），沒有則作罷。
            for pair in pairs:
                if pair[0].category() != 'pass':
                    return pair[0]
            return None
        return best
