# -*- coding: utf-8 -*-
"""DIGO_EXE 驗證引擎：共用核心。

內容：幾何、行動經濟、回合迴圈、傷害結算、legal_actions、play。
純標準庫。傷害結算逐字對齊 vault `sim_combat.py` 的 resolve_attack 狀態機。

方向模組（dir1/dir2/dir3）在此檔之上做 overlay，本檔預留掛點：
  - 隊伍與上場位：Unit.team_id / GameState.benches / engine hook change_navi
  - 資源層：GameState.resources / hook_resource_spawn / hook_resource_pickup
  - 陷阱層：GameState.traps / hook_trap_check
這些掛點在共用核心裡是空實作或 None，方向模組覆寫。
"""
import copy
import random


class _SinkList(list):
    """append 全丟掉的 list——沙盤推演不需要記 log，省記憶體與時間。"""
    __slots__ = ()

    def append(self, x):
        pass

    def extend(self, xs):
        pass

# ==================================================================
# 幾何：全域座標 6 列 × 3 排（共用基準 §二）
# ------------------------------------------------------------------
# 列 1–6 由我方後排到敵方後排；我方列 1–3、敵方列 4–6；排 1–3。
# 內部一律用 1-indexed (列 row, 排 col)，與規格文字一致。
# side 0 = 我方（列 1–3，前進方向 +列）；side 1 = 敵方（列 4–6，前進方向 −列）。
# ==================================================================

ROWS = (1, 2, 3, 4, 5, 6)
COLS = (1, 2, 3)
START_POS = {0: (2, 2), 1: (5, 2)}   # 我方 (列2,排2)、敵方 (列5,排2)


def own_rows(side):
    """該方可站的列（不可進入對方半場）。"""
    return (1, 2, 3) if side == 0 else (4, 5, 6)


def advance_dir(side):
    """朝敵方推進時列號的增量。"""
    return +1 if side == 0 else -1


def in_own_half(side, row):
    return row in own_rows(side)


def in_enemy_half(side, row):
    return row in own_rows(1 - side)


def on_board(row, col):
    return row in ROWS and col in COLS


def row_dist(a_pos, b_pos):
    """列距＝列差絕對值（共用基準 §二）。"""
    return abs(a_pos[0] - b_pos[0])


def col_dist(a_pos, b_pos):
    return abs(a_pos[1] - b_pos[1])


def manhattan(a_pos, b_pos):
    return row_dist(a_pos, b_pos) + col_dist(a_pos, b_pos)


def adjacent_cells(row, col):
    """上下左右鄰格（在盤面上者）。"""
    out = []
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        r, c = row + dr, col + dc
        if on_board(r, c):
            out.append((r, c))
    return out


# ==================================================================
# 範圍詞彙表 v0（共用基準 §二 3）
# 給定 攻擊者位置、side、範圍規格 spec、以及敵方單位位置集合，
# 回傳被命中的敵方位置清單。spec 是 (kind, *params)。
# 範圍攻擊對每個被命中的敵方單位各自結算「單次傷害 × 攻擊次數」。
# ------------------------------------------------------------------
# target 參數（策略選定的瞄準點）意義隨 kind 而定：
#   直射N / 貫穿 / 近斬 / 鎖列：不需 target（None）。
#   十字 / 全域點：target=(row,col) 敵方半場一格。
#   鎖排：target=col（指定一排 1..3）。
# enemy_positions: dict unit_index -> (row,col)，只含敵方存活上場單位。
# ==================================================================

def cells_hit(att_pos, att_side, spec, target, enemy_positions):
    """回傳被此攻擊命中的 (敵方 unit_index) 清單。"""
    kind = spec[0]
    a_row, a_col = att_pos
    enemy_side = 1 - att_side
    hit_idxs = []

    if kind == '直射':
        n = spec[1]
        # 同排、列距 ≤ N 的最近敵人（單一目標）
        cand = []
        for idx, (r, c) in enemy_positions.items():
            if c == a_col and abs(r - a_row) <= n:
                cand.append((abs(r - a_row), idx))
        if cand:
            cand.sort()
            hit_idxs = [cand[0][1]]

    elif kind == '貫穿':
        # 攻擊者同排的全部敵方格（不限距離）
        for idx, (r, c) in enemy_positions.items():
            if c == a_col:
                hit_idxs.append(idx)

    elif kind == '十字':
        # 指定敵方半場一格，命中該格＋上下左右鄰格（限敵方半場）
        tr, tc = target
        area = {(tr, tc)}
        for cell in adjacent_cells(tr, tc):
            area.add(cell)
        # 限敵方半場
        area = {(r, c) for (r, c) in area if in_own_half(enemy_side, r)}
        for idx, (r, c) in enemy_positions.items():
            if (r, c) in area:
                hit_idxs.append(idx)

    elif kind == '鎖排':
        # 指定一排，命中敵方半場該排整排 3 格
        tcol = target
        for idx, (r, c) in enemy_positions.items():
            if c == tcol and in_own_half(enemy_side, r):
                hit_idxs.append(idx)

    elif kind == '鎖列':
        # 命中敵方最前列（靠攻擊者側）整列 3 格
        front_row = 4 if att_side == 0 else 3
        for idx, (r, c) in enemy_positions.items():
            if r == front_row:
                hit_idxs.append(idx)

    elif kind == '近斬':
        # 需敵人在相鄰列且同排；「寬斬」變體同時命中其上下鄰排
        wide = (len(spec) > 1 and spec[1] == '寬')
        adv = advance_dir(att_side)
        target_row = a_row + adv    # 相鄰列（朝敵方）
        for idx, (r, c) in enemy_positions.items():
            if r != target_row:
                continue
            if c == a_col:
                hit_idxs.append(idx)
            elif wide and abs(c - a_col) == 1:
                hit_idxs.append(idx)

    elif kind == '全域點':
        # 任選敵方一格
        tr, tc = target
        for idx, (r, c) in enemy_positions.items():
            if (r, c) == (tr, tc):
                hit_idxs.append(idx)

    else:
        raise ValueError('未知範圍：%r' % (kind,))

    return hit_idxs


def range_can_reach(att_pos, att_side, spec, target, enemy_positions):
    """此攻擊在目前盤面是否命中至少一個敵方單位。"""
    return len(cells_hit(att_pos, att_side, spec, target, enemy_positions)) > 0


def enumerate_targets(att_pos, att_side, spec, enemy_positions):
    """枚舉此範圍規格所有「值得瞄準」的 target 值（只列會命中的）。

    直射/貫穿/近斬/鎖列：target=None（自動決定命中）。
    十字/全域點/鎖排：列出所有能命中至少一個敵方單位的 target。
    回傳 target 清單（可能為空＝目前打不到）。
    """
    kind = spec[0]
    enemy_side = 1 - att_side
    if kind in ('直射', '貫穿', '近斬', '鎖列'):
        if range_can_reach(att_pos, att_side, spec, None, enemy_positions):
            return [None]
        return []
    if kind == '鎖排':
        out = []
        for tcol in COLS:
            if range_can_reach(att_pos, att_side, spec, tcol, enemy_positions):
                out.append(tcol)
        return out
    if kind in ('十字', '全域點'):
        out = []
        # 候選瞄準格＝敵方半場所有格
        for r in own_rows(enemy_side):
            for c in COLS:
                if range_can_reach(att_pos, att_side, spec, (r, c), enemy_positions):
                    out.append((r, c))
        return out
    raise ValueError('未知範圍：%r' % (kind,))


# ==================================================================
# 傷害結算（共用基準 §一、契約 §一）——逐字對齊 sim_combat.resolve_attack
# ------------------------------------------------------------------
# 順序：閃避前置（每點 1/3 機率抵銷一整擊，二項分佈）
#      → 每擊過力場（單次傷害減力場值、最低 0）
#      → 護盾狀態機（盾>0 吸收；歸 0 後下一擊全額穿透、該擊之後回滿）
# 變體：
#   dodge_mode='超額削減'：確定性——單次傷害 ≤ 閃避值則全額；超過部分砍半
#            有效＝閃避值 + ⌈(單次傷害−閃避值)/2⌉。零亂數、逐擊套用。
#   field_overload='開'：單次傷害 ≥ 2×力場值的擊命中後，力場失效至受擊方下一回合結束。
# ==================================================================

EVADE_P = 1.0 / 3.0    # 每點閃避的觸發機率（與 sim_combat 一致）


def resolve_attack(defender, dmg, hits, rng, dodge_mode='機率制',
                   field_overload='關'):
    """對單一 defender 結算「單次傷害 dmg × 攻擊次數 hits」，回傳實際 HP 損失。

    會就地改 defender.hp / defender.shield_cur / defender.field_disabled。
    defender 需具備欄位：hp, evasion, field(力場值), shield_max, shield_cur,
    field_disabled(bool)。
    """
    # ---- 閃避前置 ----
    if dodge_mode == '機率制':
        # 每點 1/3 機率抵銷一整擊（二項分佈），逐擊固定機率制
        negated = sum(1 for _ in range(defender.evasion)
                      if rng.random() < EVADE_P)
        eff_hits = max(0, hits - negated)
        per_hit_evasion = 0     # 機率制不對單擊再做削減
    else:  # 超額削減（確定性閃避）：不減攻擊次數，改逐擊削傷害
        eff_hits = hits
        per_hit_evasion = defender.evasion

    field = 0 if getattr(defender, 'field_disabled', False) else defender.field
    loss = 0
    for _ in range(eff_hits):
        d = dmg
        # 超額削減（確定性閃避）：單次傷害 ≤ 閃避值則全額；超過部分砍半。
        # 有效 = 閃避值 + ⌈(單次傷害−閃避值)/2⌉。剋大擊、小擊照穿、不可墊刀。
        if per_hit_evasion > 0 and d > per_hit_evasion:
            over = d - per_hit_evasion
            d = per_hit_evasion + (over + 1) // 2   # 閃避值 + ⌈over/2⌉
        # ---- 每擊過力場（固定減、最低 0）----
        # 力場過載窗判定用「過力場前」的單次傷害（原始或閃避後）
        pre_field_d = d
        d = max(0, d - field)
        if field > 0 and field_overload == '開' and pre_field_d >= 2 * field:
            # 這一擊觸發過載：力場失效至受擊方下一回合結束
            defender.field_disabled = True
            field = 0   # 本次攻擊後續擊也失效
        if d == 0:
            continue
        # ---- 護盾狀態機（回充窗）----
        if defender.shield_cur == 0:
            loss += d
            defender.shield_cur = defender.shield_max   # 暴露擊之後回滿
        else:
            absorbed = min(d, defender.shield_cur)
            defender.shield_cur -= absorbed
            loss += d - absorbed                        # 打穿的溢傷
    defender.hp -= loss
    return loss


# ==================================================================
# 資料結構
# ==================================================================

class Unit(object):
    """一名領航員。含 HP、三防禦、位置、自身攻擊、能力。

    防禦欄位命名對齊傷害結算：evasion(閃避)/field(力場)/shield_max/shield_cur。
    team_id / on_bench 供方向一換角；能力欄位方向三留空。
    """
    __slots__ = ('name', 'hp', 'hp_max', 'evasion', 'field', 'shield_max',
                 'shield_cur', 'field_disabled', 'pos', 'navi_attack',
                 'ability', 'team_id', 'on_bench', 'alive')

    def __init__(self, name, hp, evasion=0, field=0, shield=0, pos=(2, 2),
                 navi_attack=('直射', 2, 10, 1), ability=None, team_id=0):
        # navi_attack 格式：(range_kind, range_param, 單次傷害, 攻擊次數)
        #   例：('直射', 2, 10, 1) = 10×1 直射2
        # ability：None 或 dict{cost, dmg, hits, range, heal, shield_refill}
        self.name = name
        self.hp = hp
        self.hp_max = hp
        self.evasion = evasion
        self.field = field
        self.shield_max = shield
        self.shield_cur = shield
        self.field_disabled = False
        self.pos = pos
        self.navi_attack = navi_attack
        self.ability = ability
        self.team_id = team_id
        self.on_bench = False
        self.alive = True

    def clone(self):
        u = Unit.__new__(Unit)
        for s in Unit.__slots__:
            setattr(u, s, getattr(self, s))
        return u

    def defense_summary(self):
        return (self.evasion, self.field, self.shield_max)


class Action(object):
    """一個行動。kind ∈ {移動, 晶片, 領航員, pass}。

    移動：dst=(row,col)
    晶片：chip_id, face ∈ {移動,能力}, target（能力面瞄準點或移動面目的地）
    領航員：subkind ∈ {攻擊,能力,換角}, target
    pass：無參數
    """
    __slots__ = ('kind', 'dst', 'chip_id', 'face', 'target', 'subkind')

    def __init__(self, kind, dst=None, chip_id=None, face=None, target=None,
                 subkind=None):
        self.kind = kind
        self.dst = dst
        self.chip_id = chip_id
        self.face = face
        self.target = target
        self.subkind = subkind

    # 行動經濟的「類別」：移動 / 晶片 / 領航員（同類一回合至多 1 次）
    def category(self):
        if self.kind == 'pass':
            return 'pass'
        return self.kind

    def __repr__(self):
        return 'Action(%s)' % ','.join(
            '%s=%r' % (s, getattr(self, s)) for s in Action.__slots__
            if getattr(self, s) is not None)


class GameConfig(object):
    __slots__ = ('direction', 'hp', 'first_turn_comp', 'dodge_mode',
                 'field_overload', 'safety_net_turn', 'max_turns', 'seed',
                 'oneply_samples', 'expect_samples', 'hand_limit', 'draw_per_turn',
                 'starting_hand', 'extra')

    def __init__(self, direction=3, hp=150, first_turn_comp='一行動',
                 dodge_mode='機率制', field_overload='關', safety_net_turn=25,
                 max_turns=60, seed=0, oneply_samples=200, expect_samples=200,
                 hand_limit=6, draw_per_turn=1, starting_hand=4, extra=None):
        self.direction = direction
        self.hp = hp
        self.first_turn_comp = first_turn_comp   # 無 / 一行動 / 傷害上限20
        self.dodge_mode = dodge_mode             # 機率制 / 超額削減
        self.field_overload = field_overload     # 關 / 開
        self.safety_net_turn = safety_net_turn
        self.max_turns = max_turns
        self.seed = seed
        self.oneply_samples = oneply_samples
        self.expect_samples = expect_samples
        self.hand_limit = hand_limit
        self.draw_per_turn = draw_per_turn
        self.starting_hand = starting_hand
        self.extra = extra or {}     # 方向專屬旗標（換角模式、資源制開關…）


class GameState(object):
    """完整賽局狀態。全部可 deepcopy 供 oneply 模擬。

    units：[side0 上場 Unit, side1 上場 Unit]（1對1）；方向一多名走 benches。
    benches：{side: [後備 Unit,…]}（方向一用；其餘空）。
    hands/decks/discards：{side: [chip_id,…]}
    resources：{side: 顆數}（方向二用）
    resource_cells：場上能量球位置 set of (row,col)（方向二用）
    traps：[{side, pos, dmg, hits, revealed}]（方向二用）
    energy：{side: 能量}（方向一用）
    """
    __slots__ = ('config', 'turn', 'round_no', 'side_to_move', 'units',
                 'benches', 'hands', 'decks', 'discards', 'resources',
                 'resource_cells', 'traps', 'energy', 'log', 'first_mover',
                 'actions_this_turn', 'damage_this_turn', 'winner', 'over',
                 'over_reason', 'engine')

    def __init__(self):
        self.config = None
        self.turn = 0            # 已完成的半回合數（每方一手 = 一 turn）
        self.round_no = 1        # 完整回合序號（雙方各一手 = 一回合）
        self.side_to_move = 0
        self.units = [None, None]
        self.benches = {0: [], 1: []}
        self.hands = {0: [], 1: []}
        self.decks = {0: [], 1: []}
        self.discards = {0: [], 1: []}
        self.resources = {0: 0, 1: 0}
        self.resource_cells = set()
        self.traps = []
        self.energy = {0: 0, 1: 0}
        self.log = []
        self.first_mover = 0
        self.actions_this_turn = []
        self.damage_this_turn = {0: 0, 1: 0}
        self.winner = None
        self.over = False
        self.over_reason = None
        self.engine = None       # 綁定的 Engine（方向 overlay）

    def active_unit(self, side):
        return self.units[side]

    def sim_clone(self):
        """快速沙盤複本（策略推演用）。共享 config/engine（唯讀），深拷會變的部分。

        log 換成拋棄式 list（推演不需保留事件）。比 deepcopy 快一個數量級。
        """
        dup = GameState.__new__(GameState)
        dup.config = self.config          # 唯讀共享
        dup.engine = self.engine          # 唯讀共享
        dup.turn = self.turn
        dup.round_no = self.round_no
        dup.side_to_move = self.side_to_move
        dup.first_mover = self.first_mover
        dup.units = [u.clone() if u is not None else None for u in self.units]
        dup.benches = {s: [b.clone() for b in self.benches[s]] for s in (0, 1)}
        dup.hands = {s: self.hands[s][:] for s in (0, 1)}
        dup.decks = {s: self.decks[s][:] for s in (0, 1)}
        dup.discards = {s: self.discards[s][:] for s in (0, 1)}
        dup.resources = dict(self.resources)
        dup.resource_cells = set(self.resource_cells)
        dup.traps = [dict(t) for t in self.traps]
        dup.energy = dict(self.energy)
        dup.log = _SinkList()             # 拋棄式：append 全丟掉
        dup.actions_this_turn = []
        dup.damage_this_turn = dict(self.damage_this_turn)
        dup.winner = self.winner
        dup.over = self.over
        dup.over_reason = self.over_reason
        return dup

    def enemy_positions(self, att_side):
        """敵方存活上場單位 index -> pos。1對1 時 index 恒為對方 side。

        回傳 dict：key 用 side（1對1）；方向一 3對3 也是一次只上場一名 →
        仍是單一 key。統一介面。
        """
        enemy = 1 - att_side
        u = self.units[enemy]
        if u is not None and u.alive:
            return {enemy: u.pos}
        return {}

    def total_cards(self, side):
        return len(self.hands[side]) + len(self.decks[side]) + \
            len(self.discards[side])


class GameRecord(object):
    """一局的結果與逐事件紀錄，供指標事後計算。"""
    __slots__ = ('config', 'winner', 'reason', 'rounds', 'turns', 'log',
                 'safety_net_triggered', 'first_mover', 'final_hp',
                 'hp_by_round')

    def __init__(self):
        self.config = None
        self.winner = None          # 0 / 1 / None(平局)
        self.reason = None
        self.rounds = 0
        self.turns = 0
        self.log = []
        self.safety_net_triggered = False
        self.first_mover = 0
        self.final_hp = {0: 0, 1: 0}
        # B6 metrics v2 最小掛點：逐回合雙方隊伍總 HP 快照，
        # [(round_no, {0: hp總和, 1: hp總和}), …]。不影響任何結算邏輯，
        # 純事後讀取用（見 metrics.py advantage_series）。
        self.hp_by_round = []


# ==================================================================
# 引擎：合法性、行動施行、回合迴圈、play
# ------------------------------------------------------------------
# Engine 是共用核心；方向模組繼承並覆寫 hook_*（資源、陷阱、換角、抽牌…）。
# ==================================================================

class Engine(object):
    def __init__(self, chip_db):
        # chip_db: dict chip_id -> Chip（chips.py 提供）
        self.chips = chip_db

    # ---------------- 初始化 ----------------
    def new_game(self, config, setup):
        """setup 由方向模組提供：建 units/benches/decks 等。回傳 GameState。

        setup(engine, state, config) 就地填 state。共用核心給預設 1對1 單防禦。
        """
        st = GameState()
        st.config = config
        st.engine = self
        st.first_mover = 0
        st.side_to_move = 0
        setup(self, st, config)
        # 記錄開場
        st.log.append({'event': '開局', 'round': 1})
        return st

    # ---------------- 移動 ----------------
    def basic_move_dsts(self, st, side):
        """基本移動：上下左右 1 格，限己方半場、在盤面上。"""
        u = st.units[side]
        r, c = u.pos
        out = []
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if on_board(nr, nc) and in_own_half(side, nr) and \
                    not self._occupied(st, side, (nr, nc)):
                out.append((nr, nc))
        return out

    def _occupied(self, st, side, pos):
        """該格是否被己方其他上場單位佔據（1對1 恒 False；預留 3對3）。"""
        # 1對1 只有一名上場，永不自撞。方向一同樣一次一名上場。
        return False

    def chip_move_dsts(self, st, side, chip):
        """晶片移動面的目的地清單（依 move_face 規格；限己方半場、盤面）。"""
        u = st.units[side]
        r, c = u.pos
        adv = advance_dir(side)
        mv = chip.move_face   # (mode, *params)
        mode = mv[0]
        out = []

        def ok(nr, nc):
            return (on_board(nr, nc) and in_own_half(side, nr)
                    and not self._occupied(st, side, (nr, nc))
                    and (nr, nc) != (r, c))

        if mode == '前後直移':
            dist = mv[1]
            for nr in (r + adv * dist, r - adv * dist):
                if ok(nr, c):
                    out.append((nr, c))
        elif mode == '前移':
            dist = mv[1]
            nr = r + adv * dist
            if ok(nr, c):
                out.append((nr, c))
        elif mode == '後移':
            dist = mv[1]
            nr = r - adv * dist
            if ok(nr, c):
                out.append((nr, c))
        elif mode == '上下移':
            dist = mv[1]
            for nr in (r + dist, r - dist):
                if ok(nr, c):
                    out.append((nr, c))
        elif mode == '左右移':
            dist = mv[1]
            for nc in (c + dist, c - dist):
                if ok(r, nc):
                    out.append((r, nc))
        elif mode == '前後移':
            dist = mv[1]
            for nr in (r + adv * dist, r - adv * dist):
                if ok(nr, c):
                    out.append((nr, c))
        elif mode == '斜移':
            dist = mv[1]
            for dr in (dist, -dist):
                for dc in (dist, -dist):
                    if ok(r + dr, c + dc):
                        out.append((r + dr, c + dc))
        elif mode == '任意方向移':
            dist = mv[1]
            for dr in range(-dist, dist + 1):
                for dc in range(-dist, dist + 1):
                    if (dr, dc) == (0, 0):
                        continue
                    # 距離＝切比雪夫（含斜）1 格；規格「任意方向移 1（含斜）」
                    if max(abs(dr), abs(dc)) != dist:
                        continue
                    if ok(r + dr, c + dc):
                        out.append((r + dr, c + dc))
        elif mode == '退至本排最後列':
            # 退到本排（同排）己方最後列（離敵最遠）
            back_row = 1 if side == 0 else 6
            if ok(back_row, c):
                out.append((back_row, c))
        elif mode == '跳至同排任意己方格':
            for nr in own_rows(side):
                if ok(nr, c):
                    out.append((nr, c))
        elif mode == '跳至己方半場任意格':
            for nr in own_rows(side):
                for nc in COLS:
                    if ok(nr, nc):
                        out.append((nr, nc))
        else:
            raise ValueError('未知移動面：%r' % (mode,))
        return out

    # ---------------- 合法行動枚舉（唯一入口）----------------
    def legal_actions(self, st, side, used_categories=frozenset()):
        """回傳此 side 目前所有單一合法 Action（尚未考慮組合成兩行動）。

        used_categories：本回合已用掉的類別集合（同類至多 1 次）。
        策略不得自算合法性，一律經此。
        """
        acts = [Action('pass')]
        u = st.units[side]
        if u is None or not u.alive:
            return acts

        # ---- 移動類 ----
        if '移動' not in used_categories:
            for dst in self.basic_move_dsts(st, side):
                acts.append(Action('移動', dst=dst))

        # ---- 晶片類（移動面 + 能力面）----
        if '晶片' not in used_categories:
            for cid in set(st.hands[side]):
                chip = self.chips[cid]
                # 移動面
                for dst in self.chip_move_dsts(st, side, chip):
                    acts.append(Action('晶片', chip_id=cid, face='移動', dst=dst))
                # 能力面
                acts.extend(self._chip_ability_actions(st, side, cid, chip))

        # ---- 領航員類（自攻 / 能力 / 換角）----
        if '領航員' not in used_categories:
            acts.extend(self._navi_actions(st, side))

        return acts

    def _chip_ability_actions(self, st, side, cid, chip):
        """晶片能力面可用的 Action（含攻擊瞄準枚舉、回復、護盾類）。"""
        out = []
        ab = chip.ability_face   # dict
        u = st.units[side]
        kind = ab['type']
        if kind == 'attack':
            spec = ab['range']
            targets = enumerate_targets(u.pos, side, spec,
                                        st.enemy_positions(side))
            for tg in targets:
                out.append(Action('晶片', chip_id=cid, face='能力', target=tg))
        elif kind in ('heal', 'shield_reset'):
            # 無瞄準；隨時可用（回復/護盾重整）
            out.append(Action('晶片', chip_id=cid, face='能力', target=None))
        else:
            raise ValueError('未知晶片能力：%r' % (kind,))
        return out

    def _navi_actions(self, st, side):
        """領航員自身攻擊（＋能力＋換角，後兩者由方向 hook 補）。"""
        out = []
        u = st.units[side]
        # 自身攻擊：navi_attack = (range_kind, range_param, 單傷, 次數)
        rk, rp, dmg, hits = u.navi_attack
        spec = (rk, rp) if rp is not None else (rk,)
        targets = enumerate_targets(u.pos, side, spec, st.enemy_positions(side))
        for tg in targets:
            out.append(Action('領航員', subkind='攻擊', target=tg))
        # 領航員能力（方向一：耗能量的招）
        out.extend(self.hook_navi_ability_actions(st, side))
        # 換角（方向一：佔行動的主動換角）
        out.extend(self.hook_change_navi_actions(st, side))
        return out

    # ---- 方向掛點（共用核心空實作）----
    def hook_navi_ability_actions(self, st, side):
        return []

    def hook_change_navi_actions(self, st, side):
        return []

    def hook_resource_spawn(self, st):
        pass

    def hook_resource_pickup(self, st, side, unit):
        pass

    def hook_trap_check(self, st, side, unit):
        """單位移動到新格後檢查是否踩敵方陷阱。回傳造成的傷害。"""
        return 0

    def hook_start_turn(self, st, side):
        """回合開始 hook（抽牌前）：能量 +1、資源生成等。"""
        pass

    def hook_end_turn(self, st, side):
        """回合結束 hook：力場過載窗到期解除等。"""
        pass

    # ---------------- 合法「兩行動組合」枚舉 ----------------
    def legal_action_pairs(self, st, side, first_comp_limit=None):
        """回傳合法的行動組合清單 [(a1, a2), …]。

        規則：一回合 2 個行動、同類至多 1 次（含 pass）。
        first_comp_limit='一行動' → 只給單行動組（第二個強制 pass）。
        傷害上限與能量等由施行時處理，這裡只管合法組合。
        """
        pairs = []
        first_acts = self.legal_actions(st, side)
        for a1 in first_acts:
            cats1 = set() if a1.category() == 'pass' else {a1.category()}
            if first_comp_limit == '一行動':
                pairs.append((a1, Action('pass')))
                continue
            second_acts = self.legal_actions(st, side, used_categories=cats1)
            for a2 in second_acts:
                # 避免重複列 (pass, X) 與 (X, pass)：pass 一律排第二
                if a1.category() == 'pass' and a2.category() != 'pass':
                    continue
                pairs.append((a1, a2))
        return pairs

    # ---------------- 施行單一行動 ----------------
    def apply_action(self, st, side, action, rng):
        """就地施行 action。回傳造成的 HP 傷害（供豁免判定）。"""
        u = st.units[side]
        dealt = 0
        if action.kind == 'pass':
            st.log.append({'event': 'pass', 'side': side, 'round': st.round_no})
            return 0

        if action.kind == '移動':
            u.pos = action.dst
            dealt += self.hook_trap_check(st, side, u)
            self.hook_resource_pickup(st, side, u)
            st.log.append({'event': '移動', 'side': side, 'to': action.dst,
                           'round': st.round_no})
            return dealt

        if action.kind == '晶片':
            chip = self.chips[action.chip_id]
            # 從手牌移到棄牌堆
            st.hands[side].remove(action.chip_id)
            st.discards[side].append(action.chip_id)
            if action.face == '移動':
                u.pos = action.dst
                dealt += self.hook_trap_check(st, side, u)
                self.hook_resource_pickup(st, side, u)
                st.log.append({'event': '晶片移動', 'side': side,
                               'chip': action.chip_id, 'to': action.dst,
                               'move_face_used': True, 'round': st.round_no})
            else:  # 能力面
                dealt += self._apply_chip_ability(st, side, chip, action, rng)
                st.log.append({'event': '晶片能力', 'side': side,
                               'chip': action.chip_id, 'move_face_used': False,
                               'damage': dealt, 'round': st.round_no})
            return dealt

        if action.kind == '領航員':
            if action.subkind == '攻擊':
                rk, rp, dmg, hits = u.navi_attack
                spec = (rk, rp) if rp is not None else (rk,)
                dealt += self._do_attack(st, side, spec, action.target,
                                         dmg, hits, rng)
                st.log.append({'event': '自攻', 'side': side, 'damage': dealt,
                               'round': st.round_no})
            elif action.subkind == '能力':
                dealt += self.hook_apply_navi_ability(st, side, action, rng)
            elif action.subkind == '換角':
                self.hook_apply_change_navi(st, side, action, rng)
                st.log.append({'event': '換角', 'side': side,
                               'to': action.target, 'round': st.round_no})
            return dealt

        raise ValueError('未知行動：%r' % (action.kind,))

    def _apply_chip_ability(self, st, side, chip, action, rng):
        ab = chip.ability_face
        u = st.units[side]
        kind = ab['type']
        if kind == 'attack':
            spec = ab['range']
            return self._do_attack(st, side, spec, action.target,
                                   ab['dmg'], ab['hits'], rng)
        if kind == 'heal':
            u.hp = min(u.hp_max, u.hp + ab['amount'])
            return 0
        if kind == 'shield_reset':
            u.shield_cur = u.shield_max
            u.field_disabled = False    # 「若力場失效則恢復」
            return 0
        raise ValueError('未知晶片能力：%r' % (kind,))

    def _do_attack(self, st, side, spec, target, dmg, hits, rng):
        """對範圍內每個敵方單位獨立跑完整結算。回傳總 HP 傷害。"""
        cfg = st.config
        # 先手首回合傷害上限 20（傷害上限補償）
        cap = None
        if (cfg.first_turn_comp == '傷害上限20'
                and st.round_no == 1 and side == st.first_mover):
            cap = 20
        idxs = cells_hit(st.units[side].pos, side, spec, target,
                         st.enemy_positions(side))
        total = 0
        for enemy_side in idxs:
            target_unit = st.units[enemy_side]
            loss = resolve_attack(target_unit, dmg, hits, rng,
                                  dodge_mode=cfg.dodge_mode,
                                  field_overload=cfg.field_overload)
            if cap is not None and loss > cap:
                # 回補超過上限部分（傷害上限補償只限制實際 HP 損失）
                over = loss - cap
                target_unit.hp += over
                loss = cap
            total += loss
            self._check_unit_down(st, enemy_side)
        return total

    def _check_unit_down(self, st, side):
        u = st.units[side]
        if u is not None and u.hp <= 0 and u.alive:
            u.hp = 0
            # 方向一：強制換入後備（不佔行動）；共用核心＝該方陣亡
            replaced = self.hook_on_unit_down(st, side)
            if not replaced:
                u.alive = False

    def hook_on_unit_down(self, st, side):
        """單位倒下時 hook。回傳 True＝已換入後備（該方續戰）。"""
        return False

    def hook_apply_navi_ability(self, st, side, action, rng):
        return 0

    def hook_apply_change_navi(self, st, side, action, rng):
        pass

    # ---------------- 抽牌 ----------------
    def draw(self, st, side, n, rng):
        """抽 n 張。牌庫空則把棄牌堆洗回（循環型）。手牌上限 hand_limit。"""
        limit = st.config.hand_limit
        for _ in range(n):
            if len(st.hands[side]) >= limit:
                break
            if not st.decks[side]:
                if st.discards[side]:
                    st.decks[side] = st.discards[side][:]
                    st.discards[side] = []
                    rng.shuffle(st.decks[side])
                else:
                    break   # 無牌可抽
            if st.decks[side]:
                st.hands[side].append(st.decks[side].pop())

    # ---------------- 回合迴圈 ----------------
    def take_turn(self, st, side, policy, rng):
        """一方走一手（一 turn）：開始 hook → 抽牌 → 策略選兩行動 → 施行。"""
        st.side_to_move = side
        st.actions_this_turn = []
        # 回合開始 hook（能量、資源生成）
        self.hook_start_turn(st, side)
        # 每回合開始抽 draw_per_turn 張
        self.draw(st, side, st.config.draw_per_turn, rng)

        # 先手補償：first_turn_comp
        first_comp_limit = None
        if (st.config.first_turn_comp == '一行動'
                and st.round_no == 1 and side == st.first_mover):
            first_comp_limit = '一行動'

        actions = policy.choose_actions(st, side, rng, self)
        # 防呆：策略回傳的行動須是合法組合中的一員（信任策略、但夾一次數量）
        actions = self._sanitize_actions(st, side, actions, first_comp_limit)

        used = set()
        dealt_total = 0
        for act in actions:
            if act.category() != 'pass':
                used.add(act.category())
            dealt_total += self.apply_action(st, side, act, rng)
            st.actions_this_turn.append(act)
            if st.units[1 - side] is None or not st.units[1 - side].alive:
                break   # 對手已倒，停止後續行動
            # 換角不佔行動的強制換入由 hook 處理，不在此
        st.damage_this_turn[side] = dealt_total
        self.hook_end_turn(st, side)
        return dealt_total

    def _sanitize_actions(self, st, side, actions, first_comp_limit):
        """確保回傳 ≤2 個行動、同類至多 1 次；違規截斷成合法前綴。"""
        if actions is None:
            return [Action('pass'), Action('pass')]
        out = []
        used = set()
        for act in actions:
            if len(out) >= 2:
                break
            if first_comp_limit == '一行動' and len(out) >= 1:
                break
            cat = act.category()
            if cat != 'pass' and cat in used:
                continue   # 同類重複，跳過
            used.add(cat) if cat != 'pass' else None
            out.append(act)
        while len(out) < 2:
            out.append(Action('pass'))
        return out

    # ---------------- 安全網與結束判定 ----------------
    def apply_safety_net(self, st):
        """第 safety_net_turn 回合起，每回合結束雙方各扣 10 HP；
        該回合有造成 HP 傷害者豁免（造傷豁免）。回傳是否觸發。"""
        if st.round_no < st.config.safety_net_turn:
            return False
        triggered = False
        for side in (0, 1):
            u = st.units[side]
            if u is None or not u.alive:
                continue
            if st.damage_this_turn[side] > 0:
                continue   # 造傷豁免
            u.hp -= 10
            triggered = True
            if u.hp <= 0:
                self._check_unit_down(st, side)
        if triggered:
            st.log.append({'event': '安全網', 'round': st.round_no})
        return triggered

    def check_over(self, st):
        a_dead = st.units[0] is None or not st.units[0].alive
        b_dead = st.units[1] is None or not st.units[1].alive
        if a_dead and b_dead:
            st.over = True
            st.winner = None
            st.over_reason = '同歸於盡'
        elif a_dead:
            st.over = True
            st.winner = 1
            st.over_reason = '擊倒'
        elif b_dead:
            st.over = True
            st.winner = 0
            st.over_reason = '擊倒'
        return st.over

    # ---------------- B6 metrics v2：最小掛點（不動結算邏輯） ----------------
    def team_hp(self, st, side):
        """該方目前隊伍總 HP（上場單位＋存活後備）。1對1 方向（二/三）
        benches[side] 恆空，等同 units[side].hp；方向一三名合計。"""
        u = st.units[side]
        total = u.hp if (u is not None and u.alive) else 0
        for b in st.benches.get(side, ()):
            if b is not None and b.alive:
                total += b.hp
        return total

    def _snapshot_hp(self, st, rec):
        rec.hp_by_round.append(
            (st.round_no, {0: self.team_hp(st, 0), 1: self.team_hp(st, 1)}))

    # ---------------- play：跑完整一局 ----------------
    def play(self, config, setup, policy_a, policy_b):
        """跑一局，回傳 GameRecord。同 seed 同 setup 同策略＝同結果。"""
        rng = random.Random(config.seed)
        st = self.new_game(config, setup)
        policies = [policy_a, policy_b]
        rec = GameRecord()
        rec.config = config
        rec.first_mover = st.first_mover
        rec.hp_by_round.append(
            (0, {0: self.team_hp(st, 0), 1: self.team_hp(st, 1)}))  # 開局快照

        st.round_no = 1
        while True:
            for side in (st.first_mover, 1 - st.first_mover):
                st.damage_this_turn = {0: 0, 1: 0}
                self.take_turn(st, side, policies[side], rng)
                st.turn += 1
                if self.check_over(st):
                    break
            if st.over:
                break
            # 回合結束：安全網（雙方都走完後結算）
            trig = self.apply_safety_net(st)
            if trig:
                rec.safety_net_triggered = True
            self._snapshot_hp(st, rec)   # B6：本回合雙方走完＋安全網結算後快照
            if self.check_over(st):
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
            # 對局在雙方走完前結束（例：第一手就 KO）：補最終回合快照，
            # 確保 hp_by_round 末項＝ final_hp 對應回合，adv 序列不缺尾。
            self._snapshot_hp(st, rec)
        return rec
