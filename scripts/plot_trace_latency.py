"""Recreate the SVG from the recorded per-prompt trace medians."""
import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main():
    with (ROOT / "docs/data/trace-latency.csv").open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))

    metrics = [
        ("median_total_seconds", "Total request", "#2563EB", -0.17),
        ("median_first_model_ttft_seconds", "First model call to first token", "#0F766E", 0.17),
    ]
    y = list(range(len(rows)))
    plt.rcParams.update({"svg.hashsalt": "trace-latency", "font.size": 11, "axes.labelcolor": "#334155",
                        "text.color": "#0F172A", "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(9, 3.65), layout="constrained")
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")
    ax.set_axisbelow(True)
    ax.grid(axis="x", color="#CBD5E1", linewidth=0.7)
    for field, label, color, shift in metrics:
        bars = ax.barh([index + shift for index in y], [float(row[field]) for row in rows],
                       height=0.28, label=label, color=color)
        ax.bar_label(bars, fmt="%.2f", padding=5)
    ax.set_yticks(y, [f"{row['prompt']} (n={row['trace_count']})" for row in rows])
    ax.invert_yaxis()
    ax.set_xlim(0, 12.5)
    ax.set_xlabel("Median time (seconds)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.24), frameon=False, ncols=2)
    fig.suptitle("Observed LangSmith latency by prompt", x=0.04, ha="left", fontsize=19, weight="bold")
    ax.set_title("Tagged Windows traces with local Qwen 3.5 4B", loc="left", fontsize=11, color="#475569")
    fig.savefig(ROOT / "docs/assets/trace-latency.svg", metadata={"Date": None})


if __name__ == "__main__":
    main()
