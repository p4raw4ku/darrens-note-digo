# -*- coding: utf-8 -*-
"""A1：猜測訊號對行動數——可推算度採樣模組。

問題（規格 round1/規格_輪1_全案.md「A1」節）：題1 核心張力「行動越少、放棄越是
訊號」從沒直測。本檔量測主指標「可推算度」＝尺③（手牌敏感度）的反向：
    可推算度 = 1 − 一致手牌比例
    一致手牌比例 = 在『與公開資訊一致的替代手牌』上，同一 greedy 估值器仍會
                  判定『實際觀察到的行動』為最佳行動的比例。

沿用 pillars.py 的抽樣機制改造（不重寫）：
  - 手牌重抽機制直接複用 pillars._hand_resample_flip 的核心手法（pool=手牌+
    牌庫、洗牌、重發同張數、sim_clone 複本），只把「比較基準」換掉。
  - greedy 估值器直接 import pillars.greedy_best_pair / greedy_value（同一把
    尺，不換其他策略當估值器——嚴防上輪教訓①：估值基準必須同一把尺）。

與 pillars._hand_resample_flip 的關鍵差異（嚴防上輪教訓②：抽樣行動必須＝
實際打出的行動）：
  pillars 尺③：比較『原手牌上 greedy_best_pair 算出的最佳行動』(base_pair，
    非對局策略的選擇) vs 『重抽手牌上 greedy_best_pair 算出的最佳行動』——
    問的是「手牌換了、greedy 自己的決策會不會變」，比較雙方都不是「真正打出
    的行動」。
  本檔 A1：比較『對局中真正施行的 actual_pair』(來自對局策略 greedy_damage/
    turtle，取自 _take_turn_sampled 骨架抓到的真實決策) vs 『重抽手牌上
    greedy_best_pair 算出的最佳行動』——問的是「這副替代手牌，用 greedy 這把
    尺去驗，站不站得住『這正是我們觀察到的那個行動』」。若替代手牌下 greedy
    選了別的行動（含 actual_pair 不再合法的情形），記為『不一致』；該手牌
    即被行動證據排除掉（計入可推算度的分子）。

抽樣次數：規格明定 200 副（非 pillars 預設的 10）；不像 pillars 一翻轉就
break——A1 要的是連續型『一致比例』，200 次要跑完整批。
"""
import random
import sys

from core import Action
from pillars import (greedy_best_pair, _action_signature,
                     _action_category_signature, _decision_seed, _sub_rng,
                     _choose_with_seed, _first_comp_limit)
from policies import make_policy


def _hand_resample_consistency(engine, st, side, actual_pair, k, samples, ds):
    """手牌重抽 k 次，問『這副替代手牌是否仍會用 greedy 產生 actual_pair』。

    改造自 pillars._hand_resample_flip：pool／洗牌／重發張數／sim_clone 手法
    照搬，比較基準換成傳入的 actual_pair（實際打出的行動，非 greedy 自己在
    原手牌上重算的行動）。回傳 (一致次數, 有效重抽次數) 或 None（手牌空/ 無
    法有效重抽）。兩種簽章粒度並列（精確含晶片id／類別只看行動種類），理由
    同 pillars 尺③註解：精確簽章才是規格字面『這副手牌會不會產生實際觀察到
    的行動』，類別簽章補充『至少同種戰術』的寬鬆版本，避免精確簽章因銅板局
    (n=200 副全洗、每次都幾乎全新手牌組合) 而使可推算度虛高。
    """
    hand_n = len(st.hands[side])
    if hand_n == 0:
        return None
    actual_fine = _action_signature(actual_pair)
    actual_coarse = _action_category_signature(actual_pair)
    pool = st.hands[side][:] + st.decks[side][:]
    fine_consistent = 0
    coarse_consistent = 0
    effective = 0
    for i in range(k):
        rng2 = random.Random((ds * 1000003 + i * 97) & 0x7fffffffffffffff)
        dup = st.sim_clone()
        combined = pool[:]
        rng2.shuffle(combined)
        dup.hands[side] = combined[:hand_n]
        dup.decks[side] = combined[hand_n:]
        # 與公開資訊一致：只重排手牌+牌庫的合併池、保張數——不改變對手看得到
        # 的『手牌張數』這個公開資訊，牌庫具體內容本就不公開（規格「與公開
        # 資訊一致的替代手牌」之意）。
        if sorted(dup.hands[side]) == sorted(st.hands[side]):
            continue   # 重抽後手牌多重集合與原手牌相同，不算一次有效重抽
        effective += 1
        ds2 = rng2.getrandbits(63)
        # 同一把尺：greedy_best_pair，與 actual_pair 來源（對局策略）無關，
        # 也與其餘副指標（尺①③）共用同一估值器，符合「估值基準同一把尺」。
        new_pair = greedy_best_pair(engine, dup, side, samples, ds2)
        if _action_signature(new_pair) == actual_fine:
            fine_consistent += 1
        if _action_category_signature(new_pair) == actual_coarse:
            coarse_consistent += 1
    if effective == 0:
        return None
    return {
        'k_effective': effective,
        'fine_consistent': fine_consistent,
        'coarse_consistent': coarse_consistent,
    }


def _take_turn_a1(eng, st, side, policy, rng, collect, resample_k, samples):
    """複刻 core.Engine.take_turn／pillars._take_turn_sampled 的骨架，在
    『抽牌後、決策前』取得 actual_pair 並做可推算度採樣。

    複刻理由與 pillars 相同：被採樣的行動必須就是實際施行的那手，policy 只能
    跑一次（重跑會推進/發散 rng）。
    """
    st.side_to_move = side
    st.actions_this_turn = []
    eng.hook_start_turn(st, side)
    eng.draw(st, side, st.config.draw_per_turn, rng)

    u = st.units[side]
    ds = _decision_seed(rng)
    first_comp = _first_comp_limit(st, side)
    actions = _choose_with_seed(eng, st, side, policy, ds)
    actions = eng._sanitize_actions(st, side, actions, first_comp)
    actual_pair = tuple(actions)

    # 可推算度採樣：對每個決策點都做（不分先後手——雙方對彼此都是『對手』，
    # 規格「對每個對手回合」在雙人對局裡即『每個行動方的回合，供另一方推算』）。
    if u is not None and u.alive and len(st.hands[side]) > 0:
        res = _hand_resample_consistency(eng, st, side, actual_pair,
                                         resample_k, samples, ds)
        if res is not None:
            collect['consistency'].append(res)
            collect['n_hand'].append(len(st.hands[side]))

    used = set()
    dealt_total = 0
    for act in actions:
        if act.category() != 'pass':
            used.add(act.category())
        dealt_total += eng.apply_action(st, side, act, rng)
        st.actions_this_turn.append(act)
        if st.units[1 - side] is None or not st.units[1 - side].alive:
            break
    st.damage_this_turn[side] = dealt_total
    eng.hook_end_turn(st, side)
    return dealt_total


def _play_and_sample_a1(eng, cfg, setup, policies, samples, resample_k,
                        max_decisions, first_mover=0):
    """跑一局（已組裝好的 eng/setup/cfg），逐決策點採可推算度資料。

    eng/setup 由呼叫端依 v1.1 全域檔組裝（search_v1.make_v1_config +
    make_v1_setup_with_draw + v11_calibrate.V11Dir3Engine），本函式只負責
    對局迴圈＋採樣，不重複組裝邏輯（複刻 v11_calibrate._play_from_state 的
    迴圈骨架，中段換成 _take_turn_a1 插采樣）。
    """
    st = eng.new_game(cfg, setup)
    st.first_mover = first_mover
    st.side_to_move = first_mover
    rng = random.Random(cfg.seed)
    pols = [make_policy(policies[0]), make_policy(policies[1])]

    collect = {'consistency': [], 'n_hand': [], 'dcount': 0}

    st.round_no = 1
    while collect['dcount'] < max_decisions:
        for side in (st.first_mover, 1 - st.first_mover):
            st.damage_this_turn = {0: 0, 1: 0} if side == st.first_mover \
                else st.damage_this_turn
            u = st.units[side]
            if u is None or not u.alive:
                continue
            collect['dcount'] += 1
            _take_turn_a1(eng, st, side, pols[side], rng, collect,
                         resample_k, samples)
            st.turn += 1
            if eng.check_over(st):
                break
        if st.over:
            break
        eng.apply_safety_net(st)
        if eng.check_over(st):
            break
        if st.round_no >= cfg.max_turns:
            break
        st.round_no += 1

    rounds = st.round_no
    winner = st.winner
    first_mover_out = st.first_mover
    safety_net_triggered = any(
        e.get('event') == '安全網' for e in st.log)
    return collect, {
        'rounds': rounds, 'winner': winner, 'first_mover': first_mover_out,
        'safety_net_triggered': safety_net_triggered,
        'over_reason': getattr(st, 'over_reason', None),
    }


# ==================================================================
# v1.1 全域檔組裝（共同約定：閃4 盾10 場5 HP100 自攻10×1 迴復回30限2
# 安全網起點15遞增(基10步幅5) 補償首回合1行動；對應 v11_calibrate.CHAMPION，
# 抄同一份組裝路徑，不自己手鍵數值）
# ==================================================================

def _v11_config_dict():
    """v1.1 全域檔的 config dict（照 v11_calibrate._d3_config 的欄位，剝除
    v11_calibrate 額外的 net_start/net_mode 參數化，直接寫死共同約定的值：
    安全網起點15、遞增、基值10、步幅5——不改變 v11_calibrate 本身，只在本檔
    重新表達同一份數值，因為 v11_calibrate._d3_config 回傳的是 3-tuple、
    不直接是 GameConfig，這裡對齊 make_v1_config 需要的 dict 介面）。
    """
    import v11_calibrate as VC
    cfg = dict(VC.CHAMPION)
    return {
        'hp': cfg['hp_global'],
        '閃避帶': cfg['閃避帶'], '護盾帶': cfg['護盾帶'], '力場帶': cfg['力場帶'],
        'dodge_mode': cfg['dodge_mode'],
        '領航員自攻': cfg['領航員自攻'],
        '迴復裝置': ('回', cfg['迴復量'], '限2'),
        '安全網起點': cfg['安全網起點'],
        '安全網模式': cfg['安全網模式'],
        '先手補償': cfg['先手補償'],
    }, cfg['安全網基值'], cfg['安全網步幅']


def _build_v11_dir3(seed, actions_per_turn, same_category_limit,
                    def_a='護盾', def_b='護盾'):
    """組出 (engine, GameConfig, setup)：v1.1 全域檔 + A1 新旋鈕。"""
    import search_v1 as SV1
    import v11_calibrate as VC
    from chips import shared_chip_db
    config_dict, net_base, net_step = _v11_config_dict()
    gcfg = SV1.make_v1_config(config_dict, seed, oneply_samples=50,
                              expect_samples=50,
                              actions_per_turn=actions_per_turn,
                              same_category_limit=same_category_limit)
    gcfg.extra['安全網基值'] = net_base
    gcfg.extra['安全網步幅'] = net_step
    setup = SV1.make_v1_setup_with_draw(config_dict, def_a, def_b)
    eng = VC.V11Dir3Engine(shared_chip_db())
    return eng, gcfg, setup


def run_cell(direction, actions_per_turn, same_category_limit, n_games,
            seed0, samples=6, resample_k=40, max_decisions=15,
            verbose=True):
    """跑一格（行動數×同類限制組合），回傳可推算度＋副指標的彙總 dict。

    引擎與檔位：v1.1 全域檔（v11_calibrate.CHAMPION 同一份組裝路徑，方向三
    底座，護盾×護盾對壘，共同約定「檔位不另指定時一律 v1.1 全域檔」）。
    direction 參數保留供介面一致性檢查（本實驗固定＝3，dir3 底座，規格
    A1 一節「不改引擎，dir3 底座」）。

    n_games 局按規格切四配對逐局輪替：greedy對turtle（先手greedy/後手turtle
    各半）＋greedy鏡像（各半）——4 種配對逐局輪替，各佔 1/4。
    """
    assert direction == 3, 'A1 規格固定 dir3 底座'
    pairings = [('greedy_damage', 'turtle'), ('turtle', 'greedy_damage'),
               ('greedy_damage', 'greedy_damage'), ('greedy_damage', 'greedy_damage')]
    # 對應每個輪替槽的 first_mover：greedy-turtle 槽固定 0(greedy)先手、
    # turtle-greedy 槽固定 0(turtle)先手——如此四槽跑完 greedy/turtle 兩策略
    # 在先手/後手都各出現過，湊「各半」的先後手平衡（鏡像局無先後手意義，
    # 但仍指定 first_mover 交替以維持 seed 展開的一致性、不影響鏡像局本身
    # 對稱性）。
    first_movers = [0, 0, 0, 1]

    all_consistency = []
    all_n_hand = []
    game_summaries = []
    t0 = __import__('time').time()

    for g in range(n_games):
        slot = g % len(pairings)
        pair = pairings[slot]
        fm = first_movers[slot]
        eng, gcfg, setup = _build_v11_dir3(seed0 + g, actions_per_turn,
                                           same_category_limit)
        collect, summary = _play_and_sample_a1(
            eng, gcfg, setup, pair, samples, resample_k, max_decisions,
            first_mover=fm)
        all_consistency.extend(collect['consistency'])
        all_n_hand.extend(collect['n_hand'])
        game_summaries.append(summary)
        if verbose and ((g + 1) % 40 == 0 or g + 1 == n_games):
            print('  [A1] act=%d cat_limit=%s 局 %d/%d（累積決策點 %d）' % (
                actions_per_turn, same_category_limit, g + 1, n_games,
                len(all_consistency)), file=sys.stderr)

    elapsed = __import__('time').time() - t0

    n_dp = len(all_consistency)
    if n_dp == 0:
        return {
            'actions_per_turn': actions_per_turn,
            'same_category_limit': same_category_limit,
            '決策點數': 0, '可推算度_精確': None, '可推算度_類別': None,
            '耗時秒': round(elapsed, 2), '對局摘要': game_summaries,
        }

    total_k = sum(c['k_effective'] for c in all_consistency)
    total_fine = sum(c['fine_consistent'] for c in all_consistency)
    total_coarse = sum(c['coarse_consistent'] for c in all_consistency)
    fine_consistency_ratio = total_fine / total_k if total_k else float('nan')
    coarse_consistency_ratio = total_coarse / total_k if total_k else float('nan')

    # 逐決策點的一致比例分佈（供 CI 估計；每點自己的 fine_consistent/k_effective）
    per_dp_fine_ratios = [c['fine_consistent'] / c['k_effective']
                          for c in all_consistency if c['k_effective'] > 0]
    per_dp_coarse_ratios = [c['coarse_consistent'] / c['k_effective']
                            for c in all_consistency if c['k_effective'] > 0]

    length_fm = _length_and_firstmover_stats(game_summaries)

    return {
        'actions_per_turn': actions_per_turn,
        'same_category_limit': same_category_limit,
        '對局數': n_games,
        '決策點數': n_dp,
        '重抽副數設定': resample_k,
        '重抽副數平均有效': (total_k / n_dp) if n_dp else float('nan'),
        '一致手牌比例_精確': fine_consistency_ratio,
        '一致手牌比例_類別': coarse_consistency_ratio,
        '可推算度_精確': 1.0 - fine_consistency_ratio,
        '可推算度_類別': 1.0 - coarse_consistency_ratio,
        '逐決策點一致比例_精確_均值': (sum(per_dp_fine_ratios) / len(per_dp_fine_ratios))
                                  if per_dp_fine_ratios else float('nan'),
        '逐決策點一致比例_精確_std': _stdev(per_dp_fine_ratios),
        '手牌數平均': (sum(all_n_hand) / len(all_n_hand)) if all_n_hand else float('nan'),
        '對局長度與先手勝率': length_fm,
        '耗時秒': round(elapsed, 2),
        '對局摘要': game_summaries,
    }


def _stdev(xs):
    if len(xs) < 2:
        return float('nan')
    import statistics
    return statistics.stdev(xs)


def _length_and_firstmover_stats(game_summaries):
    """副指標：對局長度（中位/p90/平均/觸頂率/安全網觸發率）＋先手勝率
    （含 Wilson 95% CI）。直接從 run_cell 收集的 game_summaries 算，沿用
    metrics.py 現成的 _median/_percentile/_wilson（尺③、尺①以外另兩項
    規格要求的副指標：對局長度、先手勝率）。
    """
    import metrics as M
    rounds = [s['rounds'] for s in game_summaries]
    n = len(game_summaries)
    cap_hits = sum(1 for s in game_summaries if s.get('over_reason') == '觸頂平局')
    net_hits = sum(1 for s in game_summaries if s.get('safety_net_triggered'))
    decisive = [s for s in game_summaries if s.get('winner') is not None]
    nd = len(decisive)
    wins = sum(1 for s in decisive if s['winner'] == s['first_mover'])
    p = (wins / nd) if nd else float('nan')
    lo, hi = M._wilson(wins, nd) if nd else (float('nan'), float('nan'))
    return {
        '對局長度_中位': M._median(rounds),
        '對局長度_p90': M._percentile(rounds, 90),
        '對局長度_平均': (sum(rounds) / n) if n else float('nan'),
        '觸頂率': (cap_hits / n) if n else float('nan'),
        '安全網觸發率': (net_hits / n) if n else float('nan'),
        '先手判定局數': nd,
        '先手平局數': n - nd,
        '先手勝': wins,
        '先手勝率': p,
        '先手勝率_CI95下': lo,
        '先手勝率_CI95上': hi,
    }
