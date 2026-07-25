# 貢獻指南 · Contributing

這是一份誠實的否定結果，也是這個系列裡第一個、最像教科書的混淆案例。歡迎你來挑戰它。

## 最歡迎的兩種貢獻

- **戳破稽核**：如果你覺得「會計恆等式」的論證、去季節的做法，或「化約為淨負載」的推論有漏洞，
  或這個相關其實有超出定義的因果成分，請告訴我。這正是本專案的重點。
- **更好的資料**：尖峰時刻的分項出力、更長的序列，都能讓這題問得更清楚。

## 跑起來

```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt
python run.py
```

全程免金鑰、免登入。台電資料自 data.gov.tw 動態取得並快取。

## 幾點約定

- 改動分析時，請一併說明它如何影響結論，並盡量附上可重現的數字。
- 不要為了讓結果變顯著而事後挑門檻或子樣本；若要做探索性分析，請明確標示。
- 程式風格對齊現有檔案；中文排版遵循
  [中文文案排版指北](https://github.com/sparanoid/chinese-copywriting-guidelines)。
- 想先討論就開一個 [issue](https://github.com/thc1006/taiwan-vre-drought/issues)。

這是一個由一人維護的小型研究專案，回覆可能需要一點時間，先謝謝你的耐心。
參與本專案即表示你同意遵守[行為準則](CODE_OF_CONDUCT.md)。
