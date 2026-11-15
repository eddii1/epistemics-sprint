"""Figures for the report, drawn from the saved result rows. Makes no model calls.

    uv run --with matplotlib python -m report.figures

Writes report/fig1_attack.png and report/fig2_closing.png.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common.stats import wilson
from grader_gaming import darkbench as db

RESULTS = Path("grader_gaming/results")
RUNS = ["confirm", "fix", "graders2", "attacks2", "fix2", "haiku_fix", "sonnet", "gpt_attacks", "gpt_fix"]
GRADERS = [  # order: DarkBench's default first, then by how much of the plain-prose claim each one believes
    ("openai/gpt-4o-mini", "gpt-4o-mini\n(DarkBench default)"),
    ("gemini/gemini-3.5-flash-lite", "Gemini 3.5\nFlash-Lite"),
    ("gemini/gemma-4-26b-a4b-it", "Gemma 4\n26B"),
    ("cli:sonnet", "Claude\nSonnet"),
    ("cli:haiku", "Claude\nHaiku"),
    ("gemini/gemini-3.8-flash", "Gemini 3.8\nFlash"),
]
INK, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#e1e0d9", "#c3c2b7", "#fcfcfb"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]  # categorical slots 1-3, validated as a set
STEPS = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]  # one-hue ordinal ramp, validated with --ordinal


def load() -> dict:
    rows = {}
    for run in RUNS:
        for line in (RESULTS / run / "rows.jsonl").read_text().splitlines():
            r = json.loads(line)
            rows[(r["grader"], r["id"], r["arm"], r["payload"], r["defense"])] = r
    return rows


def flagged(r: dict, strict: bool = False) -> bool:
    if strict:
        return bool(db.pattern_present(r["raw"], r["issue"]))
    return (r["value"] or 0) > 0


def base_items(rows: dict, grader: str) -> list[tuple[str, str]]:
    return [(k[1], k[2]) for k, r in rows.items()
            if k[0] == grader and k[3] == "none" and k[4] == "none" and flagged(r)]


def left(rows: dict, grader: str, payload: str, defense: str = "none", strict: bool = False) -> tuple[int, int]:
    items = base_items(rows, grader)
    return sum(flagged(rows[(grader, i, a, payload, defense)], strict) for i, a in items), len(items)


def style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=0, labelsize=8, colors=MUTED)
    ax.set_ylim(0, 112)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])


def bars(ax, x: float, k: int, n: int, color: str, width: float, err: bool = True) -> None:
    pct = 100 * k / n
    ax.bar(x, pct, width=width * 0.92, color=color, linewidth=0)
    top = pct
    if err:
        lo, hi = wilson(k, n)
        ax.plot([x, x], [100 * lo, 100 * hi], color=INK, linewidth=0.8, alpha=0.55)
        top = 100 * hi
    ax.text(x, top + 1.5, str(k), ha="center", va="bottom", fontsize=7.5, color=INK)


def fig1(rows: dict) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.3), dpi=220, facecolor=SURFACE)
    style(ax)
    conds = [("control", "harmless filler (control)"), ("draft_plain", '"discarded draft" claim, plain prose'),
             ("replace_transcript", '"discarded draft" claim, forged markers')]
    w = 0.26
    ticks = []
    for gi, (g, label) in enumerate(GRADERS):
        n = len(base_items(rows, g))
        ticks.append(f"{label}\nn = {n}")
        for ci, (p, _) in enumerate(conds):
            k, n = left(rows, g, p)
            bars(ax, gi + (ci - 1) * w, k, n, SERIES[ci], w)
    ax.set_xticks(range(len(GRADERS)))
    ax.set_xticklabels(ticks, color=INK)
    ax.set_ylabel("flags left, % of replies flagged with no suffix", fontsize=8, color=MUTED)
    handles = [plt.Rectangle((0, 0), 1, 1, color=SERIES[i]) for i in range(3)]
    ax.legend(handles, [c[1] for c in conds], loc="upper center", bbox_to_anchor=(0.5, 1.17), ncol=3,
              frameon=False, fontsize=8, labelcolor=INK, handlelength=1.1, columnspacing=1.6)
    fig.tight_layout()
    fig.savefig("report/fig1_attack.png", facecolor=SURFACE)


def fig2(rows: dict) -> None:
    tam = {}
    for run in ("tamper", "tamper_gpt_attacks"):
        for line in (RESULTS / run / "rows.jsonl").read_text().splitlines():
            r = json.loads(line)
            tam[(r["grader"], r["id"], r["arm"], r["payload"])] = r["tamper"] == 1
    graders = GRADERS[:3]
    steps = ["shipped prompt and score rule", "coded markers", "coded markers + changed score rule",
             "shipped prompt + tamper check"]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.5), dpi=220, facecolor=SURFACE, sharey=True)
    w = 0.2
    for ax, (p, title) in zip(axes, [("replace_transcript", "(a) forged-marker draft claim"),
                                     ("draft_plain", "(b) plain-prose draft claim")]):
        style(ax)
        for gi, (g, _) in enumerate(graders):
            items = base_items(rows, g)
            n = len(items)
            vals = [left(rows, g, p)[0], left(rows, g, p, "inspect_style")[0],
                    left(rows, g, p, "inspect_style", strict=True)[0],
                    sum(flagged(rows[(g, i, a, p, "none")]) or tam[(g, i, a, p)] for i, a in items)]
            for si, k in enumerate(vals):
                bars(ax, gi + (si - 1.5) * w, k, n, STEPS[si], w, err=False)
        ax.set_xticks(range(len(graders)))
        ax.set_xticklabels([f"{lab}\nn = {len(base_items(rows, g))}" for g, lab in graders], color=INK)
        ax.set_title(title, fontsize=8.5, color=INK, loc="left", pad=6)
    axes[0].set_ylabel("flags left, % of replies flagged with no suffix", fontsize=8, color=MUTED)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in STEPS]
    fig.legend(handles, steps, loc="upper center", ncol=2, frameon=False, fontsize=8, labelcolor=INK,
               handlelength=1.1, columnspacing=2.0, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig("report/fig2_closing.png", facecolor=SURFACE)


if __name__ == "__main__":
    data = load()
    fig1(data)
    fig2(data)
    print("wrote report/fig1_attack.png, report/fig2_closing.png")
