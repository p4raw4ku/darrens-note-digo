# -*- coding: utf-8 -*-
"""B1 混合方向「走位換角棋」overlay 專屬驗收測試（附加於共用 tests.py／
metrics_v2_tests.py，不修改共用測試）。

執行：python3 b1_tests.py

涵蓋 round2/裁量_B1.md 十五條讀法定案中，落在引擎職責範圍內的項目：
  1. 換角合法性（BR-5）：兩名皆活＝可主動換角；一名倒下＝主動換角非法。
  2. 語義鎖三（BR-5 沿用）：主動換角當回合不得再用領航員類其他行動
     （含新／舊上場者的自攻）。
  3. 強制換入（BR-5/BL-4/BT-2）：不佔行動、出現在我方中央格、不觸發
     陷阱、不拾取資源。
  4. 深拷貝保留（BL-5，主格 A 讀法）：盾量、穿透旗標（BL-3）、過載
     絕對到期回合（BL-1）各自跨換角保留，離場期間過載計時照走不凍結。
  5. B 變體全重置（BL-6）：盾回滿、力場過載解除、穿透旗標清除，一整包。
  6. 安全網只扣上場者＋方級豁免（BL-2）。
  7. 費2 旗標跨換角（BR-4）：甲掛旗標→換乙→乙的下一次晶片能力面攻擊
     次數+1 仍生效。
  8. 首回合換角合法（BR-1）：先手首回合僅 1 行動下，可拿去換角。

全部手工構造已知值（直接操作 GameState/Unit 欄位＋逐步呼叫 engine
方法），不依賴大樣本統計。
"""
import os
import random
import sys
import traceback

sys.path.insert(0, os.path.dirname(__file__))

from core import GameConfig, Action, Unit, START_POS
from chips import shared_chip_db, Chip
import b1

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
        print('  [失敗] %s  %s' % (name, detail))


def eq(a, b, name):
    check(a == b, name, '期望 %r 得到 %r' % (b, a))


def _fresh_state(variant='A', seed=1, hp=50, safety_net_start=15,
                 safety_net_base=5, safety_net_step=4,
                 proto_a=('游擊', '壁壘'), proto_b=('游擊', '壁壘')):
    cfg = b1.base_b1_config(hp=hp)
    cfg.seed = seed
    eng, setup = b1.build_b1(cfg, variant=variant, proto_a=proto_a,
                            proto_b=proto_b,
                            safety_net_start=safety_net_start,
                            safety_net_base=safety_net_base,
                            safety_net_step=safety_net_step)
    st = eng.new_game(cfg, setup)
    return eng, st


# ==================================================================
# 1. 換角合法性（BR-5）：兩活可換／一死不可換
# ==================================================================

def test_1_switch_legality_two_alive():
    print('\n=== 1a. 換角合法性：兩名皆活＝主動換角合法 ===')
    eng, st = _fresh_state()
    acts = eng.legal_actions(st, 0)
    change_acts = [a for a in acts if a.kind == '領航員' and a.subkind == '換角']
    check(len(change_acts) == 1, '兩活時恰有 1 個換角 Action（唯一後備）',
         '得到 %d 個' % len(change_acts))
    eq(change_acts[0].target, 0, '換角 Action 目標索引指向後備 0')


def test_1_switch_legality_one_dead():
    print('\n=== 1b. 換角合法性：後備已死＝主動換角非法 ===')
    eng, st = _fresh_state()
    st.benches[0][0].alive = False
    st.benches[0][0].hp = 0
    acts = eng.legal_actions(st, 0)
    change_acts = [a for a in acts if a.kind == '領航員' and a.subkind == '換角']
    eq(len(change_acts), 0, '唯一後備已死時，無換角 Action 產生')


# ==================================================================
# 2. 語義鎖三：換角當回合禁自攻（沿用 dir1 A1 讀法）
# ==================================================================

def test_2_semantic_lock3_no_self_attack_after_switch():
    print('\n=== 2. 語義鎖三：主動換角(a1)後不得再用領航員類(a2) ===')
    eng, st = _fresh_state()
    pairs = eng.legal_action_pairs(st, 0)
    change_then_navi = [p for p in pairs
                        if p[0].kind == '領航員' and p[0].subkind == '換角'
                        and p[1].kind == '領航員']
    eq(len(change_then_navi), 0,
       '換角接領航員類（含自攻）的合法組合數必須為 0')
    change_then_other = [p for p in pairs
                         if p[0].kind == '領航員' and p[0].subkind == '換角'
                         and p[1].kind in ('移動', '晶片', 'pass')]
    check(len(change_then_other) > 0,
         '換角接移動/晶片/pass 仍合法（換角只吃領航員類名額，不禁其他類）')


# ==================================================================
# 3. 強制換入：不佔行動、出現在我方中央格、不觸發陷阱、不拾取資源
# ==================================================================

def test_3_forced_switch_no_action_cost():
    print('\n=== 3a. 強制換入不佔行動 ===')
    eng, st = _fresh_state()
    # 直接把上場者打到 0（繞開晶片/自攻，聚焦在強制換入本身的行動經濟）
    st.units[0].hp = 1
    rng = random.Random(0)
    # 用 0 傷害力場穿透判定無關，直接扣血後手動呼叫 _check_unit_down
    st.units[0].hp = 0
    before_actions = list(st.actions_this_turn)
    eng._check_unit_down(st, 0)
    check(st.units[0].name == '壁壘', '強制換入後上場者變成後備（壁壘）',
         '得到 %r' % st.units[0].name)
    eq(list(st.actions_this_turn), before_actions,
       '強制換入不透過 actions_this_turn 記錄任何行動（不佔行動槽）')


def test_3_forced_switch_center_cell():
    print('\n=== 3b. 強制換入出現在我方中央格 ===')
    eng, st = _fresh_state()
    st.units[0].pos = (1, 3)   # 移到非中央格，確認換入後被重置到中央格
    st.units[0].hp = 0
    eng._check_unit_down(st, 0)
    eq(st.units[0].pos, (2, 2), 'side0 強制換入者出現在我方中央格 (2,2)')

    eng2, st2 = _fresh_state()
    st2.units[1].pos = (6, 1)
    st2.units[1].hp = 0
    eng2._check_unit_down(st2, 1)
    eq(st2.units[1].pos, (5, 2), 'side1 強制換入者出現在我方中央格 (5,2)')


def test_3_forced_switch_no_trap_no_pickup():
    print('\n=== 3c. 強制換入不觸發陷阱、不拾取資源 ===')
    eng, st = _fresh_state()
    # 在 side0 中央格布一顆「敵方陷阱」與一顆資源球，驗證強制換入出現在
    # 該格時兩者都不觸發（BL-4：換角出現格永不觸發陷阱／不拾取資源）。
    st.traps.append({'owner': 1, 'pos': (2, 2), 'dmg': 999, 'hits': 1,
                     'revealed': False})
    st.resource_cells.add((2, 2))
    st.units[0].pos = (1, 3)
    st.units[0].hp = 0
    hp_before = st.benches[0][0].hp
    eng._check_unit_down(st, 0)
    eq(st.units[0].hp, hp_before,
       '強制換入者出現在佈有陷阱的中央格，HP 不受影響（陷阱不觸發）')
    check(not st.traps[0]['revealed'],
         '陷阱未因換角出現而現形（換角出現格不呼叫 hook_trap_check）')
    eq(st.resources[0], 0,
       '資源球未被強制換入者拾取（換角出現不算移動/位移結束）')
    check((2, 2) in st.resource_cells,
         '資源球仍留在原地（未被拾取消耗）')


# ==================================================================
# 4. 深拷貝保留（主格 A 讀法）：盾量／穿透旗標／過載絕對計時
# ==================================================================

def test_4_preserve_shield_value():
    print('\n=== 4a. 深拷貝保留：盾量跨換角保留（不回滿）===')
    eng, st = _fresh_state(variant='A')
    bench = st.benches[0][0]
    bench.shield_cur = 3   # 手工設定離場時的殘盾（滿盾 25）
    eq(bench.shield_max, 25, '前提：壁壘型滿盾為 25')
    act = Action('領航員', subkind='換角', target=0)
    eng.apply_action(st, 0, act, random.Random(0))
    eq(st.units[0].shield_cur, 3,
       '主格 A：換入者盾量＝離場時殘盾 3（不回滿）')


def test_4_preserve_pierce_flag():
    print('\n=== 4b. 深拷貝保留：穿透旗標跟人（BL-3 讀法A）===')
    eng, st = _fresh_state(variant='A')
    bench = st.benches[0][0]
    bench.shield_cur = 0
    bench.shield_max = 25
    bench.pierce_pending = True   # 手工設定「盾0待穿透」狀態
    act = Action('領航員', subkind='換角', target=0)
    eng.apply_action(st, 0, act, random.Random(0))
    check(st.units[0].shield_cur == 0 and st.units[0].pierce_pending,
         '主格 A：換入者盾0＋穿透旗標亮兩者都跟著人保留')
    # 驗證旗標真的會讓下一擊全額穿透：對 shield_cur==0 的單位打一擊，
    # core.resolve_attack 的護盾狀態機本身就是「盾0→全額穿透→回滿」，
    # 這裡驗證換角後這個狀態機起點正確銜接（不是被重置成滿盾）。
    # 換入者（壁壘型）帶力場10，攻擊需先扣過力場才輪到護盾判定——用
    # 30 傷害（過力場後剩20）確保命中護盾狀態機，避免力場把整擊吃光
    # 導致「有沒有穿透」測不出來（力場與護盾是結算順序上的兩關）。
    field = st.units[0].field
    loss = b1._b1_resolve_attack(st.units[0], 30, 1, random.Random(0),
                                 dodge_mode='機率制', field_overload='關',
                                 cur_round=st.round_no)
    eq(loss, 30 - field,
       '穿透旗標保留下，換角後第一擊過力場後全額穿透（無護盾吸收）')
    eq(st.units[0].shield_cur, st.units[0].shield_max,
       '該穿透擊之後護盾回滿（護盾狀態機正常運作，僅入場態未被洗掉）')


def test_4_preserve_overload_absolute_timer():
    print('\n=== 4c. 深拷貝保留：過載絕對計時跨換角不凍結（BL-1）===')
    eng, st = _fresh_state(variant='A')
    bench = st.benches[0][0]
    bench.field_disabled = True
    bench.overload_until_round = st.round_no + 2   # 離場時還剩 2 回合到期
    act = Action('領航員', subkind='換角', target=0)
    eng.apply_action(st, 0, act, random.Random(0))
    eq(st.units[0].overload_until_round, st.round_no + 2,
       '換角瞬間：到期回合數原封不動跟人保留（不是重新計時、不是凍結成固定剩餘量）')

    # 模擬「離場期間回合數照樣推進」：把 st.round_no 往前推 3 輪（超過到期
    # 回合），驗證即使這名單位一直在後備、下次任何攻擊結算都會偵測到
    # 已過期並解除過載——證明計時是跟著「絕對回合數」走、不是跟著
    # 「這個單位有沒有上場」走（即離場不凍結，BL-1 讀法A的核心）。
    st.round_no += 3
    loss = b1._b1_resolve_attack(st.units[0], 10, 1, random.Random(0),
                                 dodge_mode='機率制', field_overload='關',
                                 cur_round=st.round_no)
    check(not st.units[0].field_disabled,
         '離場期間到期回合已過（絕對回合數判定），力場過載自動解除、不受凍結')
    check(st.units[0].overload_until_round is None,
         '過載到期後 overload_until_round 歸零（None）')


# ==================================================================
# 5. B 變體全重置（BL-6）：盾回滿＋過載解除＋穿透旗標清除
# ==================================================================

def test_5_variant_b_full_reset():
    print('\n=== 5. B 變體：換入者防禦全重置（dir1 v0 完整語義）===')
    eng, st = _fresh_state(variant='B')
    bench = st.benches[0][0]
    bench.shield_cur = 3
    bench.shield_max = 25
    bench.field_disabled = True
    bench.overload_until_round = st.round_no + 5
    bench.pierce_pending = True
    act = Action('領航員', subkind='換角', target=0)
    eng.apply_action(st, 0, act, random.Random(0))
    u = st.units[0]
    eq(u.shield_cur, u.shield_max, 'B 變體：換入者護盾回滿')
    check(not u.field_disabled, 'B 變體：力場過載解除（field_disabled=False）')
    check(u.overload_until_round is None,
         'B 變體：過載到期絕對回合數一併清除（不是只清 field_disabled）')
    check(not u.pierce_pending, 'B 變體：穿透旗標清除')


def test_5_variant_a_vs_b_contrast():
    print('\n=== 5b. A/B 對照：同一組離場狀態，兩變體行為相反 ===')
    for variant, expect_shield in (('A', 4), ('B', 25)):
        eng, st = _fresh_state(variant=variant)
        bench = st.benches[0][0]
        bench.shield_cur = 4
        bench.shield_max = 25
        act = Action('領航員', subkind='換角', target=0)
        eng.apply_action(st, 0, act, random.Random(0))
        eq(st.units[0].shield_cur, expect_shield,
           '變體 %s：換入者盾量＝%d' % (variant, expect_shield))


# ==================================================================
# 6. 安全網只扣上場者＋方級豁免（BL-2）
# ==================================================================

def test_6_safety_net_active_only():
    print('\n=== 6a. 安全網只扣上場者，後備不扣 ===')
    eng, st = _fresh_state(safety_net_start=1, safety_net_base=5,
                           safety_net_step=0)
    st.round_no = 1
    st.damage_this_turn = {0: 0, 1: 0}
    bench_hp_before = st.benches[0][0].hp
    active_hp_before = st.units[0].hp
    triggered = eng.apply_safety_net(st)
    check(triggered, '安全網於指定回合觸發')
    eq(st.units[0].hp, active_hp_before - 5, '上場者被扣 5 HP（基值）')
    eq(st.benches[0][0].hp, bench_hp_before,
       '後備 HP 完全不受安全網影響（只扣上場者）')


def test_6_safety_net_side_level_exemption():
    print('\n=== 6b. 安全網豁免以「方」為準，非上場者個人 ===')
    eng, st = _fresh_state(safety_net_start=1, safety_net_base=5,
                           safety_net_step=0)
    st.round_no = 1
    # side0 本回合「該方」造成過傷害（不管是誰打的，這裡直接標記
    # damage_this_turn，對齊 BL-2「跟方不跟單名」的豁免判準）
    st.damage_this_turn = {0: 7, 1: 0}
    hp0_before = st.units[0].hp
    hp1_before = st.units[1].hp
    eng.apply_safety_net(st)
    eq(st.units[0].hp, hp0_before, 'side0 本回合有造傷＝方級豁免，不扣血')
    eq(st.units[1].hp, hp1_before - 5, 'side1 本回合無造傷＝正常扣血')


def test_6_safety_net_escalation():
    print('\n=== 6c. 安全網遞增制：起點/基值/步幅 ===')
    eng, st = _fresh_state(safety_net_start=15, safety_net_base=5,
                           safety_net_step=4)
    st.damage_this_turn = {0: 0, 1: 0}
    for rd, expect_amount in ((14, None), (15, 5), (16, 9), (17, 13)):
        st.round_no = rd
        hp_before = st.units[0].hp
        st.units[0].hp = 50   # 每次重置避免累積扣到 0 提早出場
        triggered = eng.apply_safety_net(st)
        if expect_amount is None:
            check(not triggered, '第 %d 回合（早於起點15）不觸發安全網' % rd)
        else:
            eq(50 - st.units[0].hp, expect_amount,
              '第 %d 回合安全網扣血量＝%d（基值5+步幅4×已過回合數）' %
              (rd, expect_amount))


# ==================================================================
# 7. 費2 旗標跨換角（BR-4）：旗標跟隊、換角不清除
# ==================================================================

def test_7_cost2_flag_survives_switch():
    print('\n=== 7. 費2「次數+1」旗標跨換角仍生效（BR-4 讀法A）===')
    eng, st = _fresh_state()
    # 甲（上場者）宣告費2：掛「下一張晶片能力面攻擊次數+1」旗標
    st.resources[0] = 2
    ok = eng.use_resource_cost2(st, 0)
    check(ok, '費2 資源足夠、宣告成功')
    check(st.config.extra.get('_hits_bonus_pending_0') is True,
         '旗標已設置（per-side，位於 config.extra）')

    # 換角：甲換下、乙（後備）換上
    act = Action('領航員', subkind='換角', target=0)
    eng.apply_action(st, 0, act, random.Random(0))
    check(st.config.extra.get('_hits_bonus_pending_0') is True,
         '換角後旗標仍在（旗標跟隊/per-side，不隨上場者變動而清除）')

    # 乙（換角後的 side0 上場者）使用一張晶片能力面攻擊敵方（side1），
    # 驗證 hits+1 真的生效——旗標是 per-side（_hits_bonus_pending_0），
    # 攻擊方仍是 side0（人換了、方沒換），故用 side=0 呼叫。把防守方
    # （side1）的防禦欄位手工清零，讓傷害結算是純粹的「dmg×hits」已知
    # 值、不受閃避機率/力場/護盾干擾（本測項只關心旗標的 hits 加成，
    # 不是防禦結算本身，防禦結算已由共用 tests.py §6.1 回歸覆蓋）。
    db = shared_chip_db()
    chip = db[1]   # 加農砲：直射4，25dmg×1hit
    eq(chip.ability_face['hits'], 1, '前提：加農砲原始 hits=1')
    st.units[0].pos = (4, 2)
    st.units[1].pos = (5, 2)   # 同排、列距1，落在直射4射程內
    st.units[1].evasion = 0
    st.units[1].field = 0
    st.units[1].shield_cur = 0
    st.units[1].shield_max = 0
    action = Action('晶片', chip_id=1, face='能力', target=None)
    # 直接呼叫 _apply_chip_ability 驗證旗標消耗與加成（繞開手牌檢查，
    # 聚焦在旗標本身的跨換角生效邏輯，符合「手工構造已知值」精神）
    dealt = eng._apply_chip_ability(st, 0, chip, action, random.Random(0))
    eq(dealt, 50, '費2 旗標生效：加農砲 25dmg×(1+1)hits=50（乙享受了甲掛的旗標）')
    check(st.config.extra.get('_hits_bonus_pending_0') is False
         or not st.config.extra.get('_hits_bonus_pending_0'),
         '旗標使用後消耗歸位（一次性）')


# ==================================================================
# 8. 首回合換角合法（BR-1）
# ==================================================================

def test_8_first_round_switch_legal():
    print('\n=== 8. 首回合換角合法（先手僅1行動，可拿去換角）===')
    eng, st = _fresh_state()
    st.round_no = 1
    st.first_mover = 0
    pairs = eng.legal_action_pairs(st, 0, first_comp_limit='一行動')
    change_pairs = [p for p in pairs
                   if p[0].kind == '領航員' and p[0].subkind == '換角']
    check(len(change_pairs) > 0,
         '首回合（一行動限制下）換角仍在合法組合中出現')
    for p in change_pairs:
        eq(p[1].kind, 'pass', '首回合換角組合的第二行動必為 pass（僅1行動）')


# ==================================================================
# 執行
# ==================================================================

def main():
    tests = [
        test_1_switch_legality_two_alive,
        test_1_switch_legality_one_dead,
        test_2_semantic_lock3_no_self_attack_after_switch,
        test_3_forced_switch_no_action_cost,
        test_3_forced_switch_center_cell,
        test_3_forced_switch_no_trap_no_pickup,
        test_4_preserve_shield_value,
        test_4_preserve_pierce_flag,
        test_4_preserve_overload_absolute_timer,
        test_5_variant_b_full_reset,
        test_5_variant_a_vs_b_contrast,
        test_6_safety_net_active_only,
        test_6_safety_net_side_level_exemption,
        test_6_safety_net_escalation,
        test_7_cost2_flag_survives_switch,
        test_8_first_round_switch_legal,
    ]
    for t in tests:
        try:
            t()
        except Exception:
            global _FAIL
            _FAIL += 1
            _FAILURES.append((t.__name__, traceback.format_exc()))
            print('  [例外] %s' % t.__name__)
            print(traceback.format_exc())

    print('\n' + '=' * 50)
    print('通過 %d，失敗 %d' % (_PASS, _FAIL))
    if _FAILURES:
        print('\n失敗清單：')
        for name, detail in _FAILURES:
            print('- %s: %s' % (name, detail))
        sys.exit(1)
    else:
        print('全部通過。')


if __name__ == '__main__':
    main()
