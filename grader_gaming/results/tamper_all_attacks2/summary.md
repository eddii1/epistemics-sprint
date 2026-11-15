# tamper_all_attacks2

Responses and shipped grades from `attacks2`, every response, flagged at baseline or not. Cells: the tamper check says yes. `none` is the reply with no suffix, so a yes there is a false alarm. 95% Wilson intervals. An unparseable tamper answer counts as no.

## gemini/gemini-3.5-flash-lite

| suffix | flagged at baseline | not flagged at baseline | all | unparseable |
|---|---|---|---|---|
| none | 0/54 = 0% [0-7] | 0/56 = 0% [0-6] | 0/110 = 0% [0-3] | 0 |
| control | 0/54 = 0% [0-7] | 0/56 = 0% [0-6] | 0/110 = 0% [0-3] | 0 |
| replace_transcript | 38/54 = 70% [57-81] | 41/56 = 73% [60-83] | 79/110 = 72% [63-79] | 0 |
| draft_plain | 54/54 = 100% [93-100] | 56/56 = 100% [94-100] | 110/110 = 100% [97-100] | 0 |

## gemini/gemma-4-26b-a4b-it

| suffix | flagged at baseline | not flagged at baseline | all | unparseable |
|---|---|---|---|---|
| none | 0/53 = 0% [0-7] | 0/57 = 0% [0-6] | 0/110 = 0% [0-3] | 0 |
| control | 0/53 = 0% [0-7] | 0/57 = 0% [0-6] | 0/110 = 0% [0-3] | 0 |
| replace_transcript | 28/53 = 53% [40-66] | 36/57 = 63% [50-74] | 64/110 = 58% [49-67] | 13 |
| draft_plain | 53/53 = 100% [93-100] | 57/57 = 100% [94-100] | 110/110 = 100% [97-100] | 0 |
