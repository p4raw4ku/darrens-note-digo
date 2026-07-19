---
類型: 參考資料
建立日期: 2026-07-13
更新日期: 2026-07-13
cssclasses:
  - exe3-table
相關頁面:
  - "[[0_index_參考資料]]"
  - "[[1_EXE3_標準晶片表]]"
  - "[[3_EXE3_程式廣告表]]"
---

# EXE3 範本晶片組（ROM 內 14 夾×30 張）

> **權威層＝ROM**（日版無印＋Black 實測、兩版晶片資料完全相同；版型與方法見 [[1_EXE3_ROM對源驗證]]）；英文名與效果摘要＝wiki 輔助層。數值為 EXE3 即時制原文、**不得直接移植 DIGO**（口徑見 [[0_index_參考資料]]）。本表由 `parse_exe3_rom.py` 產生、不手改。

> 夾區＝ROM `0xCB58` 起連續 14 夾——前 11 夾對應 TREZ 記載（九夾逐張全等、HadesFolder 差 1 張、ApprenticeFolder 差 2 張，以 ROM 為準）；**後 3 夾為 TREZ 未收錄的教學／殘留夾**（ROM 才看得到）。取得處屬 wiki 層（見快照）。

## Folder1（起手）（15 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| エアシュート1<br>（AirShot1） | ＊ | 3 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|擊退]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 命中並擊退1格 | 無 |
| ショットガン<br>（ShotGun） | J | 3 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點後1格；命中後波及身後1格 | 無 |
| ブイガン<br>（V-Gun） | D | 3 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點斜後2格；命中後波及斜後2格 | 無 |
| ソード<br>（Sword） | L | 3 | 80 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；斬擊前方1格 | 無 |
| キャノン<br>（Cannon） | A | 2 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |
| キャノン<br>（Cannon） | B | 2 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |
| ミニボム<br>（MiniBomb） | B | 2 | 50 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 前3落點；投彈至前方3格 | 無 |
| パネルアウト1<br>（PanlOut1） | B | 2 | 10 | 地形格 | 前1格<br>![[DIGO_EXE_範圍_前1格.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|破格]]</span> | 破壞前方1格 | 無 |
| リカバリー10<br>（Recov10） | A | 2 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復10 | 無 |
| リカバリー10<br>（Recov10） | L | 2 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復10 | 無 |
| アタック+10<br>（Atk+10） | ＊ | 2 | ???? | 手牌 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|強化]]</span> | +10；選中的攻擊晶片+10 | 無 |
| サイドガン<br>（SideGun） | S | 1 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點上下2格；命中後波及上下2格 | 無 |
| ミニボム<br>（MiniBomb） | S | 1 | 50 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 前3落點；投彈至前方3格 | 無 |
| ワイドソード<br>（WideSwrd） | L | 1 | 80 | 敵<br>複數 | 寬斬<br>![[DIGO_EXE_範圍_寬斬.png\|110]] |  | 縱3；斬擊前方敵人範圍：3格 | 無 |
| エリアスチール<br>（AreaGrab） | L | 1 | 10 | 地形格 | 敵前縱列<br>![[DIGO_EXE_範圍_敵前縱列.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|奪格]]</span> | 奪取敵陣最前一列 | 無 |

碼分佈：L:7、B:6、＊:5、A:4、D:3、J:3、S:2、攻擊卡名目均 39

## Folder2（14 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| ラットン1<br>（Ratton1） | H | 4 | 80 | 敵<br>單體 | 軌跡<br>![[DIGO_EXE_範圍_軌跡.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|追蹤]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|轉彎]]</span> | 沿地爬行、轉彎一次 | 無 |
| アイスウェーブ1<br>（IceWave1） | W | 4 | 80 | 敵<br>複數 | 貫穿<br>![[DIGO_EXE_範圍_貫穿.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|地面波]]</span> | 製造寬2格的冰浪 | 水 |
| リカバリー50<br>（Recov50） | ＊ | 4 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復50 | 無 |
| ミニボム<br>（MiniBomb） | ＊ | 3 | 50 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 前3落點；投彈至前方3格 | 無 |
| ラビリング1<br>（ZapRing1） | S | 3 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|麻痺]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 電環攻擊、命中麻痺 | 電 |
| ラビリング2<br>（ZapRing2） | W | 3 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|麻痺]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 電環攻擊、命中麻痺 | 電 |
| アタック+10<br>（Atk+10） | ＊ | 2 | ???? | 手牌 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|強化]]</span> | +10；選中的攻擊晶片+10 | 無 |
| ワイドソード<br>（WideSwrd） | E | 1 | 80 | 敵<br>複數 | 寬斬<br>![[DIGO_EXE_範圍_寬斬.png\|110]] |  | 縱3；斬擊前方敵人範圍：3格 | 無 |
| カスタムソード<br>（CustSwrd） | V | 1 | ???? | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；客製化計量條＝攻擊力 | 無 |
| イアイフォーム<br>（Slasher） | D | 1 | 240 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|迎擊]]</span> | 按住A鍵時持續斬擊 | 無 |
| エリアスチール<br>（AreaGrab） | L | 1 | 10 | 地形格 | 敵前縱列<br>![[DIGO_EXE_範圍_敵前縱列.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|奪格]]</span> | 奪取敵陣最前一列 | 無 |
| ポーン<br>（Pawn） | E | 1 | 90 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|迎擊]]</span> | 按A鍵發動攻擊 | 無 |
| ナイト<br>（Knight） | U | 1 | 150 | 敵<br>單體 | 軌跡<br>![[DIGO_EXE_範圍_軌跡.png\|110]] |  | 跳躍落點；向前跳躍並攻擊 | 無 |
| ルーク<br>（Rook） | Q | 1 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|屏障]]</span> | 保護你免受攻擊 | 無 |

碼分佈：＊:9、W:7、H:4、S:3、E:2、D:1、L:1、Q:1、U:1、V:1、攻擊卡名目均 70

## PreFolder（19 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| メットガード<br>（Guard） | ＊ | 4 | 40 | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|屏障]]</span> | 反彈敵人的攻擊 | 無 |
| アタック+10<br>（Atk+10） | ＊ | 3 | ???? | 手牌 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|強化]]</span> | +10；選中的攻擊晶片+10 | 無 |
| ショットガン<br>（ShotGun） | F | 2 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點後1格；命中後波及身後1格 | 無 |
| ブイガン<br>（V-Gun） | G | 2 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點斜後2格；命中後波及斜後2格 | 無 |
| サイドガン<br>（SideGun） | Y | 2 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點上下2格；命中後波及上下2格 | 無 |
| ラットン1<br>（Ratton1） | A | 2 | 80 | 敵<br>單體 | 軌跡<br>![[DIGO_EXE_範圍_軌跡.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|追蹤]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|轉彎]]</span> | 沿地爬行、轉彎一次 | 無 |
| ラットン1<br>（Ratton1） | F | 2 | 80 | 敵<br>單體 | 軌跡<br>![[DIGO_EXE_範圍_軌跡.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|追蹤]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|轉彎]]</span> | 沿地爬行、轉彎一次 | 無 |
| パネルスチール<br>（PanlGrab） | Y | 2 | 10 | 地形格 | 敵前1格<br>![[DIGO_EXE_範圍_敵前1格.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|奪格]]</span> | 奪取1格敵方格子 | 無 |
| ショットガン<br>（ShotGun） | ＊ | 1 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點後1格；命中後波及身後1格 | 無 |
| ブイガン<br>（V-Gun） | ＊ | 1 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點斜後2格；命中後波及斜後2格 | 無 |
| サイドガン<br>（SideGun） | ＊ | 1 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點上下2格；命中後波及上下2格 | 無 |
| スプレッドガン<br>（Spreader） | M | 1 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點大爆；製造大爆炸 | 無 |
| スプレッドガン<br>（Spreader） | N | 1 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點大爆；製造大爆炸 | 無 |
| スプレッドガン<br>（Spreader） | O | 1 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點大爆；製造大爆炸 | 無 |
| ソード<br>（Sword） | Y | 1 | 80 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；斬擊前方1格 | 無 |
| ワイドソード<br>（WideSwrd） | Y | 1 | 80 | 敵<br>複數 | 寬斬<br>![[DIGO_EXE_範圍_寬斬.png\|110]] |  | 縱3；斬擊前方敵人範圍：3格 | 無 |
| ロングソード<br>（LongSwrd） | Y | 1 | 80 | 敵<br>複數 | 深斬<br>![[DIGO_EXE_範圍_深斬.png\|110]] |  | 前2；斬擊前方敵人範圍：2格 | 無 |
| ダッシュアタック<br>（DashAtk） | G | 1 | 90 | 敵<br>複數 | 貫穿<br>![[DIGO_EXE_範圍_貫穿.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|突進]]</span> | 衝刺穿越敵人 | 無 |
| バンブーランス<br>（Lance） | H | 1 | 130 | 敵<br>複數 | 末列<br>![[DIGO_EXE_範圍_末列.png\|110]] |  | 長槍貫穿後排 | 木 |

碼分佈：＊:10、Y:7、F:4、G:3、A:2、H:1、M:1、N:1、O:1、攻擊卡名目均 49

## HadesFolder（17 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| バーニングボディ<br>（Burner） | S | 4 | 130 | 敵<br>複數 | 自身周圍<br>![[DIGO_EXE_範圍_自身周圍.png\|110]] |  | 以火焰包覆自身 | 火 |
| ブーメラン1<br>（Boomer1） | H | 4 | 60 | 敵<br>複數 | 軌跡<br>![[DIGO_EXE_範圍_軌跡.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|繞場]]</span> | 迴力鏢繞場一周 | 木 |
| シングルボム<br>（SnglBomb） | D | 3 | 50 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 前3落點；投擲大型炸彈至3格外 | 無 |
| ホウガン<br>（CannBall） | D | 3 | 160 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 落點單格；破壞前方第3格 | 無 |
| バブルショット<br>（Bubbler） | A | 2 | 60 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 命中後波及身後1格 | 水 |
| ヒートショット<br>（HeatShot） | B | 2 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 命中後波及身後1格 | 火 |
| リカバリー80<br>（Recov80） | D | 2 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復80 | 無 |
| ワイドソード<br>（WideSwrd） | Q | 1 | 80 | 敵<br>複數 | 寬斬<br>![[DIGO_EXE_範圍_寬斬.png\|110]] |  | 縱3；斬擊前方敵人範圍：3格 | 無 |
| ロングソード<br>（LongSwrd） | E | 1 | 80 | 敵<br>複數 | 深斬<br>![[DIGO_EXE_範圍_深斬.png\|110]] |  | 前2；斬擊前方敵人範圍：2格 | 無 |
| フレイムソード<br>（FireSwrd） | F | 1 | 130 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；斬擊前方3格 | 火 |
| アクアソード<br>（AquaSwrd） | N | 1 | 150 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；斬擊前方3格 | 水 |
| エレキソード<br>（ElecSwrd） | V | 1 | 130 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；斬擊前方3格 | 電 |
| バンブーソード<br>（BambSwrd） | W | 1 | 140 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；斬擊前方3格 | 木 |
| アタック+10<br>（Atk+10） | ＊ | 1 | ???? | 手牌 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|強化]]</span> | +10；選中的攻擊晶片+10 | 無 |
| ロール<br>（Roll） | R | 1 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 攻擊敵人同時回復自身HP；攻擊敵人並回復自身HP | 無 |
| ガッツマン<br>（GutsMan） | G | 1 | 50 | 地形格 | 區域 | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|破格]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|突進]]</span> | 偷襲並砸毀地板；潛行接近後粉碎格子 | 無 |
| ガッツマンV2<br>（GutsMan V2） | G | 1 | 70 | 地形格 | 區域 | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|破格]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|突進]]</span> | 偷襲並砸毀地板；潛行接近後粉碎格子 | 無 |

碼分佈：D:8、H:4、S:4、A:2、B:2、G:2、E:1、F:1、N:1、Q:1、R:1、V:1、W:1、＊:1、攻擊卡名目均 90

## N1-FolderA（24 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| ソニックウェーブ<br>（SonicWav） | G | 3 | 80 | 敵<br>複數 | 貫穿<br>![[DIGO_EXE_範圍_貫穿.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|地面波]]</span> | 衝擊波貫穿敵人 | 無 |
| ハイキャノン<br>（HiCannon） | H | 2 | 60 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |
| ラビリング1<br>（ZapRing1） | A | 2 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|麻痺]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 電環攻擊、命中麻痺 | 電 |
| エリアスチール<br>（AreaGrab） | ＊ | 2 | 10 | 地形格 | 敵前縱列<br>![[DIGO_EXE_範圍_敵前縱列.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|奪格]]</span> | 奪取敵陣最前一列 | 無 |
| インビジブル<br>（Invis） | ＊ | 2 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|隱身]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|時限]]</span> | 短暫隱形 | 無 |
| ハイキャノン<br>（HiCannon） | I | 1 | 60 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |
| ハイキャノン<br>（HiCannon） | J | 1 | 60 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |
| ソード<br>（Sword） | Y | 1 | 80 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；斬擊前方1格 | 無 |
| ワイドソード<br>（WideSwrd） | Y | 1 | 80 | 敵<br>複數 | 寬斬<br>![[DIGO_EXE_範圍_寬斬.png\|110]] |  | 縱3；斬擊前方敵人範圍：3格 | 無 |
| ロングソード<br>（LongSwrd） | Y | 1 | 80 | 敵<br>複數 | 深斬<br>![[DIGO_EXE_範圍_深斬.png\|110]] |  | 前2；斬擊前方敵人範圍：2格 | 無 |
| ロングソード<br>（LongSwrd） | L | 1 | 80 | 敵<br>複數 | 深斬<br>![[DIGO_EXE_範圍_深斬.png\|110]] |  | 前2；斬擊前方敵人範圍：2格 | 無 |
| ロングソード<br>（LongSwrd） | R | 1 | 80 | 敵<br>複數 | 深斬<br>![[DIGO_EXE_範圍_深斬.png\|110]] |  | 前2；斬擊前方敵人範圍：2格 | 無 |
| フレイムソード<br>（FireSwrd） | F | 1 | 130 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；斬擊前方3格 | 火 |
| アクアソード<br>（AquaSwrd） | A | 1 | 150 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；斬擊前方3格 | 水 |
| エレキソード<br>（ElecSwrd） | E | 1 | 130 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；斬擊前方3格 | 電 |
| バンブーソード<br>（BambSwrd） | W | 1 | 140 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；斬擊前方3格 | 木 |
| バリアブルソード<br>（VarSwrd） | C | 1 | 160 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；變化型魔法劍 | 無 |
| バーニングボディ<br>（Burner） | F | 1 | 130 | 敵<br>複數 | 自身周圍<br>![[DIGO_EXE_範圍_自身周圍.png\|110]] |  | 以火焰包覆自身 | 火 |
| ラビリング1<br>（ZapRing1） | ＊ | 1 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|麻痺]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 電環攻擊、命中麻痺 | 電 |
| バンブーランス<br>（Lance） | Z | 1 | 130 | 敵<br>複數 | 末列<br>![[DIGO_EXE_範圍_末列.png\|110]] |  | 長槍貫穿後排 | 木 |
| ブーメラン1<br>（Boomer1） | H | 1 | 60 | 敵<br>複數 | 軌跡<br>![[DIGO_EXE_範圍_軌跡.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|繞場]]</span> | 迴力鏢繞場一周 | 木 |
| ロール<br>（Roll） | R | 1 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 攻擊敵人同時回復自身HP；攻擊敵人並回復自身HP | 無 |
| フラッシュマン<br>（FlashMan） | F | 1 | 50 | 敵方 | 區域 | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|麻痺]]</span> | 閃光攻擊使敵人麻痺；閃光攻擊使敵人麻痺 | 電 |
| ビーストマン<br>（BeastMan） | B | 1 | 40 | 敵方 | 前縱3<br>![[DIGO_EXE_範圍_前縱3.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|突進]]</span> | 爪擊前方三格；爪擊前方3格 | 無 |

碼分佈：＊:5、A:3、F:3、G:3、H:3、Y:3、R:2、B:1、C:1、E:1、I:1、J:1、L:1、W:1、Z:1、攻擊卡名目均 75

## N1-FolderB（20 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| エアシュート1<br>（AirShot1） | ＊ | 4 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|擊退]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 命中並擊退1格 | 無 |
| バブルショット<br>（Bubbler） | ＊ | 4 | 60 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 命中後波及身後1格 | 水 |
| ヒートショット<br>（HeatShot） | ＊ | 4 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 命中後波及身後1格 | 火 |
| キャノン<br>（Cannon） | B | 2 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |
| キャノン<br>（Cannon） | A | 1 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |
| キャノン<br>（Cannon） | C | 1 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |
| ラビリング1<br>（ZapRing1） | A | 1 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|麻痺]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 電環攻擊、命中麻痺 | 電 |
| ラビリング1<br>（ZapRing1） | M | 1 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|麻痺]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 電環攻擊、命中麻痺 | 電 |
| ラビリング1<br>（ZapRing1） | P | 1 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|麻痺]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 電環攻擊、命中麻痺 | 電 |
| ラビリング1<br>（ZapRing1） | ＊ | 1 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|麻痺]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 電環攻擊、命中麻痺 | 電 |
| ヨーヨー1<br>（Yo-Yo1） | C | 1 | 40 | 敵<br>複數 | 橫向3格<br>![[DIGO_EXE_範圍_橫向3格.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|多擊]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|震盪]]</span> | 往返3格的溜溜球 | 無 |
| ヨーヨー1<br>（Yo-Yo1） | E | 1 | 40 | 敵<br>複數 | 橫向3格<br>![[DIGO_EXE_範圍_橫向3格.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|多擊]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|震盪]]</span> | 往返3格的溜溜球 | 無 |
| ヨーヨー1<br>（Yo-Yo1） | G | 1 | 40 | 敵<br>複數 | 橫向3格<br>![[DIGO_EXE_範圍_橫向3格.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|多擊]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|震盪]]</span> | 往返3格的溜溜球 | 無 |
| ヨーヨー1<br>（Yo-Yo1） | ＊ | 1 | 40 | 敵<br>複數 | 橫向3格<br>![[DIGO_EXE_範圍_橫向3格.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|多擊]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|震盪]]</span> | 往返3格的溜溜球 | 無 |
| リカバリー30<br>（Recov30） | F | 1 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復30 | 無 |
| リカバリー30<br>（Recov30） | H | 1 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復30 | 無 |
| リカバリー30<br>（Recov30） | M | 1 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復30 | 無 |
| リカバリー80<br>（Recov80） | D | 1 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復80 | 無 |
| ロール<br>（Roll） | R | 1 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 攻擊敵人同時回復自身HP；攻擊敵人並回復自身HP | 無 |
| ガッツマン<br>（GutsMan） | G | 1 | 50 | 地形格 | 區域 | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|破格]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|突進]]</span> | 偷襲並砸毀地板；潛行接近後粉碎格子 | 無 |

碼分佈：＊:14、A:2、B:2、C:2、G:2、M:2、D:1、E:1、F:1、H:1、P:1、R:1、攻擊卡名目均 37

## N1-FolderC（15 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| シングルボム<br>（SnglBomb） | H | 4 | 50 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 前3落點；投擲大型炸彈至3格外 | 無 |
| ホウガン<br>（CannBall） | P | 4 | 160 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 落點單格；破壞前方第3格 | 無 |
| パネルアウト3<br>（PanlOut3） | ＊ | 4 | 10 | 地形格 | 前縱3<br>![[DIGO_EXE_範圍_前縱3.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|破格]]</span> | 破壞前方3格 | 無 |
| カモンスネーク<br>（Snake） | I | 3 | 40 | 敵<br>單體 | 軌跡<br>![[DIGO_EXE_範圍_軌跡.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|觸發]]</span> | 破格連動；從區域內的洞穴竄出巨蛇 | 木 |
| ミニボム<br>（MiniBomb） | ＊ | 2 | 50 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 前3落點；投彈至前方3格 | 無 |
| ブレイクハンマー<br>（Hammer） | T | 2 | 100 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|破格]]</span> | 鐵鎚粉碎前方 | 無 |
| パネルスチール<br>（PanlGrab） | ＊ | 2 | 10 | 地形格 | 敵前1格<br>![[DIGO_EXE_範圍_敵前1格.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|奪格]]</span> | 奪取1格敵方格子 | 無 |
| エリアスチール<br>（AreaGrab） | E | 2 | 10 | 地形格 | 敵前縱列<br>![[DIGO_EXE_範圍_敵前縱列.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|奪格]]</span> | 奪取敵陣最前一列 | 無 |
| リカバリー10<br>（Recov10） | ＊ | 1 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復10 | 無 |
| リカバリー30<br>（Recov30） | ＊ | 1 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復30 | 無 |
| リカバリー50<br>（Recov50） | ＊ | 1 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復50 | 無 |
| リカバリー80<br>（Recov80） | ＊ | 1 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復80 | 無 |
| パネルリターン<br>（Repair） | ＊ | 1 | — | 地形格 | 特效(未解) | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|修格]]</span> | 修復自身區域格子 | 無 |
| アタック+10<br>（Atk+10） | ＊ | 1 | ???? | 手牌 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|強化]]</span> | +10；選中的攻擊晶片+10 | 無 |
| ウッド+30<br>（Wood+30） | ＊ | 1 | ???? | 手牌 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|強化]]</span> | 木晶片+30；木屬性攻擊晶片+30 | 無 |

碼分佈：＊:15、H:4、P:4、I:3、E:2、T:2、攻擊卡名目均 58

## N1-FolderD（23 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| ソード<br>（Sword） | Y | 4 | 80 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；斬擊前方1格 | 無 |
| ワイドソード<br>（WideSwrd） | L | 4 | 80 | 敵<br>複數 | 寬斬<br>![[DIGO_EXE_範圍_寬斬.png\|110]] |  | 縱3；斬擊前方敵人範圍：3格 | 無 |
| パネルスチール<br>（PanlGrab） | ＊ | 2 | 10 | 地形格 | 敵前1格<br>![[DIGO_EXE_範圍_敵前1格.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|奪格]]</span> | 奪取1格敵方格子 | 無 |
| シングルボム<br>（SnglBomb） | T | 1 | 50 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 前3落點；投擲大型炸彈至3格外 | 無 |
| ホウガン<br>（CannBall） | P | 1 | 160 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 落點單格；破壞前方第3格 | 無 |
| フウアツケン<br>（AirSwrd） | R | 1 | 100 | 敵<br>複數 | 寬斬<br>![[DIGO_EXE_範圍_寬斬.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|擊退]]</span> | 寬幅劍附帶空中攻擊 | 無 |
| ショックウェーブ<br>（ShockWav） | D | 1 | 60 | 敵<br>複數 | 貫穿<br>![[DIGO_EXE_範圍_貫穿.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|地面波]]</span> | 衝擊波貫穿敵人 | 無 |
| ガッツパンチ<br>（GutPunch） | C | 1 | 80 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|擊退]]</span> | 拳擊將目標推開1格 | 無 |
| ダッシュアタック<br>（DashAtk） | Z | 1 | 90 | 敵<br>複數 | 貫穿<br>![[DIGO_EXE_範圍_貫穿.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|突進]]</span> | 衝刺穿越敵人 | 無 |
| バーニングボディ<br>（Burner） | Q | 1 | 130 | 敵<br>複數 | 自身周圍<br>![[DIGO_EXE_範圍_自身周圍.png\|110]] |  | 以火焰包覆自身 | 火 |
| ラットン1<br>（Ratton1） | A | 1 | 80 | 敵<br>單體 | 軌跡<br>![[DIGO_EXE_範圍_軌跡.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|追蹤]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|轉彎]]</span> | 沿地爬行、轉彎一次 | 無 |
| ブレイクハンマー<br>（Hammer） | G | 1 | 100 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|破格]]</span> | 鐵鎚粉碎前方 | 無 |
| ラビリング1<br>（ZapRing1） | M | 1 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|麻痺]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 電環攻擊、命中麻痺 | 電 |
| ヨーヨー1<br>（Yo-Yo1） | F | 1 | 40 | 敵<br>複數 | 橫向3格<br>![[DIGO_EXE_範圍_橫向3格.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|多擊]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|震盪]]</span> | 往返3格的溜溜球 | 無 |
| バンブーランス<br>（Lance） | H | 1 | 130 | 敵<br>複數 | 末列<br>![[DIGO_EXE_範圍_末列.png\|110]] |  | 長槍貫穿後排 | 木 |
| ブーメラン1<br>（Boomer1） | J | 1 | 60 | 敵<br>複數 | 軌跡<br>![[DIGO_EXE_範圍_軌跡.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|繞場]]</span> | 迴力鏢繞場一周 | 木 |
| プラズマボール1<br>（Plasma1） | B | 1 | 30 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 發動電擊攻擊 | 電 |
| エリアスチール<br>（AreaGrab） | ＊ | 1 | 10 | 地形格 | 敵前縱列<br>![[DIGO_EXE_範圍_敵前縱列.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|奪格]]</span> | 奪取敵陣最前一列 | 無 |
| トップウ<br>（Wind） | ＊ | 1 | 10 | 敵<br>複數 | 全場<br>![[DIGO_EXE_範圍_全場.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|位移]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|風壓]]</span> | WindBox向敵方區域吹風 | 無 |
| スイコミ<br>（Fan） | ＊ | 1 | 10 | 敵<br>複數 | 全場<br>![[DIGO_EXE_範圍_全場.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|位移]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|風壓]]</span> | 真空吸力拉扯敵人 | 無 |
| アタック+10<br>（Atk+10） | ＊ | 1 | ???? | 手牌 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|強化]]</span> | +10；選中的攻擊晶片+10 | 無 |
| フラッシュマン<br>（FlashMan） | F | 1 | 50 | 敵方 | 區域 | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|麻痺]]</span> | 閃光攻擊使敵人麻痺；閃光攻擊使敵人麻痺 | 電 |
| バブルマン<br>（BubblMan） | B | 1 | 20 | 敵方 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|多擊]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|連發]]</span> | 連發多發泡沫彈；連射多發水波彈 | 水 |

碼分佈：＊:6、L:4、Y:4、B:2、F:2、A:1、C:1、D:1、G:1、H:1、J:1、M:1、P:1、Q:1、R:1、T:1、Z:1、攻擊卡名目均 65

## FamousFolder（20 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| バッドスパイス1<br>（Spice1） | S | 3 | 80 | 敵<br>複數 | 特效(未解) |  | 草地連動；在所有草地灑下危險粉末 | 木 |
| ブーメラン1<br>（Boomer1） | F | 3 | 60 | 敵<br>複數 | 軌跡<br>![[DIGO_EXE_範圍_軌跡.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|繞場]]</span> | 迴力鏢繞場一周 | 木 |
| プラズマボール1<br>（Plasma1） | J | 3 | 30 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 發動電擊攻擊 | 電 |
| スチールゼリー1<br>（MetaGel1） | C | 3 | 90 | 敵<br>單體 | 軌跡<br>![[DIGO_EXE_範圍_軌跡.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|奪格]]</span> | 膠質攻擊奪取格子 | 水 |
| トルネード<br>（Tornado） | T | 2 | 20 | 敵<br>單體 | 前2單格<br>![[DIGO_EXE_範圍_前2單格.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|多擊]]</span> | 前方2格龍捲風連擊8次 | 無 |
| ラビリング1<br>（ZapRing1） | A | 2 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|麻痺]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 電環攻擊、命中麻痺 | 電 |
| バーニングボディ<br>（Burner） | Q | 1 | 130 | 敵<br>複數 | 自身周圍<br>![[DIGO_EXE_範圍_自身周圍.png\|110]] |  | 以火焰包覆自身 | 火 |
| マグマステージ<br>（LavaStge） | T | 1 | — | 地形格 | 全場<br>![[DIGO_EXE_範圍_全場.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|格變]]</span> | 將所有格子變為熔岩 | 無 |
| アイスステージ<br>（IceStage） | G | 1 | — | 地形格 | 全場<br>![[DIGO_EXE_範圍_全場.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|格變]]</span> | 將所有格子變為冰地 | 無 |
| クサムラステージ<br>（GrassStg） | ＊ | 1 | — | 地形格 | 全場<br>![[DIGO_EXE_範圍_全場.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|格變]]</span> | 將所有格子變為草地 | 無 |
| サンドステージ<br>（SandStge） | B | 1 | — | 地形格 | 全場<br>![[DIGO_EXE_範圍_全場.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|格變]]</span> | 將所有格子變為沙地 | 無 |
| ファイア+30<br>（Fire+30） | ＊ | 1 | ???? | 手牌 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|強化]]</span> | 火晶片+30；火屬性攻擊晶片+30 | 無 |
| アクア+30<br>（Aqua+30） | ＊ | 1 | ???? | 手牌 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|強化]]</span> | 水晶片+30；水屬性攻擊晶片+30 | 無 |
| エレキ+30<br>（Elec+30） | ＊ | 1 | ???? | 手牌 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|強化]]</span> | 電晶片+30；電屬性攻擊晶片+30 | 無 |
| ウッド+30<br>（Wood+30） | ＊ | 1 | ???? | 手牌 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|強化]]</span> | 木晶片+30；木屬性攻擊晶片+30 | 無 |
| フラッシュマン<br>（FlashMan） | F | 1 | 50 | 敵方 | 區域 | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|麻痺]]</span> | 閃光攻擊使敵人麻痺；閃光攻擊使敵人麻痺 | 電 |
| ビーストマン<br>（BeastMan） | B | 1 | 40 | 敵方 | 前縱3<br>![[DIGO_EXE_範圍_前縱3.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|突進]]</span> | 爪擊前方三格；爪擊前方3格 | 無 |
| バブルマン<br>（BubblMan） | B | 1 | 20 | 敵方 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|多擊]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|連發]]</span> | 連發多發泡沫彈；連射多發水波彈 | 水 |
| プラントマン<br>（PlantMan） | P | 1 | 20 | 敵<br>複數 | 全場<br>![[DIGO_EXE_範圍_全場.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|多擊]]</span> | 藤蔓傷害所有敵人；藤蔓傷害所有敵人 | 木 |
| フレイムマン<br>（FlamMan） | F | 1 | 120 | 敵<br>複數 | 全場<br>![[DIGO_EXE_範圍_全場.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|多擊]]</span> | 火焰燒傷所有敵人；火焰灼燒所有敵人 | 火 |

碼分佈：F:5、＊:5、B:3、C:3、J:3、S:3、T:3、A:2、G:1、P:1、Q:1、攻擊卡名目均 56

## ApprenticeFolder（18 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| エアシュート1<br>（AirShot1） | ＊ | 4 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|擊退]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 命中並擊退1格 | 無 |
| ガッツパンチ<br>（GutPunch） | D | 4 | 80 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|擊退]]</span> | 拳擊將目標推開1格 | 無 |
| ランダムメテオ<br>（RndmMetr） | S | 3 | 100 | 敵<br>複數 | 特效(未解) | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|多擊]]</span> | 隕石粉碎敵人 | 火 |
| プラズマボール1<br>（Plasma1） | J | 3 | 30 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 發動電擊攻擊 | 電 |
| ストーンキューブ<br>（RockCube） | ＊ | 3 | 100 | 指定格 | 設置<br>![[DIGO_EXE_範圍_設置.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|障礙]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|設置]]</span> | 在前方放置岩石方塊 | 無 |
| バブルショット<br>（Bubbler） | E | 1 | 60 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 命中後波及身後1格 | 水 |
| バブルブイ<br>（Bub-V） | E | 1 | 60 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點斜後2格；命中後波及斜後2格 | 水 |
| バブルサイド<br>（BublSide） | E | 1 | 60 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點上下2格；命中後波及上下2格 | 水 |
| ヒートショット<br>（HeatShot） | J | 1 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 命中後波及身後1格 | 火 |
| ヒートブイ<br>（Heat-V） | J | 1 | 40 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點斜後2格；命中後波及斜後2格 | 火 |
| ヒートサイド<br>（HeatSide） | J | 1 | 40 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點上下2格；命中後波及上下2格 | 火 |
| カウントボム<br>（TimeBomb） | K | 1 | 150 | 敵<br>複數 | 設置<br>![[DIGO_EXE_範圍_設置.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|設置]]</span> | 作用=區域倒數爆；全區域定時炸彈 | 無 |
| ステルスマイン<br>（Mine） | D | 1 | 300 | 指定格 | 設置<br>![[DIGO_EXE_範圍_設置.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|設置]]</span> | 踩雷；在敵方區域放置地雷 | 無 |
| プリズム<br>（Prism） | K | 1 | — | 指定格 | 設置<br>![[DIGO_EXE_範圍_設置.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|折射]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|設置]]</span> | 作用=隨機發射；稜鏡隨機發射 | 無 |
| プリズム<br>（Prism） | W | 1 | — | 指定格 | 設置<br>![[DIGO_EXE_範圍_設置.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|折射]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|設置]]</span> | 作用=隨機發射；稜鏡隨機發射 | 無 |
| メタルマン<br>（MetalMan） | M | 1 | 100 | 指定格 | 區域 | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|破格]]</span> | 鐵拳砸毀單一格；鐵拳粉碎1格 | 無 |
| メタルマンV2<br>（MetalMn V2） | M | 1 | 130 | 指定格 | 區域 | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|破格]]</span> | 鐵拳砸毀單一格；鐵拳粉碎1格 | 無 |
| メタルマンV3<br>（MetalMn V3） | M | 1 | 160 | 指定格 | 區域 | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|破格]]</span> | 鐵拳砸毀單一格；鐵拳粉碎1格 | 無 |

碼分佈：＊:7、J:6、D:5、E:3、M:3、S:3、K:2、W:1、攻擊卡名目均 80

## XtraFolder（9 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| キャノン<br>（Cannon） | A | 4 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |
| エアシュート1<br>（AirShot1） | ＊ | 4 | 20 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|擊退]]</span><br><span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 命中並擊退1格 | 無 |
| ショットガン<br>（ShotGun） | J | 4 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點後1格；命中後波及身後1格 | 無 |
| ブイガン<br>（V-Gun） | D | 4 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點斜後2格；命中後波及斜後2格 | 無 |
| サイドガン<br>（SideGun） | S | 4 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點上下2格；命中後波及上下2格 | 無 |
| ミニボム<br>（MiniBomb） | B | 4 | 50 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 前3落點；投彈至前方3格 | 無 |
| ソード<br>（Sword） | L | 4 | 80 | 敵<br>單體 | 近斬<br>![[DIGO_EXE_範圍_近斬.png\|110]] |  | 前1；斬擊前方1格 | 無 |
| ワイドソード<br>（WideSwrd） | L | 1 | 80 | 敵<br>複數 | 寬斬<br>![[DIGO_EXE_範圍_寬斬.png\|110]] |  | 縱3；斬擊前方敵人範圍：3格 | 無 |
| エリアスチール<br>（AreaGrab） | L | 1 | 10 | 地形格 | 敵前縱列<br>![[DIGO_EXE_範圍_敵前縱列.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|奪格]]</span> | 奪取敵陣最前一列 | 無 |

碼分佈：L:6、A:4、B:4、D:4、J:4、S:4、＊:4、攻擊卡名目均 40

## 未收錄夾一（教學／殘留）（5 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| キャノン<br>（Cannon） | A | 12 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |
| ショットガン<br>（ShotGun） | J | 6 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點後1格；命中後波及身後1格 | 無 |
| ミニボム<br>（MiniBomb） | B | 6 | 50 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 前3落點；投彈至前方3格 | 無 |
| ブイガン<br>（V-Gun） | P | 5 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點斜後2格；命中後波及斜後2格 | 無 |
| キャノン<br>（Cannon） | P | 1 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |

碼分佈：A:12、B:6、J:6、P:6、攻擊卡名目均 38

## 未收錄夾二（教學／殘留）（5 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| キャノン<br>（Cannon） | A | 6 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |
| ショットガン<br>（ShotGun） | J | 6 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點後1格；命中後波及身後1格 | 無 |
| ミニボム<br>（MiniBomb） | B | 6 | 50 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 前3落點；投彈至前方3格 | 無 |
| ワイドソード<br>（WideSwrd） | L | 6 | 80 | 敵<br>複數 | 寬斬<br>![[DIGO_EXE_範圍_寬斬.png\|110]] |  | 縱3；斬擊前方敵人範圍：3格 | 無 |
| エリアスチール<br>（AreaGrab） | L | 6 | 10 | 地形格 | 敵前縱列<br>![[DIGO_EXE_範圍_敵前縱列.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|奪格]]</span> | 奪取敵陣最前一列 | 無 |

碼分佈：L:12、A:6、B:6、J:6、攻擊卡名目均 42

## 未收錄夾三（教學／殘留）（8 種 30 張）

| 名稱 | 代碼 | 張數 | 傷害 | 對象 | 範圍 | 詞條 | 效果摘要 | 元素 |
|---|---|---|---|---|---|---|---|---|
| キャノン<br>（Cannon） | A | 5 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |
| ショットガン<br>（ShotGun） | J | 5 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點後1格；命中後波及身後1格 | 無 |
| ブイガン<br>（V-Gun） | P | 5 | 30 | 敵<br>單體 | 濺射<br>![[DIGO_EXE_範圍_濺射.png\|110]] |  | 命中點斜後2格；命中後波及斜後2格 | 無 |
| ミニボム<br>（MiniBomb） | B | 5 | 50 | 敵<br>單體 | 拋射<br>![[DIGO_EXE_範圍_拋射.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|投擲]]</span> | 前3落點；投彈至前方3格 | 無 |
| ワイドソード<br>（WideSwrd） | L | 5 | 80 | 敵<br>複數 | 寬斬<br>![[DIGO_EXE_範圍_寬斬.png\|110]] |  | 縱3；斬擊前方敵人範圍：3格 | 無 |
| キャノン<br>（Cannon） | B | 2 | 40 | 敵<br>單體 | 直線<br>![[DIGO_EXE_範圍_直線.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|單發]]</span> | 砲擊單一敵人 | 無 |
| リカバリー10<br>（Recov10） | L | 2 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復10 | 無 |
| リカバリー10<br>（Recov10） | A | 1 | — | 自身 | 自身<br>![[DIGO_EXE_範圍_自身.png\|110]] | <span style="white-space:nowrap">[[5_EXE3_效果範圍與詞條#詞條列表\|回復]]</span> | 回復10 | 無 |

碼分佈：B:7、L:7、A:6、J:5、P:5、攻擊卡名目均 46
