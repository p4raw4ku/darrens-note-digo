# DIGO_EXE 驗證引擎契約 v0

> 給實作 agent 的介面契約。目標：一個共用引擎＋三個方向模組，全部純 Python 標準庫（不裝套件），放本資料夾 `engine/` 下。**只讀 vault、只寫 scratchpad、不開子 agent。**

## 檔案佈局

```
digo_verify/
├── spec_共用基準.md / spec_方向一…二…三….md   ← 規格（唯一權威）
├── engine/
│   ├── core.py          ← 幾何、行動經濟、回合迴圈、傷害結算（共用）
│   ├── chips.py         ← 晶片資料（照規格表逐張轉錄，含方向增刪）
│   ├── policies.py      ← 策略套件（共用）＋方向專屬策略
│   ├── dir1.py / dir2.py / dir3.py   ← 方向 overlay（換角/資源/精簡）
│   ├── metrics.py       ← 指標計算（本檔第五節公式）
│   ├── runner.py        ← 實驗矩陣執行器（CLI，輸出 JSON 到 results/）
│   └── tests.py         ← 驗收測試（本檔第六節，全過才算交付）
└── results/             ← 每個實驗一個 JSON＋一份 markdown 摘要
```

## 一、傷害結算（從 vault 移植，語義不可改）

移植 `2_DIGO_EXE/9_系統/scripts/sim_combat.py` 的 `resolve_attack` 逐擊狀態機：
閃避前置（每點 1/3 機率抵銷一整擊，二項分佈）→ 每擊過力場（單次傷害減力場值、最低 0）→ 護盾狀態機（盾>0 吸收；歸 0 後下一擊全額穿透、該擊之後回滿）。
範圍攻擊對範圍內每個敵方單位獨立跑一次完整結算。
變體開關（config）：`dodge_mode ∈ {機率制, 超額削減}`、`field_overload ∈ {關, 開}`（定義見共用基準 §四）。

## 二、狀態與介面

```python
GameConfig: direction(1|2|3), hp, first_turn_comp(無|一行動|傷害上限20),
            dodge_mode, field_overload, safety_net_turn(=25), max_turns(=60), seed
GameState:  turn, side_to_move, units[](hp, defenses, pos, bench…), hands, decks,
            discard, energy/resources, traps, log[]   # log 供指標事後計算
Action:     Move(dst) | Chip(chip_id, face=移動|能力, target) | Navi(攻擊|能力|換角, target) | Pass
Policy 介面: choose_actions(state, side, rng) -> [Action, Action]  # 一回合的行動組
engine.legal_actions(state, side) -> list   # 唯一合法性判定入口，策略不得自算
engine.play(config, policy_a, policy_b) -> GameRecord   # 全局可重現（同 seed 同結果）
```

## 三、策略套件（反思二教訓：對手必須會走位）

共用：`random_legal`（合法隨機）、`greedy_damage`（最大化本回合期望傷害）、`turtle`（最大化與敵距離與防禦、僅打零風險目標）、`positional`（最大化下回合射程覆蓋與機動）、`oneply`（枚舉自己兩行動組合、對手回應抽樣，取期望最優）。
方向一加：`predictor`（依對位劣勢與殘血估計對手換角機率、針對佈局）與 `naive`（同 oneply 但視換角為雜訊）。
方向二加：`resource_aware`（把資源球納入 oneply 價值）與 `resource_blind`。
所有期望值用固定 seed 抽樣（每決策 ≥ 200 樣本）估計。

## 四、實驗矩陣（runner.py 逐項執行、可斷點續跑）

1. 各方向：策略循環賽（含鏡像自對局），**每配對 2000 局**（存活條 6：勝率檢定力）。
2. 掃描（用該方向主力配對跑）：HP 三檔 × 先手補償三檔；題4 A/B：dodge_mode 兩檔、field_overload 兩檔；方向一另掃「換角佔行動 vs 費能量」；方向二另掃「資源制開／關」。
3. 相剋矩陣：全攻擊形狀 × 全防禦配置的有效傷害期望（隔離結算、每格 4000 次）。
4. 覆蓋矩陣（題5 驗證法、純幾何枚舉，不需對局）。

## 五、指標公式（結果 JSON 必含）

- 對局長度：中位、九十百分位、上限觸頂率、安全網觸發率。
- 先手勝率（每配對含 95% 信賴區間，n=2000 時約 ±2.2 個百分點）。
- 移動面被選率＝晶片行動中取移動面的比例；移動行動占比＝移動類行動／全行動。
- 追逐死結率＝出現「連續 ≥4 回合雙方皆零 HP 傷害」的對局比例。
- 尺①真兩難密度：晶片使用時兩面 oneply 期望價值差 ≤ 較大者兩成的比例。
- 尺②口訣化：可見特徵（相對位置類、HP 帶、防禦型、列距、能量帶）分桶，各桶最頻行動占比加權平均；≥90% 標紅。
- 尺③手牌敏感度：抽樣決策點、手牌重抽 10 次後最佳行動翻轉比例。
- 相剋健康度：無「被全形狀弱支配」的防禦、無「對全防禦最優」的形狀（各留非零穿透剋制路徑）。
- 方向專屬指標照各 spec「專屬指標」節。

## 六、驗收測試（tests.py，全綠才交付）

1. 回歸（傷害核心對 sim_combat.py 已知值，機率制、seed 固定）：對護盾 5——5×8 實傷 20、20×2 實傷 35、40×1 實傷 35、10×4 實傷 30；無防禦 40×1 實傷 40。
2. 不變量（每方向各 500 局 random_legal 對打）：HP 單調不增（除迴復）、行動合法性（同類 ≤1、每回合 ≤2）、牌守恆（手＋庫＋棄＝總數）、全局在 max_turns 內結束、同 seed 全等重現。
3. 幾何：覆蓋矩陣人工抽查三例（直射、鎖列、十字）與規格逐字核對。
4. 方向一：換角後防禦生效正確、強制換入不佔行動;方向二：拾取不佔行動、陷阱只對敵方觸發且觸發後現形。
