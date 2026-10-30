# Claim extraction rules (give this file to every extractor agent)

You split documents into atomic, checkable claims. You do NOT judge truth, search the web, or edit the documents.

## Output
One JSONL file per document. One JSON object per line. `#` lines are comments; start with one header comment (what the file is, extraction date).
Allowed keys: `id, file, line, exact_text, claim_type, depends_on, cited_source, severity, scope, notes`. Validate with:
`python -X utf8 <skill>/scripts/ledger.py add --ledger <ledger.csv> --check <file.jsonl>`

## Fields
- `id`: `PREFIX-###` (prefix given in your assignment), sequential.
- `file`, `line`: path as given; integer line number.
- `exact_text`: verbatim excerpt ≤220 characters from that line. Never paraphrase. Keep the original language.
- `claim_type`:
  - `EXTERNAL_FACT` about the world (market data, companies, specs, rules, prices, dates, people and titles)
  - `CALCULATION` a number derived from other numbers (totals, margins, conversions, date arithmetic, scores)
  - `INTERNAL_FACT` about the team, the brief, what the client/company said or wrote, what another file says
  - `ASSUMPTION` stated as an estimate ("ocena", ESTIMATE, ~, "we assume")
  - `STRATEGY_OPINION` a judgment or recommendation; put the facts it rests on in `depends_on`
  - `QUOTE` attributed to a real person or organisation
- `depends_on`: comma-separated ids of claims in the same batch this one relies on (calculation inputs; facts an opinion rests on).
- `cited_source`: exactly what the document gives as its source (URL, tag, "rep", "[est]") or `none`. Do not resolve tags.
- `severity`: `CRITICAL` only for what the conclusion rests on or what will be shown as a key fact: the headline claim, key numbers (prices, margins, lead times, capacities, tariff rates, delivery dates), named target companies and named people with titles. Aim for at most about a third of the rows. `HIGH` for other facts and calculations; `MEDIUM` for background.
- `scope` (optional): e.g. `market` vs `client-internal`, when the material will later be shared with different audiences.
- `notes`: hedges, contradictions inside the document, numbers without units or dates, two values for one quantity.

## Atomicity
- One checkable statement per row. "Revenue EUR 365M, up 25%" = two rows. "1 GW campus, construction from Q3 2026" = two rows.
- Table rows with several factual cells give several rows. Implicit claims count: rankings, chart labels, captions, "this proves X", "the strongest sign".
- Cover the whole document; report skipped line ranges.

## Example rows
{"id":"ANS-019","file":"ANSWERS.md","line":35,"exact_text":"3 of 5 main transformers went in as temporary units [fact, Mortenson]","claim_type":"EXTERNAL_FACT","cited_source":"mortenson.com/projects/abilene-data-center-development","severity":"CRITICAL"}
{"id":"ANS-082","file":"ANSWERS.md","line":76,"exact_text":"Etra to a Texas pad: 24 + ~3 months shipping ≈ 27 months [est]","claim_type":"CALCULATION","depends_on":"ANS-009,ANS-083","cited_source":"[est]","severity":"CRITICAL"}

## When done
Reply with: rows per file, counts per claim_type, skipped ranges, and anything odd (contradictions, unsourced numbers, two values for one quantity). No verdicts.
