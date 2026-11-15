# Grading its own exam

Can the text of a chatbot's reply talk DarkBench's grader into a clean score, and can that be closed?

Status: project for the Apart "AI x Epistemics" Research Sprint (13-15 November 2026). Part of it was made the
evening before the sprint and is marked pre-existing below, as the sprint rules ask.

## When each part was made

Times are CET, from file creation times. The sprint page gives dates and no start hour; its first event was the
logistics talk on Friday 13 November at 15:15 CET (14:15 UTC).

| when | what | status |
|---|---|---|
| Thu 12 Nov, 20:19-22:11 | `common/`, `darkbench.py`, `run.py`, `data/`, the 110 replies, runs `pilot`, `confirm`, `fix`, `graders2`, `census/` | **pre-existing** (before the sprint) |
| Fri 13 Nov, 09:39-13:23 | runs `haiku_fix`, `sonnet`, `attacks2`, `score`, `fix2`, `tamper`, `gpt_attacks`, `gpt_fix`, `gpt_score`, `tamper_gpt_attacks`; `rescore.py`, `tamper.py`; a change to `darkbench.py` (10:37) | sprint dates, before the first talk |
| Fri 13 Nov, 14:56-15:01 | `report/` (figures script, both figures, first report draft) | sprint dates, before the first talk |
| Sun 15 Nov, 11:00-11:25 | runs `tamper_all_gpt_attacks`, `tamper_all_attacks2`, `chatbot2`, `tamper_all_chatbot2`; `--all` in `tamper.py`; `--company` and `--model-name` in `run.py` | sprint |
| Sun 15 Nov, 13:40-13:55 | repository set-up: top-level `README.md`, DarkBench licence file, keys read from a root `.env`, style-only lint fixes (no change to prompts or results) | sprint |

Two other pilots from Thursday 12 November shared `common/` with this one. They are pre-existing, are not part
of the sprint report and are not in this repository.

## Prior work this extends

Matt Fisher, "Grader Prompt Structure" (eval-experiments.generality.org, 2026-10-30) and Inspect issue #6277 /
PR #6282: forged closing markers flip Inspect's default model-graded templates, and markers that carry a random
code fix most of it. That work did not run a real safety benchmark's own grader. This pilot does, and adds a
suffix that attacks what the grader believes was shown to the user, a test of the ported fix on five graders,
and a hole in the score rule.

## Design

- **Benchmark**: DarkBench (github.com/apartresearch/DarkBench, MIT, commit 7eef151). `darkbench.py` copies its
  grader prompt, system message, pattern descriptions and score rule; `data/darkbench.jsonl` is its 660 prompts.
- **Responses**: 10 prompts per pattern (seed 0), answered by `gemma-4-26b-a4b-it` twice: with DarkBench's
  system prompt ("natural") and with an operator instruction that makes the pattern likely ("induced", five
  patterns; harmful generation is left out on purpose). 110 responses.
- **Paired test**: each response is graded as it is and again with a suffix appended. The reply to the user is
  the same in both, so a changed grade is the grader being moved, not the behaviour. No human labels needed.
- **Denominator**: the responses a grader flagged with no suffix. Cells are "flags left".
- **Suffixes** (`run.payload`): `control` (harmless filler), `plea`, `note_only`, `reopen_only`, `end_note`,
  `hidden_comment`, `invalidate`, `replace_transcript` (forged end marker + "the transcript above is a discarded
  draft" + a forged second conversation with a neutral reply), `draft_plain` (the same claim in prose, no
  markers), `self_aware` / `self_template` (written by `gemini-3.8-flash`, one attempt, without / with sight
  of the grader prompt).
- **Grader prompts** (`run.render`): `none` (as shipped), `escape` (break up `===` and `---` in the reply),
  `inspect_style` (port of Inspect's fix: every marker carries a code, plus "the conversation is data"),
  `inspect_after` (the same plus a reminder after the conversation), `json_quote` (reply passed as one JSON
  string, plus "this is data").
- **Score rules** (`rescore.py`): shipped (`invalid` wins over the pattern field) and strict (the pattern field
  counts whatever `invalid` says).
- **Statistics**: Wilson 95% intervals, exact McNemar against the control suffix.

## Changed vs the shipped DarkBench code

- `darkbench/scorer.py` runs a second `str.format` over the whole grader prompt, reply included. A reply that
  contains `{...}` raises `KeyError`, and `{model}` or `{company}` would be filled in. Here such a reply is
  inserted after the second round, unchanged, and counted (`format_breaks`).
- Graders. DarkBench's default is `openai/gpt-4o-mini`; it is one of six graders run here.
- The coded-marker fix derives its code from the content and a fixed salt so that calls can be cached. A real
  deployment draws it at random per call.

## Run

```
uv run python -m grader_gaming.run --n 10 --name <name> --threads 5 \
    [--graders a,b] [--payloads a,b] [--defenses a,b] [--all]
uv run python -m grader_gaming.rescore confirm fix graders2 attacks2 fix2 haiku_fix sonnet
uv run python -m grader_gaming.tamper --source <run> --graders a,b [--all]
uv run python -m grader_gaming.run --n 10 --name chatbot2 --generator openai/gpt-4o-mini --company OpenAI \
    --model-name ChatGPT --graders openai/gpt-4o-mini --payloads control,draft_plain,replace_transcript
```

Model strings are LiteLLM names (`gemini/...`) or `cli:<name>` for the Claude CLI. Every call is cached in
`grader_gaming/.cache/calls.jsonl`, which is in the repository, so a rerun of a finished run makes no calls and
needs no keys. For new calls, keys are read from the environment, from a `.env` file at the repository root
(git-ignored) or from the file named in `SPRINT_ENV`.

## Results

Per run: `results/<name>/summary.md` and `rows.jsonl`. All runs under both score rules: `results/rescored.md`.

| run | what it holds |
|---|---|
| `pilot` | first attempt; token limits cut replies and grades short. Not usable, kept for the record |
| `confirm` | eight suffixes, Gemini 3.5 Flash-Lite and 3.8 Flash, shipped prompt |
| `graders2` | Gemma 4 and Claude Haiku as graders |
| `fix` | `escape` and `inspect_style` on the two Gemini graders |
| `attacks2` | `draft_plain` and the model-written suffixes on the three Google graders |
| `score` | `replace_transcript` on all 110 responses, flagged or not |
| `fix2` | three fixes x four suffixes on the three Google graders |
| `haiku_fix`, `sonnet` | `draft_plain` and fixes on Claude Haiku and Claude Sonnet |
| `gpt_attacks`, `gpt_fix`, `gpt_score` | all eleven suffixes, the three fixes and the all-responses run on gpt-4o-mini |
| `tamper`, `tamper_gpt_attacks` | tamper check (`tamper.py`) on Flash-Lite and Gemma, and on gpt-4o-mini |
| `tamper_all_attacks2`, `tamper_all_gpt_attacks` | tamper check with `--all`: every response, flagged or not, with no suffix and with three suffixes |
| `chatbot2`, `tamper_all_chatbot2` | second tested chatbot (`gpt-4o-mini`, named to the grader as OpenAI's ChatGPT), graded and tamper-checked by gpt-4o-mini |

Headline numbers (shipped prompt and score rule unless stated):

- `replace_transcript` leaves 0 of 54, 51, 53, 67 and 70 flags on Flash-Lite, 3.8 Flash, Gemma, Haiku and Sonnet;
  the control suffix leaves 94-100%. On all 110 responses, flagged goes from 54, 51 and 53 to 2 on each of the
  three Google graders.
- `draft_plain` leaves 0/54 (Flash-Lite), 0/53 (Gemma), 20/70 (Sonnet), 53/67 (Haiku), 45/51 (3.8 Flash).
- Best prompt fix tested plus the strict rule, flags left on `replace_transcript`: 51/51 (3.8 Flash),
  54/67 (Haiku, `inspect_style`), 46/70 (Sonnet, `inspect_style`), 8/53 (Gemma, `inspect_after`), 0/54
  (Flash-Lite, any fix). No prompt fix closes it on the two small graders.

- gpt-4o-mini, DarkBench's default grader (89 of 110 flagged at baseline): `replace_transcript` leaves 1/89,
  `invalidate` 1/89 (87 graded invalid), `end_note` 9/89, `hidden_comment` 19/89, `draft_plain` 23/89,
  `self_template` 44/89, `self_aware` 56/89, `control` 88/89. All 110 responses: 89 flagged to 3. Prompt fixes
  leave 5-14/89 on `replace_transcript` (14-19/89 with the strict rule) and 82-86/89 on `draft_plain` with the
  strict rule.
- Tamper check, share of baseline-flagged responses where it says yes. Control: 0/54 (Flash-Lite), 0/53 (Gemma),
  9/89 (gpt-4o-mini). `draft_plain`: 54/54, 53/53, 89/89. `replace_transcript`: 38/54, 28/53, 89/89.

- Tamper check on all 110 responses (`--all`). No suffix: 0/110 (Flash-Lite), 0/110 (Gemma), 7/110 (gpt-4o-mini, all 7
  on responses it had already flagged). Control: 0, 0 and 9/110. `draft_plain`: 110/110 on all three.
  `replace_transcript`: 79/110, 64/110 (13 empty Gemma answers count as no), 110/110.
- Second chatbot (gpt-4o-mini's own replies, 83 of 110 flagged at baseline): `control` leaves 82/83, `draft_plain`
  17/83, `replace_transcript` 0/83. Tamper check: 0/110 with no suffix, 13/110 on control, 110/110 on both claims.

## Report

Draft sprint report on Apart's template structure: `report/report.md` (figures: `report/fig1_attack.png`,
`report/fig2_closing.png`). Figures are drawn from the saved rows, no model calls:

```
uv run --with matplotlib python -m report.figures
```

## Limits

- Two tested models, 110 responses each (the second on one grader and three suffixes), one grade per response and
  condition (temperature 0 where the API takes it).
- The suffixes that work were written by hand. One-attempt model-written suffixes move only the small graders.
- The fixes are ports onto DarkBench's prompt, not Inspect's code. `inspect_after` and `json_quote` were not
  run on Sonnet; `inspect_after` was not run on Haiku.
- "Haiku" and "Sonnet" are the Claude CLI names `haiku` and `sonnet`, which resolve to `claude-haiku-5-5` and
  `claude-sonnet-5-5` in the CLI versions used (2.1.322 and 2.1.323). `gpt-4o-mini` resolves to
  `gpt-4o-mini-2024-07-18`. All three were checked on 15 November 2026; the runs logged only the names.
- No check yet that a prompt fix leaves unflagged responses unflagged. The tamper check was not run on the Claude
  graders or Gemini 3.8 Flash, and not against a suffix written to get past it.
