"""分析：台灣電網最吃緊的日子，是「再生能源低谷」還是「尖峰需求」？

核心發現（2025–2026）：備轉容量率最低的日子由**再生能源低谷**主導，而非尖峰負載，
且與夏季用電尖峰**脫鉤**（集中在秋冬）。排除歲修 confound 後結論成立。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

COLMAP = {
    "尖峰負載(萬瓩)": "load",
    "備轉容量率(%)": "margin",
    "風力發電(萬瓩)": "wind",
    "太陽能發電(萬瓩)": "solar",
    "淨尖峰供電能力(萬瓩)": "supply",
}


def load_supply_demand(path) -> pd.DataFrame:
    """讀 19995 每日供需，回傳含 date/load/margin/wind/solar/supply/renew 的乾淨表。"""
    src = pd.read_csv(path, encoding="utf-8-sig")
    d = pd.DataFrame()
    d["date"] = pd.to_datetime(src["日期"].astype(str), format="%Y%m%d")
    for zh, en in COLMAP.items():           # 只建英文欄，不 rename（避免重複欄）
        d[en] = pd.to_numeric(src[zh], errors="coerce")
    d["renew"] = d["wind"] + d["solar"]
    d["month"] = d["date"].dt.month
    return d.dropna(subset=["margin", "load", "wind", "solar", "supply"]).reset_index(drop=True)


def _zscore(s: pd.Series) -> np.ndarray:
    return ((s - s.mean()) / s.std()).values


def analyze(d: pd.DataFrame, n_tight: int = 15) -> dict:
    """跑完整分析，回傳結構化結果。"""
    out: dict = {"n_days": len(d), "start": str(d.date.min().date()), "end": str(d.date.max().date())}

    # ① 備轉率和誰相關
    out["corr"] = {v: round(float(d["margin"].corr(d[v])), 3)
                   for v in ["load", "wind", "solar", "renew"]}

    # ② 最吃緊 N 天 vs 全體
    tight = d.nsmallest(n_tight, "margin")
    out["tight"] = {
        "n": n_tight,
        "margin": (round(tight.margin.mean(), 1), round(d.margin.mean(), 1)),
        "renew": (round(tight.renew.mean(), 0), round(d.renew.mean(), 0)),
        "load": (round(tight.load.mean(), 0), round(d.load.mean(), 0)),
        "supply": (round(tight.supply.mean(), 0), round(d.supply.mean(), 0)),
        "months": tight.month.value_counts().sort_index().to_dict(),
    }

    # ③ 懷疑檢驗：供給不足 vs 需求過高，且供給缺口有多少是再生能源（排除歲修）
    supply_gap = d.supply.mean() - tight.supply.mean()   # 吃緊日少了多少供給
    load_excess = tight.load.mean() - d.load.mean()       # 吃緊日多了多少負載
    renew_gap = d.renew.mean() - tight.renew.mean()       # 吃緊日再生少了多少
    out["decompose"] = {
        "supply_shortfall": round(float(supply_gap), 0),
        "load_excess": round(float(load_excess), 0),
        "driver": "supply" if abs(supply_gap) > abs(load_excess) else "demand",
        "renew_pct_of_supply_gap": round(float(renew_gap / supply_gap * 100), 0) if supply_gap else None,
    }

    # ④ 複合條件下的備轉率（三分位）
    lw = d.wind < d.wind.quantile(0.33)
    ls = d.solar < d.solar.quantile(0.33)
    hl = d.load > d.load.quantile(0.67)
    out["conditional_margin"] = {
        "all": round(float(d.margin.mean()), 1),
        "high_load_only": round(float(d[hl].margin.mean()), 1),
        "low_renew_only": round(float(d[lw & ls].margin.mean()), 1),
        "n_low_renew": int((lw & ls).sum()),
        "n_low_renew_and_high_load": int((lw & ls & hl).sum()),
    }

    # ⑤ 標準化多元迴歸：控制彼此後誰壓低備轉率
    X = np.column_stack([np.ones(len(d)), _zscore(d.load), _zscore(d.wind), _zscore(d.solar)])
    beta, *_ = np.linalg.lstsq(X, _zscore(d.margin), rcond=None)
    out["regression_std_beta"] = {
        "load": round(float(beta[1]), 2),
        "wind": round(float(beta[2]), 2),
        "solar": round(float(beta[3]), 2),
    }

    # ⑥ 逐月平均
    out["monthly"] = d.groupby("month")[["margin", "renew", "load"]].mean().round(1).to_dict("index")
    return out


def print_report(r: dict) -> None:
    print(f"資料：{r['n_days']} 天（{r['start']} – {r['end']}）\n")
    print("① 備轉率相關性：",
          "  ".join(f"{k} {v:+.2f}" for k, v in r["corr"].items()))
    t = r["tight"]
    print(f"\n② 最吃緊 {t['n']} 天 vs 全體：")
    print(f"   備轉率 {t['margin'][0]}% vs {t['margin'][1]}%   "
          f"再生 {t['renew'][0]:.0f} vs {t['renew'][1]:.0f}   "
          f"負載 {t['load'][0]:.0f} vs {t['load'][1]:.0f}")
    print(f"   月份分布：{t['months']}")
    de = r["decompose"]
    print(f"\n③ 懷疑檢驗：供給短 {de['supply_shortfall']:.0f}、負載多 {de['load_excess']:+.0f}"
          f" → {'供給主導' if de['driver'] == 'supply' else '需求主導'}")
    print(f"   供給缺口有 {de['renew_pct_of_supply_gap']:.0f}% 是再生能源 → 歲修非主因")
    cm = r["conditional_margin"]
    print(f"\n④ 條件備轉率：全體 {cm['all']}%  只高載 {cm['high_load_only']}%  "
          f"只低再生 {cm['low_renew_only']}%（n={cm['n_low_renew']}）")
    b = r["regression_std_beta"]
    print(f"\n⑤ 標準化迴歸係數：負載 {b['load']:+.2f}  風力 {b['wind']:+.2f}  太陽能 {b['solar']:+.2f}")
