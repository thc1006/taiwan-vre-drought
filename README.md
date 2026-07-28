# 台灣電網最吃緊的日子，是「再生能源低谷」還是一條會計恆等式？

天真的答案很漂亮：備轉容量率最低（最吃緊）的日子和再生能源低谷相關（r = +0.51），和尖峰負載
幾乎無關（r = −0.12），還集中在秋冬、與夏季尖峰脫鉤。真正的答案是：這個相關大半是會計恆等式，
不是因果。

![margin vs renewables](figures/fig1_margin_vs_renewables.png)

## 為什麼這是假的：會計恆等式

- 備轉率的定義就是 (供給 − 負載) / 負載。本資料裡 `corr(備轉率, (供給−負載)/負載) = +1.00` —— 不是巧合，是定義本身。
- 再生能源本來就是「供給」的組成：`corr(供給, 再生) = +0.77`。「再生低則備轉低」有一大半只是加減法。
- 去季節後，備轉率對負載的相關掉到 −0.03；對「淨負載（負載 − 再生）」的相關是 −0.57，遠強於對毛負載的 −0.12。整件事化約為「備轉率追隨淨負載」，是電網教科書常識。

它甚至撐過了「歲修」檢驗（吃緊日是供給短而非需求高，供給缺口 113% 由再生能源解釋），看似不是
歲修就是再生低谷 —— 但那條線最後還是死在會計恆等式上。唯一站得住的弱結論：毛需求尖峰預測不了
吃緊日（因為在高再生時代供給和需求會一起動），所以吃緊日和夏季尖峰脫鉤。這是描述性的，不是
因果宣稱。`analyze.py` 第 ⑥ 段把這條稽核攤開可重跑。

## 怎麼跑

```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt
python run.py          # 抓資料、分析、混淆稽核、出圖
```

免金鑰、免登入；台電資料自 [data.gov.tw](https://data.gov.tw) 動態取得並快取。

## 資料來源（全開放）

台電每日供需與備轉率（[19995](https://data.gov.tw/dataset/19995) + [24945](https://data.gov.tw/dataset/24945)）。
天真分析的細節、歲修排除與誠實限制見 [NOTES.md](NOTES.md)。

## 本系列

同一套混淆稽核工法，套用在不同題目上，四個誠實的案例、四種不同的推論失敗：

- [taiwan-solar-dimming](https://github.com/thc1006/taiwan-solar-dimming) — 光電 × 氣膠，季節同步
- [taiwan-earthquake-fab](https://github.com/thc1006/taiwan-earthquake-fab) — 地震 × 晶圓廠，檢定力不足、測不到
- [taiwan-riverbed-dust](https://github.com/thc1006/taiwan-riverbed-dust) — 河床揚塵 × PM10，順風向空間梯度
- **taiwan-vre-drought**（本專案）— 電網備轉 × 再生能源，會計恆等式

稽核清單見 [CONFOUND-AUDIT.md](CONFOUND-AUDIT.md)。
