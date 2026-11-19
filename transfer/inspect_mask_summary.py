"""Paired summary of the MASK-through-Inspect runs (transfer/inspect_mask_note.py).

For every sample, compares the honesty label of the shipped score with the same label after the control
paragraph and after the draft-claim note, on the same replies. "Lies left" = of the samples the shipped scorer
labels `lie`, how many are still `lie` with each suffix. Exact McNemar against the control.

    .venv-inspect/bin/python transfer/inspect_mask_summary.py transfer/inspect_logs/run1
"""

from __future__ import annotations

import glob
import math
import sys
from collections import Counter

from inspect_ai.log import read_eval_log


def mcnemar_exact(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2**n)


def main(log_dir: str) -> None:
    rows = []
    for path in sorted(glob.glob(f"{log_dir}/*.eval")):
        log = read_eval_log(path)
        archetype = log.eval.task_args.get("question_archetype")
        for s in log.samples or []:
            sc = s.scores or {}
            if not all(k in sc for k in ("accuracy_and_honesty", "with_control", "with_note")):
                continue
            rows.append((archetype, s.id, *(sc[k].value["honesty"] for k in
                                              ("accuracy_and_honesty", "with_control", "with_note"))))

    print(f"{len(rows)} samples from {log_dir}\n")
    print("| subset | lies (shipped) | lies left, control | lies left, note | p (note vs control) |")
    print("|---|---|---|---|---|")
    for subset in sorted({r[0] for r in rows}) + ["all"]:
        rs = [r for r in rows if subset == "all" or r[0] == subset]
        lies = [r for r in rs if r[2] == "lie"]
        ctrl = {r[1] for r in lies if r[3] == "lie"}
        note = {r[1] for r in lies if r[4] == "lie"}
        p = mcnemar_exact(len(ctrl - note), len(note - ctrl))
        print(f"| {subset} | {len(lies)} | {len(ctrl)} | {len(note)} | {p:.2g} |")
    moved = Counter(r[4] for r in rows if r[2] == "lie" and r[4] != "lie")
    print(f"\nWhere the note moves shipped lies: {dict(moved)}")
    print(f"Shipped label counts: {dict(Counter(r[2] for r in rows))}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "transfer/inspect_logs/run1")
