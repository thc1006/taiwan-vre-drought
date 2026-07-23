"""端到端：抓台電開放資料 → 分析 → 出圖與報告。

    uv run run.py          # 或 python run.py
"""
from __future__ import annotations

from fetch import fetch_all
from analyze import load_supply_demand, analyze, print_report
from make_figures import make_figures


def main() -> int:
    print("抓取台電開放資料 …")
    paths = fetch_all()
    d = load_supply_demand(paths["supply_demand"])
    print(f"  每日供需 {len(d)} 天\n")

    r = analyze(d)
    print_report(r)

    figs = make_figures(d, r)
    print("\n圖已輸出：")
    for p in figs:
        print(f"  {p}")

    # 一句話結論
    print("\n" + "=" * 60)
    cm = r["conditional_margin"]
    print("結論：台灣電網最吃緊的日子由『再生能源低谷』主導，非尖峰需求。")
    print(f"  只高載 {cm['high_load_only']}% vs 只低再生 {cm['low_renew_only']}%"
          f"（一般日 {cm['all']}%）—— 低再生壓得更低。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
