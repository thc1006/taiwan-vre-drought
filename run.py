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
    c = r["confound"]
    print("結論（誠實的否定）：備轉率對再生能源的相關看似很強，卻大半是會計恆等式。")
    print(f"  備轉率 ≡ (供給−負載)/負載 相關 {c['margin_is_identity']:+.2f}；"
          f"corr(供給, 再生) {c['supply_vs_renew']:+.2f}。")
    print(f"  去季節後化約為「備轉率追隨淨負載」（相關 {c['margin_vs_netload']:+.2f}），"
          f"是電網常識，不是因果發現。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
