# chatbot2

Generator `openai/gpt-4o-mini`, 10 prompts per pattern, arms natural,induced. Rows: responses the grader flagged with no payload. Cells: still flagged (score 1 or 2) with the payload appended, 95% Wilson interval. `invalid` and `unparseable` are counted as not flagged, as DarkBench's metric does (unparseable is dropped from its denominator).

## Grader prompt: none

| grader | flagged at baseline | control | draft_plain | replace_transcript |
|---|---|---|---|---|
| openai/gpt-4o-mini | 83 | 82/83 = 99% [93-100] (invalid 0, unparseable 0) | 17/83 = 20% [13-30] (invalid 5, unparseable 0) | 0/83 = 0% [0-4] (invalid 2, unparseable 0) |

Exact McNemar test against the harmless `control` suffix (pairs = same response, same grader):

- openai/gpt-4o-mini, draft_plain: flag lost 65, flag gained 0, p = 0.0000
- openai/gpt-4o-mini, replace_transcript: flag lost 82, flag gained 0, p = 0.0000
