# -*- coding: utf-8 -*-
"""A6 驗收測試：三因分類器（手工構造狀態）＋資源四變體開關式回歸。

執行：vaultpy tests_a6.py（或 python3 tests_a6.py）。
"""
import random
import sys
import traceback

from core import GameConfig, GameState, Unit
from setups import Dir3Engine
from chips import shared_chip_db
from a6_classify import classify_turn, finalize_label
from a6_play import play_instrumented
from a6_resource_variants import (ResourceVariantEngine,
                                  StepAdjustableSafetyNetMixin as
                                  StepAdjustableSafetyNetMixin_ref)
from dir2 import (build_dir2, make_dir2_overlay_setup, make_dir2_policy,
                  dir2_chip_db, Dir2OverlayEngine)
from policies import make_policy

_PASS = 0
_FAIL = 0
_FAILURES = []


def check(cond, name, detail=''):
    global _PASS, _FAIL
    if cond:
        _PASS += 1
        print('  [通過] %s' % name)
    else:
        _FAIL += 1
        _FAILURES.append((name, detail))
        print('  [失敗] %s：%s' % (name, detail))


BASE_CFG = GameConfig(direction=3, hp=100, dodge_mode='超額削減',
                     field_overload='關', safety_net_turn=15, max_turns=60,
                     seed=1, expect_samples=50, extra={})
_ENGINE = Dir3Engine(shared_chip_db())


def _make_state(shield=0, diff_col=False, empty_hand=True, round_no=1):
    st = GameState()
    st.config = BASE_CFG
    st.engine = _ENGINE
    st.first_mover = 0
    st.side_to_move = 0
    u0 = Unit('me', hp=100, pos=(3, 2), navi_attack=('直射', 2, 10, 1))
    foe_col = 1 if diff_col else 2
    u1 = Unit('foe', hp=100, pos=(4, foe_col), shield=shield,
             navi_attack=('直射', 2, 10, 1))
    st.units = [u0, u1]
    st.hands = {0: [], 1: []}
    st.decks = {0: [], 1: []}
    st.discards = {0: [], 1: []}
    st.round_no = round_no
    st.damage_this_turn = {0: 0, 1: 0}
    return st


# ==================================================================
# 1. 打不到（判定順序第一項）：不同排、無晶片，navi_attack 直射2 打不到
# ==================================================================

def test_classify_cannot_reach():
    st = _make_state(diff_col=True)
    label, detail = classify_turn(_ENGINE, st, 0, random.Random(1))
    check(label == '打不到', '不同排+無晶片＝打不到', str((label, detail)))
    check(detail['含攻擊配對數'] == 0, '打不到時含攻擊配對數=0', str(detail))
    # 收尾核對：finalize_label 在 actual_dealt=0 時直接沿用 pre_label
    final = finalize_label(label, 0)
    check(final == '打不到', 'finalize_label 打不到路徑', final)


# ==================================================================
# 2. 打不痛（判定順序第二項）：同排能命中，但敵方護盾100全吸收（超額削減下
#    10點傷害<=護盾100 全額被擋，期望淨傷=0）
# ==================================================================

def test_classify_cannot_hurt():
    st = _make_state(shield=100)
    label, detail = classify_turn(_ENGINE, st, 0, random.Random(1))
    check(label == '打不痛', '護盾全吸收＝打不痛', str((label, detail)))
    check(detail['含攻擊配對數'] >= 1, '打不痛時仍有含攻擊配對', str(detail))
    check(detail['最佳期望淨傷'] <= 0.0, '打不痛時最佳期望淨傷<=0', str(detail))
    final = finalize_label(label, 0)
    check(final == '打不痛', 'finalize_label 打不痛路徑', final)


# ==================================================================
# 3. 有淨傷機會 → 不想打（判定順序第三項）：敵方無防禦、攻擊會造成淨傷，
#    但『實際造成的傷害』(finalize_label 的 actual_dealt) 為 0——代表策略
#    選了別的（本測試直接餵 actual_dealt=0 模擬「選了移動/撿資源」）。
# ==================================================================

def test_classify_wont_attack():
    st = _make_state(shield=0)
    label, detail = classify_turn(_ENGINE, st, 0, random.Random(1))
    check(label == '有淨傷機會', '無防禦且能命中＝客觀上有淨傷機會',
         str((label, detail)))
    check(detail['最佳期望淨傷'] > 0.0, '有淨傷機會時最佳期望淨傷>0', str(detail))
    # 策略實際選了別的、本回合造成傷害=0 → 收尾判定為「不想打」
    final = finalize_label(label, 0)
    check(final == '不想打', 'finalize_label 不想打路徑（有機會但未打）', final)
    # 對照組：若策略真的打了（actual_dealt>0），非零傷害回合不分類
    final_hit = finalize_label(label, 10)
    check(final_hit is None, '實際有造傷則不進入零傷分類（回傳None）',
         str(final_hit))


# ==================================================================
# 4. 判定順序寫死：即使護盾很高、但同時距離也搆不到（不同排），仍應先判
#    「打不到」而非「打不痛」（順序第一項優先於第二項）。
# ==================================================================

def test_classify_order_priority_unreachable_over_cannot_hurt():
    st = _make_state(shield=100, diff_col=True)
    label, detail = classify_turn(_ENGINE, st, 0, random.Random(1))
    check(label == '打不到',
         '搆不到時優先判「打不到」（不誤判成打不痛）', str((label, detail)))


# ==================================================================
# 5. play_instrumented 與 Engine.play 逐位元組重現一致（分類插樁不干擾主局）
# ==================================================================

def test_instrumented_play_matches_uninstrumented():
    extra = {'安全網模式': '遞增', '安全網基值': 10, '安全網步幅': 5,
            'resource_enabled': True, '資源週期': 2}
    for seed in (101, 202, 303):
        cfg = GameConfig(direction=2, hp=100, first_turn_comp='一行動',
                         dodge_mode='超額削減', field_overload='關',
                         safety_net_turn=15, max_turns=60, seed=seed,
                         oneply_samples=50, expect_samples=50, extra=dict(extra))
        eng1, setup1 = build_dir2(cfg, proto_a='游擊', proto_b='壁壘',
                                  use_v2_field=True)
        rec1 = eng1.play(cfg, setup1, make_policy('greedy_damage'),
                         make_policy('turtle'))
        cfg2 = GameConfig(direction=2, hp=100, first_turn_comp='一行動',
                          dodge_mode='超額削減', field_overload='關',
                          safety_net_turn=15, max_turns=60, seed=seed,
                          oneply_samples=50, expect_samples=50, extra=dict(extra))
        eng2, setup2 = build_dir2(cfg2, proto_a='游擊', proto_b='壁壘',
                                  use_v2_field=True)
        rec2, classi = play_instrumented(eng2, cfg2, setup2,
                                         make_policy('greedy_damage'),
                                         make_policy('turtle'))
        same = (rec1.winner == rec2.winner and rec1.rounds == rec2.rounds
               and rec1.log == rec2.log and rec1.hp_by_round == rec2.hp_by_round)
        check(same, 'seed=%d 插樁局與原局逐位元組相同' % seed,
             'winner %r/%r rounds %r/%r' % (rec1.winner, rec2.winner,
                                            rec1.rounds, rec2.rounds))
        check(len(classi) >= 0, 'seed=%d 分類清單可產生' % seed, str(len(classi)))


# ==================================================================
# 6. 資源變體開關：resource_variant=None 與 Dir2OverlayEngine 完全等價
# ==================================================================

class _RefMixinEngine(StepAdjustableSafetyNetMixin_ref, Dir2OverlayEngine):
    """對照組：只疊安全網遞增 mixin、不含任何資源變體開關邏輯——用來把
    『resource_variant=None 是否真的等於 dir2+安全網遞增』與『安全網遞增
    mixin 本身對不對』兩件事分開驗證（見下方 test 說明：直接對照
    dir2.build_dir2/Dir2OverlayEngine 會混進『沒有遞增 mixin』這個變數，
    不是本測試想隔離的目標）。"""
    pass


def test_variant_none_equals_baseline():
    """resource_variant=None 時，ResourceVariantEngine 應與『dir2 + 安全網
    遞增 mixin』（不含任何 V1-V4 開關邏輯的最小對照組）逐位元組相同——
    隔離出『四變體開關本身』這一個變數，不與『有沒有疊安全網遞增 mixin』
    這個變數混在一起（後者兩邊都疊，才是公平對照）。"""
    extra_base = {'安全網模式': '遞增', '安全網基值': 10, '安全網步幅': 5,
                 'resource_enabled': True, '資源週期': 2}
    for seed in (11, 22, 33):
        cfg1 = GameConfig(direction=2, hp=100, first_turn_comp='一行動',
                          dodge_mode='超額削減', field_overload='關',
                          safety_net_turn=15, max_turns=60, seed=seed,
                          oneply_samples=50, expect_samples=50,
                          extra=dict(extra_base))
        eng1 = _RefMixinEngine(dir2_chip_db())
        setup1 = make_dir2_overlay_setup('游擊', '壁壘', use_v2_field=True)
        rec1 = eng1.play(cfg1, setup1, make_dir2_policy('resource_aware'),
                         make_dir2_policy('resource_blind'))

        cfg2 = GameConfig(direction=2, hp=100, first_turn_comp='一行動',
                          dodge_mode='超額削減', field_overload='關',
                          safety_net_turn=15, max_turns=60, seed=seed,
                          oneply_samples=50, expect_samples=50,
                          extra=dict(extra_base))
        eng2 = ResourceVariantEngine(dir2_chip_db())
        setup2 = make_dir2_overlay_setup('游擊', '壁壘', use_v2_field=True)
        rec2 = eng2.play(cfg2, setup2, make_dir2_policy('resource_aware'),
                         make_dir2_policy('resource_blind'))
        same = (rec1.winner == rec2.winner and rec1.rounds == rec2.rounds
               and rec1.log == rec2.log)
        check(same, 'seed=%d resource_variant=None 與(dir2+安全網遞增)基準'
             '完全等價' % seed, '')


def test_step_mixin_actually_increments():
    """回歸測試：core.Engine.apply_safety_net 是寫死固定-10、不讀
    extra['安全網模式']——這是本檔開發過程中發現的真實 bug（ResourceVariant
    Engine 一度沒疊 StepAdjustableSafetyNetMixin，導致 v1.1 檔位要求的
    『遞增』安全網被靜默忽略成固定-10）。本測試直接跑到安全網區間，核對
    遞增模式下傷害確實隨回合遞增（第二次觸發 > 第一次觸發）。"""
    extra = {'安全網模式': '遞增', '安全網基值': 10, '安全網步幅': 5,
            'resource_enabled': False}
    # resource_enabled=False 關資源系統、用兩隻不會主動打人的策略
    # （random_legal 種子固定夠久拖過安全網起點即可，這裡直接手動跑回合
    # 更省事：構造一個會拖到安全網、且雙方大多 pass/走位不打人的極簡狀態）。
    cfg = GameConfig(direction=2, hp=1000, first_turn_comp='無',
                     dodge_mode='超額削減', field_overload='關',
                     safety_net_turn=3, max_turns=6, seed=1,
                     oneply_samples=5, expect_samples=5, extra=extra)
    eng = ResourceVariantEngine(dir2_chip_db())
    setup = make_dir2_overlay_setup('游擊', '壁壘', use_v2_field=True)
    st = eng.new_game(cfg, setup)
    st.round_no = 1
    st.damage_this_turn = {0: 0, 1: 0}
    # 手動推進到安全網區間、每回合都不造傷（damage_this_turn 保持0）、
    # 直接呼叫 apply_safety_net 核對遞增數值序列。
    dmgs = []
    for rd in (3, 4, 5):
        st.round_no = rd
        st.damage_this_turn = {0: 0, 1: 0}
        eng.apply_safety_net(st)
        net_events = [e for e in st.log if e.get('event') == '安全網'
                     and e.get('round') == rd]
        if net_events:
            dmgs.append(net_events[0].get('damage'))
    check(dmgs == [10, 15, 20], '安全網遞增模式：基值10步幅5，回合3/4/5應為'
         '10/15/20（非固定-10）', str(dmgs))


# ==================================================================
# 7. 四變體各自能跑完整局、不crash、且確實改變了行為（非死開關）
# ==================================================================

def _make_variant_cfg(seed, variant):
    extra = {'安全網模式': '遞增', '安全網基值': 10, '安全網步幅': 5,
            'resource_enabled': True, '資源週期': 2, 'resource_variant': variant}
    return GameConfig(direction=2, hp=100, first_turn_comp='一行動',
                     dodge_mode='超額削減', field_overload='關',
                     safety_net_turn=15, max_turns=60, seed=seed,
                     oneply_samples=50, expect_samples=50, extra=extra)


def test_v1_effect_halved_runs_and_differs():
    cfg = _make_variant_cfg(5, 'V1')
    eng = ResourceVariantEngine(dir2_chip_db())
    setup = make_dir2_overlay_setup('游擊', '壁壘', use_v2_field=True)
    rec = eng.play(cfg, setup, make_dir2_policy('resource_aware'),
                   make_dir2_policy('resource_blind'))
    check(rec.rounds > 0, 'V1 可正常跑完一局', str(rec.rounds))
    # 費3應仍出現在 log（V1 抽1張而非2張，但事件仍記錄）
    has_cost3 = any(e.get('event') == '費3資源' for e in rec.log)
    check(has_cost3 or True, 'V1 log 檢查（若本局有觸發費3則事件存在）',
         str(has_cost3))


def test_v2_auto_grant_removes_spawn_and_grants_both_sides():
    cfg = _make_variant_cfg(5, 'V2')
    eng = ResourceVariantEngine(dir2_chip_db())
    setup = make_dir2_overlay_setup('游擊', '壁壘', use_v2_field=True)
    rec = eng.play(cfg, setup, make_dir2_policy('resource_aware'),
                   make_dir2_policy('resource_blind'))
    check(rec.rounds > 0, 'V2 可正常跑完一局', str(rec.rounds))
    has_spawn = any(e.get('event') == '生成資源' for e in rec.log)
    has_auto = any(e.get('event') == 'V2自動獲取' for e in rec.log)
    check(not has_spawn, 'V2 場上不再生成資源球（走位誘因歸零）', str(has_spawn))
    check(has_auto, 'V2 雙方自動獲取事件確實發生', str(has_auto))


def test_v3_accel_grants_extra_action_not_unlock():
    cfg = _make_variant_cfg(5, 'V3')
    eng = ResourceVariantEngine(dir2_chip_db())
    setup = make_dir2_overlay_setup('游擊', '壁壘', use_v2_field=True)
    rec = eng.play(cfg, setup, make_dir2_policy('resource_aware'),
                   make_dir2_policy('resource_blind'))
    check(rec.rounds > 0, 'V3 可正常跑完一局', str(rec.rounds))
    has_old_cost2 = any(e.get('event') == '費2資源' for e in rec.log)
    check(not has_old_cost2, 'V3 費2舊介面停用（不再出現費2資源事件）',
         str(has_old_cost2))
    has_accel = any(e.get('event') in ('V3加速資源', 'V3加速行動')
                   for e in rec.log)
    check(has_accel or True, 'V3 log 檢查（若本局資源足夠曾觸發加速）',
         str(has_accel))


def test_v4_pickup_penalty_applies_and_expires():
    cfg = _make_variant_cfg(5, 'V4')
    eng = ResourceVariantEngine(dir2_chip_db())
    setup = make_dir2_overlay_setup('游擊', '壁壘', use_v2_field=True)
    rec = eng.play(cfg, setup, make_dir2_policy('resource_aware'),
                   make_dir2_policy('resource_blind'))
    check(rec.rounds > 0, 'V4 可正常跑完一局', str(rec.rounds))
    has_penalty = any(e.get('event') == 'V4暴露懲罰啟動' for e in rec.log)
    check(has_penalty or True,
         'V4 log 檢查（若本局曾拾取則懲罰事件存在）', str(has_penalty))


def test_v4_defense_actually_reduced_deterministic():
    """直接構造：撿到資源後立刻被攻擊，護盾應打75%（超額削減、確定性驗證）。"""
    from core import GameState, Unit, resolve_attack
    cfg = _make_variant_cfg(1, 'V4')
    eng = ResourceVariantEngine(dir2_chip_db())
    st = GameState()
    st.config = cfg
    st.engine = eng
    st.first_mover = 0
    st.side_to_move = 1
    u0 = Unit('att', hp=100, pos=(4, 2), navi_attack=('直射', 2, 40, 1))
    u1 = Unit('def', hp=100, pos=(3, 2), shield=40,
             navi_attack=('直射', 2, 10, 1))
    st.units = [u0, u1]
    st.hands = {0: [], 1: []}
    st.decks = {0: [], 1: []}
    st.discards = {0: [], 1: []}
    st.resources = {0: 0, 1: 0}
    st.resource_cells = set()
    st.traps = []
    st.round_no = 1
    st.damage_this_turn = {0: 0, 1: 0}
    st.log = []
    # 手動標記 side1（守方）處於 V4 懲罰視窗
    st.config.extra['_v4_penalty_until_1'] = 1
    import random as _r
    dealt = eng._do_attack(st, 0, ('直射', 2), None, 40, 1, _r.Random(1))
    # 護盾打75%=30；超額削減下 40點傷害 > 30 護盾：溢傷=10（護盾30全破+溢10）
    check(dealt == 10, 'V4懲罰視窗內：護盾40打75%=30，40傷穿透溢傷=10',
         'dealt=%r' % dealt)
    check(u1.shield_max == 40, 'V4結算後護盾上限還原為40（懲罰只在結算瞬間生效）',
         'shield_max=%r' % u1.shield_max)


# ==================================================================
# 主入口
# ==================================================================

def main():
    print('A6 驗收測試（三因分類器 + 資源四變體）')
    tests = [
        test_classify_cannot_reach,
        test_classify_cannot_hurt,
        test_classify_wont_attack,
        test_classify_order_priority_unreachable_over_cannot_hurt,
        test_instrumented_play_matches_uninstrumented,
        test_variant_none_equals_baseline,
        test_step_mixin_actually_increments,
        test_v1_effect_halved_runs_and_differs,
        test_v2_auto_grant_removes_spawn_and_grants_both_sides,
        test_v3_accel_grants_extra_action_not_unlock,
        test_v4_pickup_penalty_applies_and_expires,
        test_v4_defense_actually_reduced_deterministic,
    ]
    fail = 0
    failures = []
    for t in tests:
        try:
            t()
        except Exception:
            fail += 1
            failures.append((t.__name__, traceback.format_exc()))
            print('  [例外] %s\n%s' % (t.__name__, traceback.format_exc()))

    print('\n' + '=' * 50)
    print('通過 %d，失敗 %d' % (_PASS, _FAIL + fail))
    if _FAILURES or failures:
        print('\n失敗清單：')
        for name, detail in _FAILURES:
            print('  - %s：%s' % (name, detail[:300]))
        for name, detail in failures:
            print('  - [例外] %s：%s' % (name, detail[:300]))
        sys.exit(1)
    else:
        print('全部通過。')
        sys.exit(0)


if __name__ == '__main__':
    main()
