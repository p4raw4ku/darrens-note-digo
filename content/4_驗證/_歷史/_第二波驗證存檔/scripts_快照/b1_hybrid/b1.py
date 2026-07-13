# -*- coding: utf-8 -*-
"""DIGO_EXE B1 混合方向「走位換角棋」overlay。

唯一自變量＝「2 名領航員＋換角」疊上方向二 v1.1（走位晶片棋）。資源系統
（資源球／費2／費3）原封不動沿用 Dir2OverlayEngine；晶片牌庫 36、幾何、
陷阱、位移、過載窗全部照 spec_方向二 v0＋v1.1 檔位。

規格與裁量依據：
  round2/規格_輪2_全案.md 「B1 混合方向」節
  round2/裁量_B1.md（十五條讀法定案，本檔優先權高於規格文字歧義）
  round2/reports/律師_B1.md「給引擎組的硬約束清單」節

dir1.py 換角碼不可直接 cp——三處必須覆寫（裁量檔 BL-1/BL-5/BL-6、
律師卷宗 BL-1/BL-3/BL-5/BL-6）：
  (a) 過載到期＝絕對回合數、離場不凍結（dir1/dir2 原版：力場過載旗標靠
      `st.config.extra['_overload_pending_%d'%side]` 二段式切換，且只在
      「該方單位仍上場」時才會被 hook_end_turn 檢查到——換角把單位換下場
      後，這個切換機制對誰是「現在的 st.units[side]」有依賴，形同離場
      即凍結。B1 一律改成 per-navi 絕對到期回合數，離場也照常倒數。）
  (b) 主格 A 讀法＝深拷貝整個防禦狀態物件跟人保留（盾量／護盾態／穿透
      旗標／力場值／過載到期絕對回合），不做 dir1 v0 的「回滿＋解除」。
  (c) 穿透旗標（護盾归零後下一擊全額穿透）是防禦狀態的一部分、跟人走
      （不是跟「場上位」）——需要把這個旗標從「暫存於 Unit 隱性狀態」
      提升為可被換角讀寫的一級欄位。

A/B 兩條 code path：
  A（主格）：hook_apply_change_navi 深拷貝保留離場者的完整防禦狀態機。
  B（變體）：hook_apply_change_navi 完整 dir1 v0 語義——護盾回滿＋力場
            過載解除＋穿透旗標清除（一整包防禦重置）。
  由 B1Engine(variant='A'|'B') 建構參數切換，兩條 path 都活在同一個
  Engine 類別內（覆寫同一個 hook，依 self.variant 分支），不是兩個平行
  子類複製貼上——防止兩份程式碼各自漂移。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import random

from core import (GameConfig, Action, Unit, own_rows, COLS, START_POS,
                  resolve_attack, cells_hit, range_can_reach,
                  enumerate_targets, advance_dir, in_own_half)
from chips import build_deck, Chip as _ChipView
from setups import (Dir2Engine, dir2_chip_db, DIR2_DECK_IDS, _rng_deck,
                    _draw_start)
from dir2 import (Dir2OverlayEngine, DIR2_PROTOTYPES_V2, _push_row,
                  _pull_row)
import metrics as M


# ==================================================================
# 一、隊伍原型（沿用方向二 v1.1 檔位，BL-5/BL-6 用不到 v0 原值）
# ==================================================================

B1_PROTOTYPES = dict(DIR2_PROTOTYPES_V2)   # 游擊(閃8盾15) / 壁壘(場10盾25) /
                                            # 重甲(場5閃4，決策重要1下修版)

B1_SELF_ATTACK = ('直射', 2, 10, 1)   # 自攻一律 10×1 直射2（規格明文）


# ==================================================================
# 二、per-navi 持久防禦狀態（BL-5 讀法B/C：完整狀態機，不是純量）
# ------------------------------------------------------------------
# Unit 的 __slots__ 是共用核心定義、不可改（不修改 core.py）。B1 專屬的
# 兩項持久欄位（過載到期絕對回合數／穿透旗標）用一個子類 `_B1Unit`承載：
#   - 盾量（shield_cur/shield_max）、力場失效瞬時旗標（field_disabled）
#     Unit 原生就有，本來就跟著 Unit 物件走，深拷貝/換角保留字面上
#     「換 Python 物件」即自動保留——不需要額外欄位。
#   - 但「力場失效到期的絕對回合數」與「下一擊全額穿透旗標」在共用核心
#     完全沒有 per-unit 持久欄位（dir2 用 config.extra 的 side-keyed
#     暫存，隱含「目前上場者是誰」的假設，這正是律師卷宗點名必須覆寫
#     之處）——B1 一律用建構時就是 `_B1Unit`（而非事後 `__class__` 改指
#     派——slots 佈局不同會被 Python 拒絕）的實例承載這兩項。
#   - core.Unit.clone() 寫死 `Unit.__new__(Unit)`（回傳純 Unit，不管
#     `self` 實際型別），所以 `_B1Unit` 必須自己覆寫 `clone()`，讓
#     `GameState.sim_clone()`（policies 每次決策都會呼叫）在複製 B1
#     單位時透過動態方法解析（`dup_unit.clone()` 呼叫的是 `_B1Unit.
#     clone`，不是 `Unit.clone`）連 B1 專屬欄位一起深拷貝，而不遺失。
# ==================================================================

class _B1Unit(Unit):
    """Unit 的 B1 專屬子類：加兩個持久欄位（過載到期絕對回合、穿透旗標），
    覆寫 `clone()` 使其隨深拷貝／換角搬動一起保留（不覆寫任何其他方法、
    不改變任何共用傷害/合法性行為）。"""
    __slots__ = ('overload_until_round', 'pierce_pending')

    def __init__(self, *a, **kw):
        super(_B1Unit, self).__init__(*a, **kw)
        self.overload_until_round = None   # None＝未過載；否則絕對回合數
        self.pierce_pending = False        # 下一擊全額穿透旗標（跟人）

    def clone(self):
        u = _B1Unit.__new__(_B1Unit)
        for s in Unit.__slots__:
            setattr(u, s, getattr(self, s))
        u.overload_until_round = self.overload_until_round
        u.pierce_pending = self.pierce_pending
        return u


def _ensure_b1_fields(u):
    """相容層：呼叫端只管「拿到這個 unit 的 b1 擴充欄位」，不用關心它是
    否已經是 `_B1Unit`——本檔一律用 `_B1Unit` 建構單位（見 make_b1_setup /
    hook_on_unit_down 皆只搬動既有物件、不重新建構），故這裡只是斷言＋
    回傳自身（保留函式介面，供 `_b1_resolve_attack` 等處統一呼叫風格，
    不需要每處都判斷型別）。"""
    assert isinstance(u, _B1Unit), (
        'B1 單位必須是 _B1Unit（過載/穿透旗標無處安放）：%r' % (u,))
    return u


# ==================================================================
# 三、B1 傷害結算覆寫：絕對回合過載到期＋穿透旗標跟人
# ------------------------------------------------------------------
# 不能直接用 core.resolve_attack（它把「過載中」寫成瞬時 bool
# field_disabled、把「穿透」寫成護盾狀態機的隱性瞬間效果，兩者都沒有
# 「離場後如何延續」的介面）。B1 用薄殼包一層：resolve_attack 呼叫前後，
# 從 defender（_B1Unit）的 overload_until_round / pierce_pending 同步/
# 寫回狀態——這兩個欄位就在 Unit 物件本身上，換角＝物件被搬動，欄位
# 天然跟人保留，不需要另外的旁表或搬運步驟。
# ==================================================================

def _b1_resolve_attack(defender, dmg, hits, rng, dodge_mode, field_overload,
                       cur_round):
    """薄殼：呼叫前依 defender.overload_until_round 決定 field_disabled
    是否該在本回合已恢復（絕對回合到期即解除，不管有沒有上場過），呼叫
    後從護盾狀態同步穿透旗標（讓旗標離場後也能被讀到／保留）。"""
    _ensure_b1_fields(defender)
    # ---- 過載到期判定：絕對回合數，離場不凍結（BL-1） ----
    if defender.overload_until_round is not None:
        if cur_round > defender.overload_until_round:
            defender.field_disabled = False
            defender.overload_until_round = None
        else:
            defender.field_disabled = True

    # ---- 穿透旗標：若離場前護盾已破且旗標亮，這一擊必須全額穿透 ----
    # core.resolve_attack 的「盾0時全額穿透、之後回滿」邏輯已經是逐擊
    # 判斷 shield_cur==0，這本身就是「跟人」的（shield_cur 是 Unit 欄位，
    # 隨物件走）。defender.pierce_pending 是「盾為0且尚未被穿透過」這個
    # 中間態的顯式旗標，供裁量 BL-3 的『旗標跟人』語意可被外部讀取／
    # 測試驗證（core 的護盾狀態機本身已經正確：shield_cur==0 即代表
    # 「穿透待發」，不需要另外攔截傷害結算——但需要在換角時把這個「盾
    # 是否為0」的狀態明確跟著 Unit 物件保留，而不是被 B 變體的回滿蓋掉）。
    loss = resolve_attack(defender, dmg, hits, rng, dodge_mode=dodge_mode,
                          field_overload=field_overload)

    # ---- 過載觸發後：記錄絕對到期回合＝本回合+1（受擊方下一回合結束）----
    if defender.field_disabled and defender.overload_until_round is None:
        defender.overload_until_round = cur_round + 1

    # ---- 穿透旗標同步：盾為0＝旗標亮；剛回滿＝旗標滅 ----
    defender.pierce_pending = (defender.shield_cur == 0
                               and defender.shield_max > 0)
    return loss


# ==================================================================
# 四、安全網：只扣上場者＋方級豁免（BL-2）；起點/基值/步幅可配置
# ------------------------------------------------------------------
# 共用核心 apply_safety_net 是寫死「每回合扣 10」的常數版，B1 需要
# 「起點 R0、基值 B、步幅 S」的遞增制（主格 R0=15,B=5,S=4；A/B對照格
# R0=15,B=3,S=3，沿用 dir1 v1.1 檔）——覆寫整個方法，不修共用 core.py。
# ==================================================================

class B1Engine(Dir2OverlayEngine):
    """B1 混合方向：2 名領航員＋主動換角，疊在方向二 overlay 之上。

    variant: 'A'（主格，深拷貝保留離場防禦狀態）或
             'B'（變體，dir1 v0 完整重置：盾回滿＋過載解除＋穿透旗標清除）。
    safety_net_start/base/step：安全網遞增制三參數（主格 15/5/4；A/B對照
    格 15/3/3，由呼叫端在 GameConfig 或建構參數指定）。
    """

    def __init__(self, chip_db, variant='A', safety_net_start=15,
                safety_net_base=5, safety_net_step=4):
        super(B1Engine, self).__init__(chip_db)
        if variant not in ('A', 'B'):
            raise ValueError('variant 必須是 A 或 B，得到 %r' % (variant,))
        self.variant = variant
        self.sn_start = safety_net_start
        self.sn_base = safety_net_base
        self.sn_step = safety_net_step

    # ---------------- 換角合法性（BR-5：兩活可換、一死不可換）----------------
    def hook_change_navi_actions(self, st, side):
        """主動換角僅在『有存活後備』時合法（BR-5）；強制換入純被動、
        不經此 hook（見 hook_on_unit_down），故此處只管主動換角一種。"""
        out = []
        for i, bu in enumerate(st.benches[side]):
            if bu.alive:
                out.append(Action('領航員', subkind='換角', target=i))
        return out

    # ---------------- 主動換角施行（三處覆寫的核心）----------------
    def hook_apply_change_navi(self, st, side, action, rng):
        idx = action.target
        cur = st.units[side]
        bench_unit = st.benches[side][idx]
        _ensure_b1_fields(cur)
        _ensure_b1_fields(bench_unit)

        # 換入者出現在換出者所在格（規格明文；BT-2：不算移動/位移結束，
        # 不觸發陷阱、不拾取資源——故此處故意不呼叫 hook_trap_check /
        # hook_resource_pickup，與共用 apply_action 的『移動』分支不同）。
        bench_unit.pos = cur.pos

        if self.variant == 'A':
            # ---- 主格：深拷貝保留離場時完整防禦狀態機 ----
            # bench_unit（即將上場的後備）本來就帶著自己離場時的
            # shield_cur / field_disabled / overload_until_round /
            # pierce_pending——因為它是同一個 Python 物件、從沒被誰動過
            # （不像 dir1 v0 那樣去重置它）。此分支刻意「什麼都不做」，
            # 這正是「保留」的字面意義：不 touch 任何防禦欄位。
            #
            # 過載到期＝絕對回合數（BL-1）：bench_unit.overload_until_round
            # 若非 None，離場期間我們沒有主動遞減任何東西——因為它本來
            # 就是「絕對回合」而非「剩餘回合數」，讀取時（_b1_resolve_
            # attack）用 st.round_no 比較即可得到「離場照樣繼續倒數」的
            # 效果，不需要在換角當下做任何事。
            pass
        else:
            # ---- B 變體：完整 dir1 v0 語義，一整包防禦重置（BL-6）----
            bench_unit.shield_cur = bench_unit.shield_max
            bench_unit.field_disabled = False
            bench_unit.overload_until_round = None
            bench_unit.pierce_pending = False

        bench_unit.on_bench = False
        cur.on_bench = True
        st.benches[side][idx] = cur
        st.units[side] = bench_unit

    # ---------------- 強制換入（BR-5：不佔行動，兩名皆倒＝敗）----------------
    def hook_on_unit_down(self, st, side):
        cur = st.units[side]
        cur.alive = False
        cur.hp = 0
        alive_bench = [i for i, b in enumerate(st.benches[side]) if b.alive]
        if not alive_bench:
            return False   # 唯一後備也倒下／本無後備＝該方輸
        idx = alive_bench[0]
        newu = st.benches[side][idx]
        _ensure_b1_fields(newu)
        # 強制換入不做防禦重置也不做深拷貝保留的『選擇』——它就是把已經
        # 保留著自己防禦狀態的後備原物件搬上場（與主動換角 A 分支同一套
        # 「不 touch 防禦欄位」的精神；強制換入本來就只有唯一後備、沒有
        # A/B 兩種讀法好選，規格也沒說強制換入要重置防禦）。
        center = (2, 2) if side == 0 else (5, 2)
        newu.pos = center
        newu.on_bench = False
        st.benches[side][idx] = cur
        st.units[side] = newu
        st.log.append({'event': '強制換入', 'side': side, 'to': idx,
                       'round': st.round_no})
        return True

    # ---------------- 傷害結算：接入 B1 過載/穿透薄殼 ----------------
    def _do_attack(self, st, side, spec, target, dmg, hits, rng):
        """覆寫共用 `_do_attack`：改呼叫 `_b1_resolve_attack`（帶絕對回合
        過載到期＋穿透旗標同步），其餘（傷害上限補償、cells_hit 命中枚舉、
        _check_unit_down）邏輯逐字照抄共用核心，不更動語意。"""
        cfg = st.config
        cap = None
        if (cfg.first_turn_comp == '傷害上限20'
                and st.round_no == 1 and side == st.first_mover):
            cap = 20
        idxs = cells_hit(st.units[side].pos, side, spec, target,
                         st.enemy_positions(side))
        total = 0
        for enemy_side in idxs:
            target_unit = st.units[enemy_side]
            loss = _b1_resolve_attack(target_unit, dmg, hits, rng,
                                      dodge_mode=cfg.dodge_mode,
                                      field_overload=cfg.field_overload,
                                      cur_round=st.round_no)
            if cap is not None and loss > cap:
                over = loss - cap
                target_unit.hp += over
                loss = cap
            total += loss
            self._check_unit_down(st, enemy_side)
        return total

    def _apply_chip_ability(self, st, side, chip, action, rng):
        """晶片能力面攻擊（含換位裝置/鉤索的 on_hit 位移）沿用
        Dir2OverlayEngine 的完整邏輯（費2旗標／位移／陷阱聯動），只有
        底層傷害結算需要走 B1 的過載/穿透薄殼——但 Dir2OverlayEngine 內部
        呼叫的是 `super()._apply_chip_ability`（一路回到 core.Engine），
        並非直接呼叫 resolve_attack，故改為在 attack 分支前先委派給共用
        `_do_attack`（已被上面覆寫成 B1 版）：直接重寫 heal/shield_reset
        以外的攻擊分支，其餘（陷阱/位移/費2旗標）保留 Dir2OverlayEngine
        原始程式路徑不變。"""
        ab = chip.ability_face
        if ab['type'] == 'attack':
            key = '_hits_bonus_pending_%d' % side
            if st.config.extra.get(key):
                ab = dict(ab)
                ab['hits'] = ab['hits'] + 1
                st.config.extra[key] = False
                chip = _ChipView(chip.cid, chip.name, chip.move_face, ab)
            if 'on_hit' in ab:
                # 換位裝置/鉤索：交給 Dir2OverlayEngine 完整流程（它內部
                # 呼叫的 super()._apply_chip_ability 一路落到
                # core.Engine._apply_chip_ability → 沒有走 B1 薄殼）。
                # 為了讓推/拉類攻擊的傷害也套用 B1 的過載/穿透，這裡直接
                # 內聯複製 Dir2OverlayEngine 的位移邏輯，但呼叫 B1 的
                # `_do_attack`（見下）。
                u = st.units[side]
                spec = ab['range']
                idxs_before = cells_hit(u.pos, side, spec, action.target,
                                        st.enemy_positions(side))
                dealt = self._do_attack(st, side, spec, action.target,
                                        ab['dmg'], ab['hits'], rng)
                kind, amount = ab['on_hit']
                for enemy_side in idxs_before:
                    target_unit = st.units[enemy_side]
                    if target_unit is None or not target_unit.alive:
                        continue
                    row, col = target_unit.pos
                    if kind == '推':
                        new_row = _push_row(side, row)
                    elif kind == '拉':
                        new_row = _pull_row(side, row)
                    else:
                        raise ValueError('未知 on_hit 種類：%r' % (kind,))
                    if new_row != row:
                        target_unit.pos = (new_row, col)
                        st.log.append({'event': '強制位移', 'side': side,
                                       'victim': enemy_side, 'kind': kind,
                                       'to': target_unit.pos,
                                       'round': st.round_no})
                        extra = self.hook_trap_check(st, enemy_side,
                                                     target_unit)
                        if extra:
                            dealt += extra
                            self._check_unit_down(st, enemy_side)
                    else:
                        st.log.append({'event': '強制位移無效', 'side': side,
                                       'victim': enemy_side, 'kind': kind,
                                       'round': st.round_no})
                return dealt
            return self._do_attack(st, side, ab['range'], action.target,
                                   ab['dmg'], ab['hits'], rng)
        if ab['type'] == 'heal':
            u = st.units[side]
            u.hp = min(u.hp_max, u.hp + ab['amount'])
            return 0
        if ab['type'] == 'shield_reset':
            u = st.units[side]
            u.shield_cur = u.shield_max
            u.field_disabled = False
            _ensure_b1_fields(u).overload_until_round = None
            return 0
        if ab['type'] == 'trap':
            existing = [t for t in st.traps if t['owner'] == side
                       and not t['revealed']]
            for t in existing:
                st.traps.remove(t)
            pos = action.target
            st.traps.append({'owner': side, 'pos': pos, 'dmg': ab['dmg'],
                             'hits': ab['hits'], 'revealed': False})
            st.log.append({'event': '布陷阱', 'side': side, 'pos': pos,
                           'round': st.round_no})
            return 0
        raise ValueError('未知晶片能力：%r' % (ab['type'],))

    # 注意：不需要覆寫 apply_action。領航員自攻（Action.subkind=='攻擊'）
    # 在 core.Engine.apply_action 內是直接呼叫 `self._do_attack`——該方法
    # 已被本類覆寫成 B1 版（帶過載絕對計時／穿透旗標薄殼），Dir2OverlayEngine
    # 與 core.Engine 都未覆寫 apply_action 本身，動態方法解析（self._do_
    # attack）自然讓自攻也走新版結算，不需要整個複寫 apply_action。

    # ---------------- hook_end_turn：不再用 dir2 的 side-keyed 切換 ----------------
    def hook_end_turn(self, st, side):
        """B1 完全不使用 dir2/setups 的『_overload_pending_%d』二段式
        切換（那套機制隱含『目前上場者是誰』的假設，換角後失真——即律師
        卷宗點名的凍結行為來源）。過載到期改在 `_b1_resolve_attack` 內
        以絕對回合數即時判定，此 hook 對過載無事可做；但陷阱/資源仍由
        Dir2OverlayEngine.hook_start_turn 處理（不受影響），此處故意
        NOT 呼叫 super().hook_end_turn()（那會誤觸發 dir2 的過載切換
        邏輯，讀取/清除一個 B1 用不到、且可能與 config.extra 命名衝突
        的鍵）。"""
        pass

    # ---------------- B6 team_hp：全隊總 HP 口徑（BT-1）----------------
    def team_hp(self, st, side):
        u = st.units[side]
        total = u.hp if (u is not None and u.alive) else 0
        for b in st.benches.get(side, ()):
            if b is not None and b.alive:
                total += b.hp
        return total

    # ---------------- 安全網：只扣上場者＋方級豁免＋遞增制（BL-2）----------------
    def apply_safety_net(self, st):
        """第 sn_start 回合起，每回合結束對『當前上場者』扣血；扣血量
        隨回合遞增（基值 + 步幅×經過的安全網回合數，1-indexed：第
        sn_start 回合扣 base、sn_start+1 回合扣 base+step……）。
        豁免以『該方本回合有無造成傷害』為準（跟方不跟單名，BL-2）。
        """
        if st.round_no < self.sn_start:
            return False
        elapsed = st.round_no - self.sn_start   # 0-indexed 第幾個安全網回合
        amount = self.sn_base + self.sn_step * elapsed
        triggered = False
        for side in (0, 1):
            u = st.units[side]
            if u is None or not u.alive:
                continue
            if st.damage_this_turn[side] > 0:
                continue   # 造傷豁免（跟方：本回合『該方』有造傷即豁免）
            u.hp -= amount
            triggered = True
            if u.hp <= 0:
                self._check_unit_down(st, side)
        if triggered:
            st.log.append({'event': '安全網', 'round': st.round_no,
                           'amount': amount})
        return triggered


def build_b1(config, variant='A', proto_a=('游擊', '壁壘'),
            proto_b=('游擊', '壁壘'), safety_net_start=15,
            safety_net_base=5, safety_net_step=4):
    """組裝 B1 (engine, setup)。

    proto_a/proto_b：各方 2 名領航員原型名稱 tuple，**列首固定先發**
    （BR-6：主格 游擊＋壁壘 對 游擊＋壁壘，游擊先上）。
    """
    eng = B1Engine(dir2_chip_db(), variant=variant,
                  safety_net_start=safety_net_start,
                  safety_net_base=safety_net_base,
                  safety_net_step=safety_net_step)
    setup = make_b1_setup(proto_a, proto_b)
    return eng, setup


def make_b1_setup(proto_a=('游擊', '壁壘'), proto_b=('游擊', '壁壘')):
    def setup(engine, st, config):
        for side, protos in ((0, proto_a), (1, proto_b)):
            units = []
            for name in protos:
                dd = B1_PROTOTYPES[name]
                u = _B1Unit(name=name, hp=config.hp, pos=START_POS[side],
                           navi_attack=B1_SELF_ATTACK, ability=None,
                           team_id=side, **dd)
                units.append(u)
            # 列首固定先發（BR-6）：protos[0] 先上，其餘進 benches
            st.units[side] = units[0]
            st.benches[side] = units[1:]
            for b in st.benches[side]:
                b.on_bench = True
            deck = build_deck(DIR2_DECK_IDS, copies=2)
            st.decks[side] = deck[:]
            _rng_deck(st, side)
            _draw_start(engine, st, side)
    return setup


def base_b1_config(hp=50, variant_ab='主格'):
    """主格：起點15/基值5/步幅+4；A/B 對照格（安全網 A/B）：基值3/步幅3
    （dir1 v1.1 檔，仍起點15）——呼叫端自行決定用哪組常數，本函式只回傳
    GameConfig 本身（安全網三參數在 build_b1 另外傳）。"""
    return GameConfig(direction=None, hp=hp, first_turn_comp='一行動',
                      dodge_mode='機率制', field_overload='開',
                      safety_net_turn=15, max_turns=60, seed=1000,
                      oneply_samples=1, expect_samples=1)
