"""產生圖表（英文標籤，避免缺字型；README 為中文）。"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def make_figures(d, r: dict, outdir="figures") -> list:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    tight = d.nsmallest(r["tight"]["n"], "margin")
    paths = []

    # ── Fig 1: reserve margin vs renewable output ───────────────────────────
    fig, ax = plt.subplots(figsize=(7.5, 5))
    sc = ax.scatter(d.renew, d.margin, c=d.load, cmap="coolwarm", s=18, alpha=.7,
                    edgecolors="none")
    ax.scatter(tight.renew, tight.margin, s=70, facecolors="none",
               edgecolors="black", linewidths=1.4,
               label=f"{r['tight']['n']} tightest-margin days")
    cb = fig.colorbar(sc); cb.set_label("Peak load (10 MW)")
    ax.set_xlabel("Renewable output  wind + solar  (10 MW)")
    ax.set_ylabel("Reserve margin (%)")
    ax.set_title(f"Taiwan grid is tightest on LOW-renewable days\n"
                 f"margin vs renewables r = {r['corr']['renew']:+.2f}   "
                 f"vs peak load r = {r['corr']['load']:+.2f}")
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout(); p = out / "fig1_margin_vs_renewables.png"
    fig.savefig(p, dpi=140); plt.close(fig); paths.append(p)

    # ── Fig 2: what drives the tightest days (supply vs demand) ─────────────
    t = r["tight"]; de = r["decompose"]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.6))
    cats = ["Reserve\nmargin (%)", "Renewables\n(10 MW)", "Peak load\n(10 MW)"]
    allv = [t["margin"][1], t["renew"][1], t["load"][1]]
    tigv = [t["margin"][0], t["renew"][0], t["load"][0]]
    x = np.arange(3)
    ax[0].bar(x - .2, allv, .4, label="All days", color="tab:gray")
    ax[0].bar(x + .2, tigv, .4, label="Tightest days", color="tab:red")
    ax[0].set_xticks(x); ax[0].set_xticklabels(cats)
    ax[0].set_title("Tightest days: renewables collapse,\nload barely rises")
    ax[0].legend(fontsize=9)
    # supply-gap attribution
    renew_share = de["renew_pct_of_supply_gap"]
    ax[1].bar(["Supply\nshortfall", "…from\nrenewables"],
              [de["supply_shortfall"], de["supply_shortfall"] * renew_share / 100],
              color=["tab:blue", "tab:green"])
    ax[1].set_ylabel("10 MW")
    ax[1].set_title(f"Supply shortfall on tight days is\n{renew_share:.0f}% renewable lull"
                    f"  (maintenance ruled out)")
    fig.tight_layout(); p = out / "fig2_supply_vs_demand.png"
    fig.savefig(p, dpi=140); plt.close(fig); paths.append(p)

    # ── Fig 3: monthly pattern ──────────────────────────────────────────────
    mc = d.groupby("month")[["margin", "renew"]].mean()
    fig, ax = plt.subplots(figsize=(8, 4.6))
    tight_by_month = tight.month.value_counts().reindex(range(1, 13), fill_value=0)
    ax.bar(mc.index, mc.margin, color="tab:blue", alpha=.6, label="Reserve margin (%)")
    for m, n in tight_by_month.items():
        if n:
            ax.annotate(f"{n} tight", (m, mc.margin.get(m, 0) + 0.4),
                        ha="center", fontsize=8, color="tab:red")
    ax.set_xlabel("Month"); ax.set_ylabel("Reserve margin (%)", color="tab:blue")
    ax2 = ax.twinx()
    ax2.plot(mc.index, mc.renew, "o-", color="tab:green", label="Renewables (10 MW)")
    ax2.set_ylabel("Renewable output (10 MW)", color="tab:green")
    ax.set_xticks(range(1, 13))
    ax.set_title("Tightest days cluster in autumn/winter (renewable lull),\nNOT the summer demand peak")
    fig.tight_layout(); p = out / "fig3_monthly.png"
    fig.savefig(p, dpi=140); plt.close(fig); paths.append(p)
    return paths
