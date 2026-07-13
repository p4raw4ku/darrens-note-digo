# -*- coding: utf-8 -*-
"""A6 僵持解剖 Part1：零傷害回合三因分類器。

判定順序寫死（規格明定，先1後2後3）：
  1. 打不到：該回合（該側該手）不存在任何「能命中對手」的合法攻擊行動。
     幾何上，legal_actions() 產生的攻擊類行動一律先經 enumerate_targets()
     過濾成「只列會命中的」（見 core.py cells_hit/range_can_reach/
     enumerate_targets），因此「合法攻擊行動集合是否為空」直接等價於
     「這回合有沒有任何攻擊能碰到對手」——不需要另外重算幾何。
  2. 打不痛：存在至少一個能命中的攻擊行動，但把它排進兩行動組合、經完整
     resolve_attack 結算（含護盾/閃避/力場）後，全部「含攻擊」的合法配對
     期望淨傷都 ≤ 0（被防禦全吸收，即護盾未穿透、力場削到 0、閃避全擋）。
  3. 不想打：存在期望淨傷 > 0 的合法配對，但策略本回合實際選的配對造成
     的傷害是 0（选了别的——撿資源/走位/佈陷阱/回復…）。

「期望淨傷」的定義與 greedy_damage／resource_aware 同一把尺：用
policies._expected_pair_damage()（v1.1 全域檔採 dodge_mode='超額削減'，
_damage_is_deterministic 恆真，故每個 pair 只需單次 resolve_attack 模拟、
不必抽樣——與策略實際評分時的確定性路徑完全一致，無估值器基準不一致
的風險，見報告可信度聲明）。

本模組只讀 GameState／Engine 既有介面，不修改任何結算邏輯；靠
InstrumentedTakeTurn 這個 mixin 在 take_turn 開頭「攔截」一次（用
engine.legal_action_pairs 現算，不改變策略實際呼叫路徑本身），把分類
結果掛進一個外部收集器（每局一個 list），而非塞進 GameState/GameRecord
（避免碰 __slots__、不動 core.py）。
"""
from policies import _expected_pair_damage, _decision_seed, _sub_rng


ATTACK_TYPES = ('attack',)


def _action_is_attack(engine, action):
    """單一 Action 是否為『攻擊類』（領航員自攻／晶片能力面攻擊，含推拉位移
    附帶的 on_hit 攻擊——on_hit 本身仍是 attack 型能力面，dmg/hits 已含在內）。
    """
    if action.kind == '領航員' and action.subkind == '攻擊':
        return True
    if action.kind == '晶片' and action.face == '能力':
        chip = engine.chips[action.chip_id]
        return chip.ability_face.get('type') in ATTACK_TYPES
    return False


def _pair_has_attack(engine, pair):
    return any(_action_is_attack(engine, a) for a in pair)


def classify_turn(engine, st, side, rng_for_eval):
    """在策略選擇之前呼叫。回傳 (label, detail)。

    label ∈ {'打不到', '打不痛', '有淨傷機會'}——第三類「不想打」需要事後
    比對『策略實際造成的傷害是否為0』，本函式只能判到「這回合客觀上有沒有
    淨傷機會」，留給呼叫方（在拿到實際 dealt_total 後）決定最終三分類。
    """
    first_comp_limit = None
    if (st.config.first_turn_comp == '一行動'
            and st.round_no == 1 and side == st.first_mover):
        first_comp_limit = '一行動'
    pairs = engine.legal_action_pairs(st, side, first_comp_limit)

    # 1. 打不到：合法單一行動中有沒有任何攻擊類（用 legal_actions 的第一層即可
    #    判斷是否存在攻擊類行動；pairs 是其組合，含攻擊的 pair 存在 <=> 存在
    #    攻擊類單一行動）。
    attack_pairs = [p for p in pairs if _pair_has_attack(engine, p)]
    if not attack_pairs:
        return '打不到', {'合法配對數': len(pairs), '含攻擊配對數': 0}

    # 2. 打不痛：對每個含攻擊的 pair 算期望淨傷（與 greedy/resource_aware
    #    同一把尺：_expected_pair_damage，v1.1 檔位下為確定性單次模拟）。
    ds = _decision_seed(rng_for_eval)
    best_net = 0.0
    net_values = []
    samples = max(1, st.config.expect_samples)
    for pair in attack_pairs:
        sub = _sub_rng(ds, pair)
        net = _expected_pair_damage(engine, st, side, pair, sub, samples)
        net_values.append(net)
        if net > best_net:
            best_net = net
    if best_net <= 0.0:
        return '打不痛', {'含攻擊配對數': len(attack_pairs),
                        '最佳期望淨傷': best_net,
                        '淨傷分佈樣本': net_values[:5]}

    # 3. 客觀上有淨傷機會（>0）——是否「不想打」留給呼叫方核對實際 dealt。
    return '有淨傷機會', {'含攻擊配對數': len(attack_pairs),
                       '最佳期望淨傷': best_net}


def finalize_label(pre_label, actual_dealt):
    """pre_label 是 classify_turn() 的分類；actual_dealt 是該回合（該側）
    實際造成的 HP 傷害（st.damage_this_turn[side]，來自策略真正選擇後的
    結算結果——與 pre 評估用同一 resolve_attack 路徑，只是策略可能選了
    不同的 pair）。

    回傳最終三分類之一：'打不到' / '打不痛' / '不想打' / None（非零傷害
    回合，不需要分類）。
    """
    if actual_dealt > 0:
        return None
    if pre_label == '打不到':
        return '打不到'
    if pre_label == '打不痛':
        return '打不痛'
    # pre_label == '有淨傷機會' 但實際 dealt == 0 → 策略選了別的
    return '不想打'
