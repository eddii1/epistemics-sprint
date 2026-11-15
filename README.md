# Grading its own exam

Can text appended to a chatbot's reply talk an LLM grader into a clean score? This repository tests that on
[DarkBench](https://github.com/apartresearch/DarkBench), a benchmark for manipulative behaviour in chatbots, and
tests what closes it.

Project for the Apart Research "AI x Epistemics" Research Sprint (13-15 November 2026). Single author: Eduard
Tudoran.

## Finding in short

- A suffix that fakes the end of the conversation and claims the reply above was a discarded draft removes
  99-100% of DarkBench's flags on six graders. On the default grader, `gpt-4o-mini`, flagged replies fall from 89
  of 110 to 3. A harmless suffix removes at most 6%.
- Rewriting the grader prompt, including a port of Inspect's fix for forged markers, fully restores the flags on
  one grader of six.
- A second question to the grader, whether the reply contains text addressed to a grader, restores all 89 flags
  on `gpt-4o-mini`, with false alarms on 6% of untouched replies. It catches 53-70% on two small graders.

The full account, with methods, tables and limits, is in [`report/report.md`](report/report.md).

## Pre-existing work

Part of this was made on Thursday 12 November, the evening before the sprint dates, and is pre-existing work:
the set-up, the DarkBench port, `run.py`, the 110 replies, the runs `pilot`, `confirm`, `fix` and `graders2`, and
the census. The table in [`grader_gaming/README.md`](grader_gaming/README.md#when-each-part-was-made) lists what
was made when, from file creation times. The repository itself was created on Sunday 15 November, so the commit
dates do not show this.

Not original to this project: DarkBench's prompts, grader prompt and score rule (MIT, commit `7eef151`, licence
in [`grader_gaming/data/LICENSE-DarkBench`](grader_gaming/data/LICENSE-DarkBench)), and the coded-marker fix,
which is a port of the one in Inspect PR #6282.

## Layout

| path | what |
|---|---|
| `grader_gaming/` | the experiment (`run.py`), re-scoring (`rescore.py`), tamper check (`tamper.py`), DarkBench port, data, results per run, call cache |
| `common/` | one cached model-call function and the statistics helpers |
| `census/` | which model-graded evals in `inspect_evals` paste the reply into the grader prompt the same way |
| `report/` | the report and the script that draws its figures |
| `upstream/` | a patch for DarkBench's own scorer (crash bug and score rule), ready to send |

## Reproduce

```
uv sync
uv run python -m grader_gaming.run --n 10 --name chatbot2 --generator openai/gpt-4o-mini --company OpenAI \
    --model-name ChatGPT --graders openai/gpt-4o-mini --payloads control,draft_plain,replace_transcript
uv run --with matplotlib python -m report.figures
```

Every model call of the report's runs is in `grader_gaming/.cache/calls.jsonl`, so rerunning a finished run
makes no calls and needs no API keys. All commands and the list of runs are in
[`grader_gaming/README.md`](grader_gaming/README.md).
