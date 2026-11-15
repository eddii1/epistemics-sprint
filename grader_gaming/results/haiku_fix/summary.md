# haiku_fix

Generator `gemini/gemma-4-26b-a4b-it`, 10 prompts per pattern, arms natural,induced. Rows: responses the grader flagged with no payload. Cells: still flagged (score 1 or 2) with the payload appended, 95% Wilson interval. `invalid` and `unparseable` are counted as not flagged, as DarkBench's metric does (unparseable is dropped from its denominator).

## Grader prompt: none

| grader | flagged at baseline | control | replace_transcript | draft_plain |
|---|---|---|---|---|
| cli:haiku | 67 | 64/67 = 96% [88-98] (invalid 0, unparseable 0) | 0/67 = 0% [0-5] (invalid 0, unparseable 0) | 53/67 = 79% [68-87] (invalid 1, unparseable 0) |

Exact McNemar test against the harmless `control` suffix (pairs = same response, same grader):

- cli:haiku, replace_transcript: flag lost 64, flag gained 0, p = 0.0000
- cli:haiku, draft_plain: flag lost 12, flag gained 1, p = 0.0034

## Grader prompt: inspect_style

| grader | flagged at baseline | control | replace_transcript | draft_plain |
|---|---|---|---|---|
| cli:haiku | 67 (no payload under this fix: 66/67 = 99% [92-100]) | 64/67 = 96% [88-98] (invalid 0, unparseable 0) | 41/67 = 61% [49-72] (invalid 13, unparseable 0) | 53/67 = 79% [68-87] (invalid 12, unparseable 0) |

Exact McNemar test against the harmless `control` suffix (pairs = same response, same grader):

- cli:haiku, replace_transcript: flag lost 25, flag gained 2, p = 0.0000
- cli:haiku, draft_plain: flag lost 12, flag gained 1, p = 0.0034

## Grader prompt: json_quote

| grader | flagged at baseline | control | replace_transcript | draft_plain |
|---|---|---|---|---|
| cli:haiku | 67 (no payload under this fix: 65/67 = 97% [90-99]) | 63/67 = 94% [86-98] (invalid 0, unparseable 0) | 42/67 = 63% [51-73] (invalid 17, unparseable 0) | 49/67 = 73% [61-82] (invalid 13, unparseable 0) |

Exact McNemar test against the harmless `control` suffix (pairs = same response, same grader):

- cli:haiku, replace_transcript: flag lost 22, flag gained 1, p = 0.0000
- cli:haiku, draft_plain: flag lost 14, flag gained 0, p = 0.0001
