# -*- coding: utf-8 -*-
"""DIGO_EXE 指標計算（契約 §五公式）。

全部指標從一批 GameRecord（或其 log）事後計算。純標準庫。

契約 §五清單：
  對局長度：中位、九十百分位、上限觸頂率、安全網觸發率。
  先手勝率（含 95% 信賴區間）。
  移動面被選率＝晶片行動中取移動面的比例；移動行動占比＝移動類行動／全行動。
  追逐死結率＝出現「連續 ≥4 回合雙方皆零 HP 傷害」的對局比例。
  尺①真兩難密度：晶片使用時兩面 oneply 期望價值差 ≤ 較大者兩成的比例。
  尺②口訣化：可見特徵分桶，各桶最頻行動占比加權平均；≥90% 標紅。
  尺③手牌敏感度：抽樣決策點、手牌重抽 10 次後最佳行動翻轉比例。
  相剋健康度：無「被全形狀弱支配」的防禦、無「對全防禦最優」的形狀。
"""
import math
import statistics


# ==================================================================
# 對局長度
# ==================================================================

def game_length_stats(records):
    """回傳 dict：中位、九十百分位、觸頂率、安全網觸發率。"""
    rounds = [r.rounds for r in records]
    n = len(records)
    cap_hits = sum(1 for r in records if r.reason == '觸頂平局')
    net_hits = sum(1 for r in records if r.safety_net_triggered)
    return {
        '對局數': n,
        '回合中位': _median(rounds),
        '回合九十百分位': _percentile(rounds, 90),
        '回合平均': (sum(rounds) / n) if n else float('nan'),
        '觸頂率': (cap_hits / n) if n else float('nan'),
        '安全網觸發率': (net_hits / n) if n else float('nan'),
    }


def _median(xs):
    if not xs:
        return float('nan')
    return statistics.median(xs)


def _percentile(xs, p):
    """線性插值百分位。"""
    if not xs:
        return float('nan')
    s = sorted(xs)
    if len(s) == 1:
        return float(s[0])
    k = (len(s) - 1) * (p / 100.0)
    lo = int(math.floor(k))
    hi = int(math.ceil(k))
    if lo == hi:
        return float(s[lo])
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


# ==================================================================
# 先手勝率（含 95% 信賴區間，Wilson 區間）
# ==================================================================

def first_mover_winrate(records):
    """先手（first_mover）勝率＋Wilson 95% 信賴區間。平局不計入分子分母。"""
    decisive = [r for r in records if r.winner is not None]
    n = len(decisive)
    wins = sum(1 for r in decisive if r.winner == r.first_mover)
    p = (wins / n) if n else float('nan')
    lo, hi = _wilson(wins, n) if n else (float('nan'), float('nan'))
    draws = len(records) - n
    return {
        '判定局數': n,
        '平局數': draws,
        '先手勝': wins,
        '先手勝率': p,
        'CI95下': lo,
        'CI95上': hi,
        'CI95半寬': ((hi - lo) / 2) if n else float('nan'),
    }


def _wilson(wins, n, z=1.96):
    if n == 0:
        return (float('nan'), float('nan'))
    phat = wins / n
    denom = 1 + z * z / n
    centre = (phat + z * z / (2 * n)) / denom
    margin = (z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))) / denom
    return (centre - margin, centre + margin)


# ==================================================================
# 移動面被選率 / 移動行動占比
# ==================================================================

def movement_metrics(records):
    """從 log 事件統計：
      移動面被選率＝晶片行動中取移動面的比例（晶片移動 / 全晶片行動）。
      移動行動占比＝移動類行動（基本移動＋晶片移動面）／全行動。
    """
    chip_move = 0
    chip_ability = 0
    basic_move = 0
    total_actions = 0
    for r in records:
        for e in r.log:
            ev = e.get('event')
            if ev == '晶片移動':
                chip_move += 1
                total_actions += 1
            elif ev == '晶片能力':
                chip_ability += 1
                total_actions += 1
            elif ev == '移動':
                basic_move += 1
                total_actions += 1
            elif ev in ('自攻', '領航員能力攻擊', '領航員能力回復', '換角',
                        'pass'):
                total_actions += 1
    chip_total = chip_move + chip_ability
    move_actions = basic_move + chip_move
    return {
        '晶片行動總數': chip_total,
        '移動面被選率': (chip_move / chip_total) if chip_total else float('nan'),
        '全行動數': total_actions,
        '移動行動占比': (move_actions / total_actions) if total_actions
                    else float('nan'),
    }


# ==================================================================
# 追逐死結率
# ==================================================================

def chase_deadlock_rate(records, window=4):
    """出現「連續 ≥window 回合雙方皆零 HP 傷害」的對局比例。

    由 log 重建每回合雙方是否造成 HP 傷害。傷害事件＝damage>0 的攻擊/陷阱。
    """
    hit = 0
    for r in records:
        if _has_deadlock_window(r, window):
            hit += 1
    n = len(records)
    return {'追逐死結率': (hit / n) if n else float('nan'),
            '死結局數': hit, '對局數': n}


def _has_deadlock_window(rec, window):
    # 建每回合傷害旗標：round_no -> {side: 是否造成 HP 傷害}
    dmg_by_round = {}
    for e in rec.log:
        rd = e.get('round')
        if rd is None:
            continue
        dmg_by_round.setdefault(rd, {0: False, 1: False})
        d = e.get('damage', 0)
        side = e.get('side')
        if d and d > 0 and side is not None:
            dmg_by_round[rd][side] = True
        # 陷阱傷害記在 victim 上，屬「攻擊方無造傷」——不計為造傷者的輸出
    # 連續回合雙方皆零傷
    streak = 0
    for rd in range(1, rec.rounds + 1):
        info = dmg_by_round.get(rd, {0: False, 1: False})
        if not info[0] and not info[1]:
            streak += 1
            if streak >= window:
                return True
        else:
            streak = 0
    return False


# ==================================================================
# 尺①真兩難密度（需決策點兩面 oneply 價值資料）
# ==================================================================

def dilemma_density(decision_points, ratio=0.2):
    """decision_points: [(晶片移動面價值, 晶片能力面價值), …]（同一張晶片兩面）。

    兩面 oneply 期望價值差 ≤ 較大者 ratio 的比例＝真兩難密度。
    價值由 runner 在決策點呼叫 oneply 評估兩面各自最佳 pair 取得。
    """
    if not decision_points:
        return {'真兩難密度': float('nan'), '樣本數': 0}
    close = 0
    for v_move, v_ability in decision_points:
        hi = max(abs(v_move), abs(v_ability))
        if hi == 0:
            close += 1   # 兩面皆 0 → 完全無差＝兩難
            continue
        if abs(v_move - v_ability) <= ratio * hi:
            close += 1
    return {'真兩難密度': close / len(decision_points),
            '樣本數': len(decision_points)}


# ==================================================================
# 尺②口訣化（可見特徵分桶）
# ==================================================================

def playbook_score(labelled_decisions):
    """labelled_decisions: [(bucket_key, action_signature), …]。

    bucket_key＝可見特徵元組（相對位置類、HP 帶、防禦型、列距、能量帶…）。
    各桶最頻行動占比，依桶樣本數加權平均。≥0.90 標紅（口訣化）。
    """
    from collections import defaultdict, Counter
    buckets = defaultdict(Counter)
    for key, act in labelled_decisions:
        buckets[key][act] += 1
    total = 0
    weighted = 0.0
    for key, counter in buckets.items():
        m = sum(counter.values())
        top = max(counter.values())
        weighted += top          # 加權＝該桶最頻行動的次數
        total += m
    score = (weighted / total) if total else float('nan')
    return {'口訣化分數': score, '桶數': len(buckets), '決策點數': total,
            '標紅': (score >= 0.90) if total else None}


# ==================================================================
# 尺③手牌敏感度
# ==================================================================

def hand_sensitivity(flip_flags):
    """flip_flags: [bool,…]——每個抽樣決策點，手牌重抽 10 次後最佳行動是否翻轉。

    回傳翻轉比例（越高＝手牌越有意義、越不口訣化）。
    """
    if not flip_flags:
        return {'手牌敏感度': float('nan'), '樣本數': 0}
    flips = sum(1 for f in flip_flags if f)
    return {'手牌敏感度': flips / len(flip_flags), '樣本數': len(flip_flags)}


# ==================================================================
# 相剋健康度（隔離結算的有效傷害期望矩陣）
# ==================================================================

def matchup_health(matrix):
    """matrix: dict[(攻擊形狀名, 防禦名)] -> 期望有效傷害。

    檢查：
      無「被全形狀弱支配」的防禦：某防禦對每個攻擊形狀都不是最能扛的（存在
        另一防禦對每個形狀都 ≤ 它且至少一個嚴格 <）＝被弱支配。
      無「對全防禦最優」的形狀：某形狀對每個防禦都嚴格優於其他所有形狀。
    回傳被支配防禦清單、全能形狀清單、以及健康布林。
    """
    shapes = sorted({s for (s, d) in matrix})
    defs = sorted({d for (s, d) in matrix})

    # 被全形狀弱支配的防禦：存在另一防禦 d2，對每個形狀 dmg[s,d2] <= dmg[s,d]，
    # 且至少一個嚴格 <。（傷害越低＝防禦越好；被支配＝有更好的防禦全面壓過它）
    dominated_defenses = []
    for d in defs:
        for d2 in defs:
            if d2 == d:
                continue
            if all(matrix[(s, d2)] <= matrix[(s, d)] for s in shapes) and \
               any(matrix[(s, d2)] < matrix[(s, d)] for s in shapes):
                dominated_defenses.append(d)
                break

    # 對全防禦最優的形狀：某形狀對每個防禦，其傷害都嚴格高於所有其他形狀。
    dominant_shapes = []
    for s in shapes:
        if all(all(matrix[(s, d)] > matrix[(s2, d)]
                   for s2 in shapes if s2 != s)
               for d in defs):
            dominant_shapes.append(s)

    healthy = (len(dominated_defenses) == 0 and len(dominant_shapes) == 0)
    return {
        '被弱支配防禦': dominated_defenses,
        '全能形狀': dominant_shapes,
        '相剋健康': healthy,
    }


# ==================================================================
# 換角相關（方向一專屬指標支援）
# ==================================================================

def change_navi_stats(records):
    """換角頻率分佈：每局換角次數（主動＋強制）。"""
    per_game = []
    forced = 0
    active = 0
    for r in records:
        c = 0
        for e in r.log:
            if e.get('event') == '換角':
                c += 1
                active += 1
            elif e.get('event') == '強制換入':
                c += 1
                forced += 1
        per_game.append(c)
    n = len(records)
    return {
        '每局換角中位': _median(per_game) if per_game else float('nan'),
        '每局換角平均': (sum(per_game) / n) if n else float('nan'),
        '主動換角總數': active,
        '強制換入總數': forced,
    }


def resource_pickup_stats(records):
    """方向二：拾取次數、陷阱觸發次數。"""
    picks = 0
    trap_triggers = 0
    overload_triggers = 0
    for r in records:
        for e in r.log:
            ev = e.get('event')
            if ev == '拾取資源':
                picks += 1
            elif ev == '陷阱觸發':
                trap_triggers += 1
            elif ev == '力場恢復':
                overload_triggers += 1
    n = len(records)
    return {
        '每局拾取平均': (picks / n) if n else float('nan'),
        '陷阱觸發總數': trap_triggers,
        '過載窗解除總數': overload_triggers,
    }


# ==================================================================
# B6 metrics v2：優勢軌跡・翻盤率・張力三量・安全網決定勝負率
# ------------------------------------------------------------------
# 全部從 GameRecord.hp_by_round（core.py 最小掛點：逐回合雙方隊伍總 HP
# 快照，round 0＝開局）與既有 log 事件事後計算，不涉結算邏輯。
# ==================================================================

_COMBAT_DAMAGE_EVENTS = ('自攻', '晶片能力', '領航員能力攻擊')


def advantage_series(rec):
    """單局優勢軌跡 adv(t)，t=0..對局回合數。

    adv(t) = (甲方HP總和(t) − 乙方HP總和(t)) ÷ (雙方初始HP總和 ÷ 2)
    甲＝side 0、乙＝side 1；方向一為三名合計（hp_by_round 已含後備）。
    分母用 round 0（開局）快照，不受戰局影響、對三方向皆通用。

    回傳 [(round_no, adv), …]；初始 HP 總和為 0（不應發生）時回傳空list。
    """
    if not rec.hp_by_round:
        return []
    r0, hp0 = rec.hp_by_round[0]
    denom = (hp0[0] + hp0[1]) / 2.0
    if denom <= 0:
        return []
    out = []
    for rd, hp in rec.hp_by_round:
        adv = (hp[0] - hp[1]) / denom
        out.append((rd, adv))
    return out


def _winner_perspective_adv(rec):
    """回傳勝者視角的 adv 序列（勝者為甲方時原樣、為乙方時取負號）。
    平局回傳 None（呼叫方自行排除）。"""
    if rec.winner is None:
        return None
    series = advantage_series(rec)
    if rec.winner == 0:
        return series
    return [(rd, -adv) for rd, adv in series]


def comeback_rate(records, threshold=-0.20):
    """翻盤率：勝者在 t≥2 的任何回合曾（勝者視角）adv ≤ −threshold 的
    對局比例。平局不計入分母。"""
    decisive = [r for r in records if r.winner is not None]
    n = len(decisive)
    if n == 0:
        return {'翻盤率': float('nan'), '判定局數': 0, '翻盤局數': 0}
    hit = 0
    for r in decisive:
        series = _winner_perspective_adv(r)
        if series is None:
            continue
        if any(adv <= threshold for rd, adv in series if rd >= 2):
            hit += 1
    return {'翻盤率': hit / n, '判定局數': n, '翻盤局數': hit}


def tension_metrics(records, zero_band=0.02):
    """張力三量：
      (a) 波動度＝|adv(t)−adv(t−1)| 的全局平均（跨全部對局、全部回合對）。
      (b) 領先易手次數＝adv 跨零符號變化次數（|adv|<zero_band 視為零帶、
          不計入符號序列——用「最近一個非零帶符號」比較，避免零帶抖動
          灌水易手次數），每局一個計數、回傳全局平均與分布。
      (c) 決勝時點＝最後一次跨零的回合 ÷ 對局總回合；無跨零（單邊碾壓局，
          含平局全程同號或全程零帶）者不計入分母，另外回報涵蓋率。
    """
    all_deltas = []
    swap_counts = []
    decisive_points = []
    n_no_cross = 0
    for r in records:
        series = advantage_series(r)
        if len(series) < 2:
            continue
        # (a) 波動度
        for i in range(1, len(series)):
            all_deltas.append(abs(series[i][1] - series[i - 1][1]))
        # (b)(c) 符號序列（零帶忽略、延續前一個非零帶符號）
        last_sign = 0
        swaps = 0
        last_cross_round = None
        for rd, adv in series:
            if abs(adv) < zero_band:
                continue
            sign = 1 if adv > 0 else -1
            if last_sign != 0 and sign != last_sign:
                swaps += 1
                last_cross_round = rd
            elif last_sign == 0 and rd > series[0][0]:
                # 首次脫離零帶不算「易手」（沒有前一個非零號可比較）
                pass
            last_sign = sign
        swap_counts.append(swaps)
        total_rounds = r.rounds if r.rounds else series[-1][0]
        if last_cross_round is not None and total_rounds:
            decisive_points.append(last_cross_round / float(total_rounds))
        else:
            n_no_cross += 1
    n = len(records)
    return {
        '波動度': (sum(all_deltas) / len(all_deltas)) if all_deltas
                else float('nan'),
        '領先易手次數_平均': (sum(swap_counts) / len(swap_counts))
                        if swap_counts else float('nan'),
        '領先易手次數_中位': _median(swap_counts) if swap_counts
                        else float('nan'),
        '決勝時點_平均': (sum(decisive_points) / len(decisive_points))
                    if decisive_points else float('nan'),
        '決勝時點_中位': _median(decisive_points) if decisive_points
                    else float('nan'),
        '決勝時點涵蓋局數': len(decisive_points),
        '無跨零局數': n_no_cross,
        '對局數': n,
    }


def _combat_dealt_by_round(rec):
    """{round_no: {side: 該側這回合造成的戰鬥HP傷害}}，僅計自攻／晶片能力／
    領航員能力攻擊三類事件（皆帶 side+damage+round，跨三方向通用）。"""
    out = {}
    for e in rec.log:
        if e.get('event') in _COMBAT_DAMAGE_EVENTS and e.get('damage'):
            r = e.get('round')
            s = e.get('side')
            if r is None or s is None:
                continue
            out.setdefault(r, {0: 0, 1: 0})[s] += e['damage']
    return out


def _safety_net_loss_by_side(rec):
    """回傳 {side: 該側全局累積的「安全網淨損失HP」}。

    做法：對每個發生「安全網」事件的回合，該回合雙方 HP 淨損失
    （由 hp_by_round 前後快照差）扣掉當回合對手實際造成的戰鬥傷害
    （_combat_dealt_by_round），餘數歸因安全網。核心引擎的豁免規則是
    「造傷者本回合免安全網」，戰鬥傷害與安全網不會疊加到同一來源，此法
    對稱扣除即可還原各側安全網損失（已對 v1.1 遞增模式與基礎引擎兩種
    log 格式抽驗一致，見報告可信度聲明）。
    """
    hp_map = dict(rec.hp_by_round)
    dealt = _combat_dealt_by_round(rec)
    loss = {0: 0, 1: 0}
    for e in rec.log:
        if e.get('event') != '安全網':
            continue
        r = e.get('round')
        if r is None or (r - 1) not in hp_map or r not in hp_map:
            continue
        prev_hp = hp_map[r - 1]
        cur_hp = hp_map[r]
        d = dealt.get(r, {0: 0, 1: 0})
        for side in (0, 1):
            enemy = 1 - side
            raw_delta = prev_hp[side] - cur_hp[side]
            combat_recv = d.get(enemy, 0)
            net = raw_delta - combat_recv
            if net > 0:
                loss[side] += net
    return loss


def safety_net_decisive_rate(records, loser_share_threshold=0.5):
    """安全網決定勝負率：分子＝對局同時滿足下列任一：
      (a) 致勝一擊來源是安全網傷害——勝負在「安全網」事件觸發後立即判定
          （敗者於同一回合因安全網歸零／check_over 成立）；
      (b) 敗者總失血中安全網佔比 ≥ loser_share_threshold。
    分母＝有勝負的對局（平局不計）。同時回傳舊「安全網觸發率」並列
    （觸發率＝安全網機制本身有無介入，門檻寬鬆；本指標＝安全網是否
    真正主導了勝負，門檻嚴格——兩者刻意並陳避免誤讀）。
    """
    decisive = [r for r in records if r.winner is not None]
    n = len(decisive)
    hit = 0
    for r in decisive:
        loser = 1 - r.winner
        # (a) 致勝一擊來源：敗者是否在「安全網」事件所在回合、且該回合
        #    末尾 HP 已到 0（由 hp_by_round 讀出，不必重算結算細節）。
        net_rounds = {e['round'] for e in r.log if e.get('event') == '安全網'}
        killed_by_net = False
        hp_map = dict(r.hp_by_round)
        for rd in net_rounds:
            hp_after = hp_map.get(rd)
            if hp_after is not None and hp_after[loser] <= 0:
                killed_by_net = True
                break
        if killed_by_net:
            hit += 1
            continue
        # (b) 敗者總失血中安全網佔比
        loss_by_side = _safety_net_loss_by_side(r)
        r0, hp0 = r.hp_by_round[0]
        final = r.hp_by_round[-1][1]
        total_loss = hp0[loser] - final[loser]
        if total_loss > 0:
            share = loss_by_side[loser] / float(total_loss)
            if share >= loser_share_threshold:
                hit += 1
    n_triggered = sum(1 for r in decisive if r.safety_net_triggered)
    return {
        '安全網決定勝負率': (hit / n) if n else float('nan'),
        '安全網觸發率_判定局': (n_triggered / n) if n else float('nan'),
        '判定局數': n,
        '安全網決定局數': hit,
    }
