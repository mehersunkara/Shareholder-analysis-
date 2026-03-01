"""
Shareholder Ownership Analysis
================================
Analyses institutional shareholding data to identify ownership concentration,
flag unusual position changes, and visualise trends across a company register.

Author: Meher Sunkara
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ── Styling ──────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor":   "#161b22",
    "axes.edgecolor":   "#30363d",
    "axes.labelcolor":  "#c9d1d9",
    "xtick.color":      "#8b949e",
    "ytick.color":      "#8b949e",
    "text.color":       "#c9d1d9",
    "grid.color":       "#21262d",
    "grid.linestyle":   "--",
    "grid.alpha":       0.6,
    "font.family":      "monospace",
})

ACCENT   = "#58a6ff"
POSITIVE = "#3fb950"
NEGATIVE = "#f85149"
WARNING  = "#d29922"

# ── Simulate realistic shareholder register ───────────────────────────────────
np.random.seed(42)

institutions = [
    "BlackRock Inc.",
    "Vanguard Group",
    "State Street Corp",
    "Fidelity Investments",
    "Capital Research",
    "Wellington Mgmt",
    "Invesco Ltd",
    "Legal & General",
    "Aviva Investors",
    "Schroders plc",
    "JP Morgan AM",
    "Norges Bank",
    "Government of Singapore",
    "Dimensional Fund Advisors",
    "T. Rowe Price",
]

total_shares = 500_000_000  # 500M shares in issue

# Current holdings (% of total shares)
current_pct = np.array([
    8.72, 7.45, 5.31, 4.88, 3.94,
    3.21, 2.87, 2.65, 2.41, 2.18,
    1.95, 1.74, 1.52, 1.31, 1.12,
])
current_shares = (current_pct / 100 * total_shares).astype(int)

# Previous period holdings (simulate changes)
change_pct = np.array([
    0.00, +0.45, -0.23, +1.12, -0.67,
    0.00, +0.34, -0.18, +0.55, -0.41,
    +0.28, -0.15, +0.63, -0.09, +0.22,
])
previous_pct = current_pct - change_pct
previous_shares = (previous_pct / 100 * total_shares).astype(int)
change_shares = current_shares - previous_shares

# Market value (assume £4.85 share price)
share_price = 4.85
market_value = current_shares * share_price

df = pd.DataFrame({
    "Institution":       institutions,
    "Current Shares":    current_shares,
    "Previous Shares":   previous_shares,
    "Change (Shares)":   change_shares,
    "Current %":         current_pct,
    "Previous %":        previous_pct,
    "Change (%)":        change_pct,
    "Market Value (£)":  market_value,
})

# Flag significant changes (threshold: ±0.5%)
df["Flag"] = df["Change (%)"].abs() >= 0.5

# ── Analysis Functions ─────────────────────────────────────────────────────────
def ownership_concentration(df):
    """Herfindahl-Hirschman Index — measures ownership concentration."""
    pct_array = df["Current %"].values
    hhi = np.sum(pct_array ** 2)
    return round(hhi, 2)

def top_n_concentration(df, n=5):
    return round(df.nlargest(n, "Current %")["Current %"].sum(), 2)

# ── Print Summary ──────────────────────────────────────────────────────────────
print("=" * 65)
print("  SHAREHOLDER OWNERSHIP ANALYSIS REPORT")
print(f"  Generated: {datetime.today().strftime('%d %B %Y')}")
print("=" * 65)
print(f"\n  Company:          ACME Financial PLC")
print(f"  Total Shares:     {total_shares:,.0f}")
print(f"  Share Price:      £{share_price:.2f}")
print(f"  Market Cap:       £{total_shares * share_price / 1e9:.2f}bn")
print(f"\n  Top 5 Concentration:  {top_n_concentration(df, 5)}%")
print(f"  Top 10 Concentration: {top_n_concentration(df, 10)}%")
print(f"  HHI Score:            {ownership_concentration(df)}")
print(f"\n  ⚠  Flagged changes (≥ ±0.5%): {df['Flag'].sum()} institutions")

print("\n" + "-" * 65)
print(f"  {'Institution':<28} {'Current %':>10} {'Change %':>10} {'Flag':>6}")
print("-" * 65)
for _, row in df.iterrows():
    flag = "🔴" if row["Flag"] and row["Change (%)"] < 0 else \
           "🟢" if row["Flag"] and row["Change (%)"] > 0 else "  "
    chg  = f"{row['Change (%)']:+.2f}%"
    print(f"  {row['Institution']:<28} {row['Current %']:>9.2f}%  {chg:>9}  {flag}")
print("=" * 65)

# ── Plot 1: Top 15 Holders Bar Chart ──────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle("Shareholder Ownership Analysis — ACME Financial PLC",
             fontsize=15, fontweight="bold", color="#e6edf3", y=0.98)

ax1 = axes[0, 0]
colors = [POSITIVE if c > 0 else NEGATIVE if c < 0 else ACCENT
          for c in df["Change (%)"]]
bars = ax1.barh(df["Institution"][::-1], df["Current %"][::-1],
                color=ACCENT, alpha=0.85, height=0.6)
ax1.set_xlabel("Shareholding (%)")
ax1.set_title("Top 15 Institutional Holders", color="#e6edf3", pad=10)
ax1.axvline(x=5, color=WARNING, linestyle="--", alpha=0.7, linewidth=1)
ax1.text(5.1, 0.5, "5% threshold", color=WARNING, fontsize=7, va="bottom")
ax1.grid(axis="x")
for bar, val in zip(bars, df["Current %"][::-1]):
    ax1.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
             f"{val:.2f}%", va="center", fontsize=7.5, color="#8b949e")

# ── Plot 2: Period-on-Period Changes ──────────────────────────────────────────
ax2 = axes[0, 1]
change_colors = [POSITIVE if c > 0 else NEGATIVE if c < 0 else "#484f58"
                 for c in df["Change (%)"]]
ax2.barh(df["Institution"][::-1], df["Change (%)"][::-1],
         color=change_colors[::-1], alpha=0.85, height=0.6)
ax2.set_xlabel("Change in Shareholding (%)")
ax2.set_title("Period-on-Period Changes", color="#e6edf3", pad=10)
ax2.axvline(x=0, color="#8b949e", linewidth=0.8)
ax2.axvline(x=0.5,  color=WARNING, linestyle=":", alpha=0.5, linewidth=1)
ax2.axvline(x=-0.5, color=WARNING, linestyle=":", alpha=0.5, linewidth=1)
ax2.grid(axis="x")

# ── Plot 3: Ownership Concentration Pie ───────────────────────────────────────
ax3 = axes[1, 0]
top5_pct  = top_n_concentration(df, 5)
top10_pct = top_n_concentration(df, 10)
rest_pct  = 100 - df["Current %"].sum()
sizes  = [top5_pct, top10_pct - top5_pct,
          df["Current %"].sum() - top10_pct, rest_pct]
labels = ["Top 5", "6th–10th", "11th–15th", "Other"]
pie_colors = [ACCENT, "#388bfd", "#1f6feb", "#0d419d"]
wedges, texts, autotexts = ax3.pie(
    sizes, labels=labels, colors=pie_colors,
    autopct="%1.1f%%", startangle=90,
    wedgeprops={"edgecolor": "#0d1117", "linewidth": 2},
    textprops={"color": "#c9d1d9", "fontsize": 9},
)
for at in autotexts:
    at.set_color("#e6edf3")
    at.set_fontsize(8)
ax3.set_title("Ownership Concentration", color="#e6edf3", pad=10)

# ── Plot 4: Market Value of Top 10 ────────────────────────────────────────────
ax4 = axes[1, 1]
top10 = df.nlargest(10, "Market Value (£)")
mv_millions = top10["Market Value (£)"] / 1e6
bars4 = ax4.bar(range(len(top10)), mv_millions,
                color=ACCENT, alpha=0.85, width=0.6)
ax4.set_xticks(range(len(top10)))
ax4.set_xticklabels(
    [n.split()[0] for n in top10["Institution"]],
    rotation=35, ha="right", fontsize=8
)
ax4.set_ylabel("Market Value (£m)")
ax4.set_title("Market Value of Top 10 Holdings", color="#e6edf3", pad=10)
ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:.0f}m"))
ax4.grid(axis="y")
for bar, val in zip(bars4, mv_millions):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"£{val:.0f}m", ha="center", fontsize=7.5, color="#8b949e")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("/mnt/user-data/outputs/shareholder_analysis_output.png",
            dpi=150, bbox_inches="tight", facecolor="#0d1117")
plt.close()
print("\n  ✅ Chart saved: shareholder_analysis_output.png")
