# -*- coding: utf-8 -*-
"""B6 尺 v2（metrics 擴充）驗收測試——手工構造已知軌跡，逐指標核值。

執行：vaultpy metrics_v2_tests.py（或 python3 metrics_v2_tests.py）。
純標準庫、不觸網、不改結算邏輯——只餵手造 GameRecord 給 metrics.py 新函式。
"""
import sys
import traceback

from core import GameRecord
import metrics as M

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


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol


def make_rec(hp_by_round, winner, rounds=None, log=None,
             safety_net_triggered=False):
    """建最小 GameRecord：只填 metrics_v2 用得到的欄位。"""
    rec = GameRecord()
    rec.hp_by_round = hp_by_round
    rec.winner = winner
    rec.rounds = rounds if rounds is not None else hp_by_round[-1][0]
    rec.log = log or []
    rec.safety_net_triggered = safety_net_triggered
    rec.final_hp = {0: hp_by_round[-1][1][0], 1: hp_by_round[-1][1][1]}
    return rec


# ==================================================================
# 1. 優勢軌跡 advantage_series
# ==================================================================

def test_advantage_series():
    # 甲乙初始各100，甲穩定壓制到70：adv = (100-30)/100=0.7 在終局
    hp = [(0, {0: 100, 1: 100}), (1, {0: 100, 1: 70}), (2, {0: 100, 1: 30})]
    rec = make_rec(hp, winner=0)
    series = M.advantage_series(rec)
    check(series[0] == (0, 0.0), 'adv(0)=0（開局對稱）', str(series))
    check(close(series[1][1], 0.3), 'adv(1)=0.3（甲多贏30/denom100）',
          str(series[1]))
    check(close(series[2][1], 0.7), 'adv(2)=0.7（甲多贏70/denom100）',
          str(series[2]))

    # 方向一三名合計：初始HP總和300（每名100），分母150；
    # 甲300 vs 乙150 → adv=(300-150)/150=1.0……實際上分母是
    # (300+300)/2=300，故 adv=(300-150)/300=0.5（三名合計只影響分母
    # 隨隊伍規模放大，不影響「初始HP總和之半」這條公式本身）。
    hp1 = [(0, {0: 300, 1: 300}), (1, {0: 300, 1: 150})]
    rec1 = make_rec(hp1, winner=0)
    s1 = M.advantage_series(rec1)
    check(close(s1[1][1], 0.5), '三名合計 denom 正確（adv=150/300=0.5）',
          str(s1))


# ==================================================================
# 2. 翻盤率 comeback_rate
# ==================================================================

def test_comeback_rate_monotone_crush():
    # 單調碾壓局：甲從頭到尾都領先（勝者=甲），adv 從不小於等於 -0.20
    hp = [(0, {0: 100, 1: 100}), (1, {0: 90, 1: 60}), (2, {0: 80, 1: 20}),
          (3, {0: 70, 1: 0})]
    rec = make_rec(hp, winner=0)
    out = M.comeback_rate([rec])
    check(out['翻盤率'] == 0.0, '單調碾壓局翻盤率=0', str(out))
    check(out['判定局數'] == 1, '判定局數=1（無平局）', str(out))


def test_comeback_rate_v_shape_reversal():
    # V 型逆轉局：乙在 t=2（滿足 t>=2 判準）大幅落後（乙視角 adv=-0.5，
    # <=-0.20），最終乙翻盤獲勝（winner=1）
    hp = [(0, {0: 100, 1: 100}),      # t0 adv(甲視角)=0
          (1, {0: 100, 1: 90}),       # t1 adv=+0.1（尚未深度落後）
          (2, {0: 90, 1: 40}),        # t2 adv=+0.5 → 乙視角-0.5（<=-0.20，t>=2成立）
          (3, {0: 0, 1: 80})]         # t3 乙翻盤獲勝
    rec = make_rec(hp, winner=1)
    out = M.comeback_rate([rec])
    check(out['翻盤率'] == 1.0, 'V型逆轉局翻盤率=1', str(out))


def test_comeback_rate_excludes_draws_and_t_lt_2():
    # 平局不計分母
    hp = [(0, {0: 100, 1: 100}), (1, {0: 50, 1: 50})]
    draw_rec = make_rec(hp, winner=None)
    out = M.comeback_rate([draw_rec])
    check(out['判定局數'] == 0, '平局不計入翻盤率分母', str(out))

    # t=1（t<2）就大幅落後但 t>=2 之後穩定回穩不算——這裡構造只在 t=1
    # 出現深度落後、t>=2 之後都未再出現 <=-0.20，翻盤率應為0
    hp2 = [(0, {0: 100, 1: 100}), (1, {0: 40, 1: 100}),  # t1 甲視角 adv=-0.6（但t<2不計）
           (2, {0: 60, 1: 40}), (3, {0: 80, 1: 0})]       # t2起甲已回穩、adv>=-0.20
    rec2 = make_rec(hp2, winner=0)
    out2 = M.comeback_rate([rec2])
    check(out2['翻盤率'] == 0.0, 't<2 的深度落後不算翻盤（判準只看t>=2）',
          str(out2))


# ==================================================================
# 3. 張力三量 tension_metrics
# ==================================================================

def test_tension_volatility():
    # 兩局：adv 序列已知，波動度=|delta|全局平均
    hp_a = [(0, {0: 100, 1: 100}), (1, {0: 90, 1: 100}),  # adv 0 -> -0.1
            (2, {0: 100, 1: 80})]                          # adv -0.1 -> 0.2
    rec_a = make_rec(hp_a, winner=0)
    out = M.tension_metrics([rec_a])
    # deltas: |(-0.1)-0|=0.1, |0.2-(-0.1)|=0.3 → 平均0.2
    check(close(out['波動度'], 0.2), '波動度＝|adv差|全局平均', str(out))


def test_tension_lead_swaps_and_decisive_point():
    # 領先易手：甲先領先(t1)、乙反超(t2)、甲再反超(t3)＝2次易手；
    # 最後一次跨零在 t3、對局共3回合 → 決勝時點=3/3=1.0
    hp = [(0, {0: 100, 1: 100}),   # t0 adv=0（零帶，不計號）
          (1, {0: 120, 1: 100}),   # t1 adv=+0.2 →首次脫離零帶，不算易手
          (2, {0: 90, 1: 120}),    # t2 adv=-0.3 → 易手1（+→-）
          (3, {0: 130, 1: 90})]    # t3 adv=+0.4 → 易手2（-→+）
    rec = make_rec(hp, winner=0, rounds=3)
    out = M.tension_metrics([rec])
    check(out['領先易手次數_平均'] == 2, '領先易手次數=2', str(out))
    check(close(out['決勝時點_平均'], 1.0), '決勝時點=最後跨零回合3/總回合3=1.0',
          str(out))


def test_tension_zero_band_ignored():
    # 零帶抖動（|adv|<0.02）不應被算成易手
    hp = [(0, {0: 100, 1: 100}), (1, {0: 101, 1: 100}),   # adv=0.01（零帶）
          (2, {0: 99, 1: 100}),                            # adv=-0.01（零帶）
          (3, {0: 130, 1: 100})]                           # adv=0.3（脫離零帶，首次不算易手）
    rec = make_rec(hp, winner=0, rounds=3)
    out = M.tension_metrics([rec])
    check(out['領先易手次數_平均'] == 0, '零帶抖動不計入易手次數', str(out))
    check(out['無跨零局數'] == 1, '全程零帶或僅單邊脫離＝無跨零', str(out))


# ==================================================================
# 4. 安全網決定勝負率 safety_net_decisive_rate
# ==================================================================

def test_safety_net_kill_shot():
    # 安全網補刀局：敗者在「安全網」事件觸發回合HP降至0（致勝一擊來源=安全網）
    log = [{'event': '安全網', 'round': 3}]
    hp = [(0, {0: 100, 1: 100}), (1, {0: 100, 1: 30}),
          (2, {0: 100, 1: 10}), (3, {0: 100, 1: 0})]
    rec = make_rec(hp, winner=0, log=log, safety_net_triggered=True)
    out = M.safety_net_decisive_rate([rec])
    check(out['安全網決定勝負率'] == 1.0, '安全網補刀局判定為網決定', str(out))
    check(out['安全網決定局數'] == 1, '安全網決定局數=1', str(out))


def test_safety_net_pure_combat_kill():
    # 全程無安全網事件、純戰鬥擊殺——不應被判定為網決定
    log = [{'event': '自攻', 'side': 0, 'damage': 100, 'round': 1}]
    hp = [(0, {0: 100, 1: 100}), (1, {0: 100, 1: 0})]
    rec = make_rec(hp, winner=0, log=log, safety_net_triggered=False)
    out = M.safety_net_decisive_rate([rec])
    check(out['安全網決定勝負率'] == 0.0, '純戰鬥擊殺不判定為網決定', str(out))


def test_safety_net_share_threshold():
    # 敗者總失血中安全網佔比 >=50%：戰鬥造成40、安全網造成60（共100失血、
    # 佔比60% >= 閾值），且敗者非在安全網回合死亡（改在下一回合純戰鬥擊殺，
    # 用來測「非致勝一擊但佔比達標」這條路徑）。
    log = [
        {'event': '自攻', 'side': 0, 'damage': 40, 'round': 1},
        {'event': '安全網', 'round': 2},   # 甲乙各自扣30（乙未造傷、甲亦未造傷此回合）
        {'event': '自攻', 'side': 0, 'damage': 30, 'round': 3},  # 補刀（非安全網回合）
    ]
    # t0: 100/100; t1: 甲未變, 乙 100-40=60（戰鬥40）
    # t2: 安全網：甲100-30=70，乙60-30=30（此回合皆未造傷，對稱各扣30）
    # t3: 乙 30-30=0（純戰鬥30，甲不變）
    hp = [(0, {0: 100, 1: 100}), (1, {0: 100, 1: 60}),
          (2, {0: 70, 1: 30}), (3, {0: 70, 1: 0})]
    rec = make_rec(hp, winner=0, log=log, safety_net_triggered=True)
    out = M.safety_net_decisive_rate([rec])
    # 敗者(乙)總失血=100-0=100；安全網損失=30；佔比30/100=0.30 < 0.5
    # 這是「不達標」對照組，驗證判準不會誤判佔比不足的局
    check(out['安全網決定勝負率'] == 0.0,
          '安全網佔比30%（<50%閾值）不判定為網決定', str(out))


def test_safety_net_share_threshold_positive():
    # 佔比達標路徑（(b)）獨立測試：致勝一擊在 t3 是純戰鬥（非安全網回合），
    # 但敗者(乙)全局總失血中安全網貢獻 60% >= 50% 閾值 → 仍應判定為網決定。
    log = [
        {'event': '自攻', 'side': 0, 'damage': 10, 'round': 1},
        {'event': '安全網', 'round': 2},
        {'event': '自攻', 'side': 0, 'damage': 10, 'round': 3},
    ]
    # t0:100/100 → t1:乙100-10=90(戰鬥10) → t2:安全網對稱各扣30(甲70/乙60)
    # → t3:乙60-10=50(純戰鬥10，致勝一擊；乙未歸零，僅驗證佔比路徑非致死路徑)
    hp = [(0, {0: 100, 1: 100}), (1, {0: 100, 1: 90}),
          (2, {0: 70, 1: 60}), (3, {0: 70, 1: 50})]
    rec = make_rec(hp, winner=0, log=log, safety_net_triggered=True)
    out = M.safety_net_decisive_rate([rec])
    # 敗者(乙)總失血=100-50=50；安全網損失=90-60=30；佔比30/50=0.6>=0.5
    check(out['安全網決定勝負率'] == 1.0,
          '佔比60%達標（非致勝一擊，走(b)路徑）判定為網決定', str(out))


def test_safety_net_trigger_rate_vs_decisive_rate_distinct():
    # 觸發率(寬鬆) vs 決定率(嚴格)應可並存不同值：
    # 一局安全網有觸發但只佔敗者失血20%（不達標、也非致勝一擊）
    log = [
        {'event': '自攻', 'side': 0, 'damage': 80, 'round': 1},
        {'event': '安全網', 'round': 2},
    ]
    hp = [(0, {0: 100, 1: 100}), (1, {0: 100, 1: 20}),
          (2, {0: 90, 1: 10})]
    rec = make_rec(hp, winner=0, log=log, safety_net_triggered=True,
                   rounds=2)
    # 乙未歸零，補一個純戰鬥終結回合
    hp3 = hp + [(3, {0: 90, 1: 0})]
    log3 = log + [{'event': '自攻', 'side': 0, 'damage': 10, 'round': 3}]
    rec3 = make_rec(hp3, winner=0, log=log3, safety_net_triggered=True)
    out = M.safety_net_decisive_rate([rec3])
    check(out['安全網觸發率_判定局'] == 1.0, '觸發率仍算有觸發（寬鬆判準）',
          str(out))
    check(out['安全網決定勝負率'] == 0.0,
          '決定率嚴格判準下不達標（觸發≠決定，兩者確實不同值）', str(out))


# ==================================================================
# 主入口
# ==================================================================

def main():
    print('B6 尺 v2（metrics 擴充）驗收測試')
    tests = [
        test_advantage_series,
        test_comeback_rate_monotone_crush,
        test_comeback_rate_v_shape_reversal,
        test_comeback_rate_excludes_draws_and_t_lt_2,
        test_tension_volatility,
        test_tension_lead_swaps_and_decisive_point,
        test_tension_zero_band_ignored,
        test_safety_net_kill_shot,
        test_safety_net_pure_combat_kill,
        test_safety_net_share_threshold,
        test_safety_net_share_threshold_positive,
        test_safety_net_trigger_rate_vs_decisive_rate_distinct,
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
