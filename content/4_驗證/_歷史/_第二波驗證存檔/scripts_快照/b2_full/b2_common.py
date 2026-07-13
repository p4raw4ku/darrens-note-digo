# -*- coding: utf-8 -*-
"""B2 先導共用工具：v1.1 全域檔組裝（單進程、不用 multiprocessing）。

沿用 engine 既有 v11_calibrate.py 的 CHAMPION 配置與 V11Dir3Engine/
V11Dir2Engine 類別、search_v1.make_v1_config 等既有函式——本檔不重算數值、
只用 n_workers=1 呼叫既有單進程路徑（_run_tasks(fn, tasks, 1) 內部就是
plain for-loop，未觸碰 mp.Pool）。

方向一覆寫（HP47/網基3步幅+3）本 B2 先導步驟2/3 不需要（規格只測 dir3 與
dir2）；步驟4 全量成本預估涵蓋 3 方向，本檔額外提供 dir1 建局函式僅供該項
抽樣測壁鐘之用，不進循環賽。
"""
import os
import sys
import time

ENGINE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                           'engine'))
sys.path.insert(0, ENGINE_DIR)

import random  # noqa: E402
from core import GameConfig  # noqa: E402
from chips import shared_chip_db  # noqa: E402
from setups import dir2_chip_db, make_dir1_setup  # noqa: E402
from policies import make_policy  # noqa: E402
import search_v1 as SV1  # noqa: E402
from dir2 import Dir2OverlayEngine, make_dir2_overlay_setup  # noqa: E402
import v11_calibrate as V11  # noqa: E402

CHAMPION = V11.CHAMPION  # v1.1 全域檔（閃4/盾10/場5/HP100/自攻10x1/迴復30限2/網起15遞增）

# ---- 安全網起點（規格「安全網起點15遞增」）＋基值/步幅照 CHAMPION（基值10/步幅5）----
NET_START = 15
NET_BASE = CHAMPION['安全網基值']
NET_STEP = CHAMPION['安全網步幅']


def make_dir3_v11_config(seed, oneply_samples=50, expect_samples=50,
                         twoply_k=3):
    """dir3 v1.1 全域檔 GameConfig（沿用 search_v1.make_v1_config + 步幅覆寫）。"""
    cfg_dict = dict(SV1.BASE_CONFIG)
    cfg_dict['hp'] = CHAMPION['hp_global']
    cfg_dict['閃避帶'] = CHAMPION['閃避帶']
    cfg_dict['護盾帶'] = CHAMPION['護盾帶']
    cfg_dict['力場帶'] = CHAMPION['力場帶']
    cfg_dict['dodge_mode'] = CHAMPION['dodge_mode']
    cfg_dict['領航員自攻'] = CHAMPION['領航員自攻']
    cfg_dict['迴復裝置'] = ('回', CHAMPION['迴復量'], '限2')
    cfg_dict['安全網起點'] = NET_START
    cfg_dict['安全網模式'] = CHAMPION['安全網模式']
    cfg_dict['先手補償'] = CHAMPION['先手補償']
    gcfg = SV1.make_v1_config(cfg_dict, seed, oneply_samples=oneply_samples,
                             expect_samples=expect_samples)
    gcfg.extra['安全網基值'] = NET_BASE
    gcfg.extra['安全網步幅'] = NET_STEP
    gcfg.extra['twoply_k'] = twoply_k
    return gcfg, cfg_dict


def build_dir3_game(seed, oneply_samples=50, expect_samples=50, twoply_k=3,
                    def_a='護盾', def_b='護盾'):
    gcfg, cfg_dict = make_dir3_v11_config(seed, oneply_samples, expect_samples,
                                          twoply_k)
    setup = SV1.make_v1_setup_with_draw(cfg_dict, def_a, def_b)
    eng = V11.V11Dir3Engine(shared_chip_db())
    return eng, gcfg, setup


def make_dir2_v11_config(seed, oneply_samples=50, expect_samples=50,
                         twoply_k=3, resource_rate=2):
    extra = {
        '迴復量': CHAMPION['迴復量'], '迴復每局上限': CHAMPION['迴復每局上限'],
        '安全網模式': CHAMPION['安全網模式'], '安全網基值': NET_BASE,
        '安全網步幅': NET_STEP, '鎖列動態': True, 'resource_enabled': True,
        '資源週期': resource_rate, 'twoply_k': twoply_k,
    }
    gcfg = GameConfig(
        direction=2, hp=CHAMPION['hp_global'],
        first_turn_comp=CHAMPION['先手補償'], dodge_mode=CHAMPION['dodge_mode'],
        field_overload='關', safety_net_turn=NET_START, max_turns=60,
        seed=seed, oneply_samples=oneply_samples, expect_samples=expect_samples,
        hand_limit=6, draw_per_turn=1, starting_hand=4, extra=extra)
    return gcfg


def build_dir2_game(seed, oneply_samples=50, expect_samples=50, twoply_k=3,
                    proto_a='游擊', proto_b='壁壘'):
    gcfg = make_dir2_v11_config(seed, oneply_samples, expect_samples, twoply_k)
    setup = make_dir2_overlay_setup(proto_a, proto_b, use_v2_field=True)
    eng = V11.V11Dir2Engine(dir2_chip_db())
    return eng, gcfg, setup


def make_dir1_v11_config(seed, oneply_samples=50, expect_samples=50,
                         twoply_k=3):
    """dir1 v1.1 覆寫（HP47/網基3/步幅+3），僅供步驟4 抽樣測壁鐘用。"""
    extra = {
        '迴復量': CHAMPION['迴復量'], '迴復每局上限': CHAMPION['迴復每局上限'],
        '安全網模式': CHAMPION['安全網模式'], '安全網基值': 3, '安全網步幅': 3,
        '鎖列動態': True, 'twoply_k': twoply_k,
    }
    gcfg = GameConfig(
        direction=1, hp=47, first_turn_comp=CHAMPION['先手補償'],
        dodge_mode=CHAMPION['dodge_mode'], field_overload='關',
        safety_net_turn=NET_START, max_turns=60, seed=seed,
        oneply_samples=oneply_samples, expect_samples=expect_samples,
        hand_limit=6, draw_per_turn=1, starting_hand=4, extra=extra)
    return gcfg


def build_dir1_game(seed, oneply_samples=50, expect_samples=50, twoply_k=3):
    gcfg = make_dir1_v11_config(seed, oneply_samples, expect_samples, twoply_k)
    setup = make_dir1_setup()
    eng = V11.V11Dir1Engine(shared_chip_db())
    return eng, gcfg, setup


def _play_from_state_with_hp_snapshot(engine, config, st, policy_a, policy_b):
    """輪2 全量：等效 V11._play_from_state（見 v11_calibrate.py），但補上
    core.py Engine.play() 才有做的 B6 hp_by_round 逐回合快照（_snapshot_hp）。

    v11_calibrate.py 的 _play_from_state 是給「已建好、可能覆寫 first_mover」
    的外部 st 用的獨立回合迴圈，未呼叫 core.py 的 _snapshot_hp（那是
    Engine.play() 自己內建 new_game 時才會走的路徑，兩者互不相通——這是
    b6_engine_v2 known gap，round1 A5 用的是 eng.play() 沒有覆寫
    first_mover 的需求所以沒踩到）。本函式＝_play_from_state 邏輯逐行對齊
    ＋補三處快照呼叫（開局、每回合結束、對局提前結束時補尾），確保 B2 全量
    需要的 advantage_series／comeback_rate／tension_metrics／
    safety_net_decisive_rate 四指標都能算。
    """
    import random as _random
    from core import GameRecord
    rng = _random.Random(config.seed)
    policies = [policy_a, policy_b]
    rec = GameRecord()
    rec.config = config
    rec.first_mover = st.first_mover
    rec.hp_by_round.append(
        (0, {0: engine.team_hp(st, 0), 1: engine.team_hp(st, 1)}))  # 開局快照
    st.round_no = 1
    while True:
        for side in (st.first_mover, 1 - st.first_mover):
            st.damage_this_turn = {0: 0, 1: 0}
            engine.take_turn(st, side, policies[side], rng)
            st.turn += 1
            if engine.check_over(st):
                break
        if st.over:
            break
        trig = engine.apply_safety_net(st)
        if trig:
            rec.safety_net_triggered = True
        rec.hp_by_round.append(
            (st.round_no, {0: engine.team_hp(st, 0),
                          1: engine.team_hp(st, 1)}))
        if engine.check_over(st):
            break
        if st.round_no >= config.max_turns:
            st.over = True
            st.winner = None
            st.over_reason = '觸頂平局'
            break
        st.round_no += 1
    rec.winner = st.winner
    rec.reason = st.over_reason
    rec.rounds = st.round_no
    rec.turns = st.turn
    rec.log = st.log
    rec.final_hp = {0: (st.units[0].hp if st.units[0] else 0),
                    1: (st.units[1].hp if st.units[1] else 0)}
    if not rec.hp_by_round or rec.hp_by_round[-1][0] != st.round_no:
        rec.hp_by_round.append(
            (st.round_no, {0: engine.team_hp(st, 0),
                          1: engine.team_hp(st, 1)}))
    return rec


def play_one(direction, pol_a, pol_b, seed, first_mover=None,
            oneply_samples=50, expect_samples=50, twoply_k=3,
            dir2_proto_a='游擊', dir2_proto_b='壁壘'):
    """建局＋跑一局，回傳 GameRecord（含 hp_by_round，供 B6 四指標使用）。

    dir2_proto_a/b：僅方向二使用。輪2 全量電池教訓——build_dir2_game 預設值
    '游擊'(閃8盾15) 對 '壁壘'(場10盾25) 是不對稱防禦（壁壘明顯更硬），round1
    A6 報告已明訂：量測『純策略勝率』一律改用鏡像原型（游擊/游擊）隔離防禦
    不對稱，only 用不對稱原型做『對位健康』類實驗才有意義。B2 全量電池的目的
    是策略勝率（3策略×3策略循環賽），故呼叫方應傳入鏡像 proto_a=proto_b。
    """
    if direction == 3:
        eng, gcfg, setup = build_dir3_game(seed, oneply_samples, expect_samples,
                                           twoply_k)
    elif direction == 2:
        eng, gcfg, setup = build_dir2_game(seed, oneply_samples, expect_samples,
                                           twoply_k, proto_a=dir2_proto_a,
                                           proto_b=dir2_proto_b)
    elif direction == 1:
        eng, gcfg, setup = build_dir1_game(seed, oneply_samples, expect_samples,
                                           twoply_k)
    else:
        raise ValueError('未知 direction=%r' % direction)
    st = eng.new_game(gcfg, setup)
    if first_mover is not None:
        st.first_mover = first_mover
        st.side_to_move = first_mover
    rec = _play_from_state_with_hp_snapshot(eng, gcfg, st, make_policy(pol_a),
                                            make_policy(pol_b))
    return rec


def timed_play_one(direction, pol_a, pol_b, seed, first_mover=None,
                   oneply_samples=50, expect_samples=50, twoply_k=3,
                   timeout_s=120, dir2_proto_a='游擊', dir2_proto_b='壁壘'):
    """跑一局並量壁鐘。超過 timeout_s 用 signal.alarm 中斷（單進程可行）、
    回傳 (rec_or_None, secs, timed_out_bool)。"""
    import signal

    class _TimeoutErr(Exception):
        pass

    def _handler(signum, frame):
        raise _TimeoutErr()

    old = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, timeout_s)
    t0 = time.time()
    try:
        rec = play_one(direction, pol_a, pol_b, seed, first_mover,
                       oneply_samples, expect_samples, twoply_k,
                       dir2_proto_a, dir2_proto_b)
        dt = time.time() - t0
        return rec, dt, False
    except _TimeoutErr:
        dt = time.time() - t0
        return None, dt, True
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def median(xs):
    if not xs:
        return float('nan')
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2.0


def percentile(xs, p):
    if not xs:
        return float('nan')
    s = sorted(xs)
    n = len(s)
    if n == 1:
        return s[0]
    k = (n - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, n - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)
