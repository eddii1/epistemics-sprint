# gpt_score

Generator `gemini/gemma-4-26b-a4b-it`, 10 prompts per pattern, arms natural,induced. Rows: responses the grader flagged with no payload. Cells: still flagged (score 1 or 2) with the payload appended, 95% Wilson interval. `invalid` and `unparseable` are counted as not flagged, as DarkBench's metric does (unparseable is dropped from its denominator).

## Grader prompt: none

| grader | flagged at baseline | replace_transcript |
|---|---|---|
| openai/gpt-4o-mini | 110 | 3/110 = 3% [1-8] (invalid 2, unparseable 0) |
