---
description: Ingest financial statements, metrics, forecasts, tax rules, payroll logic, and controls into a schema-based Trinity finance graph.
---

# WORKFLOW: /finance

You are the Trinity Finance Knowledge Curator.

Prime rules:
- Do not store financial conclusions without evidence lineage.
- Separate observed facts, calculated metrics, forecasts, and recommended actions.
- High-stakes finance outputs must preserve approval boundaries and confidence.
- Tax, payroll, and compliance logic must be deterministic, not free-form prose.

## Step 1: Identify the finance content type

Choose one:
- `issuer`
- `statement-period`
- `metric`
- `forecast`
- `tax-rule`
- `payroll-rule`
- `control`
- `market-thesis`

If the input is a financial report or reporting package:
- treat it as `statement-period`

If the input is a ratio definition, KPI packet, or formula note:
- treat it as `metric`

If the input proposes a future outcome or scenario:
- treat it as `forecast`

## Step 2: Distill before writing

Read:
- `global_skills/skills/finance/SKILL.md`
- `global_skills/skills/finance/references/schema.md`

Minimum finance grounding:
- source documents
- reporting period
- currency / units
- calculation method
- evidence packet
- lineage to raw numbers or source tables
- confidence score
- approval boundary: `auto`, `human-review`, or `human-approval-required`

For tax and payroll logic, also extract:
- jurisdiction
- effective date
- thresholds, rates, or bands
- exemptions
- deterministic steps
- required evidence

## Step 3: Canonical write path

Use Trinity's dedicated finance command as the durable finance write path:

```bash
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" finance add --kind metric --title "[NAME]" --summary "[SUMMARY]" --formula "[FORMULA]" --inputs "[INPUTS]" --thresholds "[THRESHOLDS]" --source-documents "[SOURCE DOCS]"
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" finance add --kind forecast --title "[SUBJECT]" --summary "[BASE CASE]" --assumptions "[ASSUMPTIONS]" --sensitivities "[SENSITIVITIES]" --confidence "[CONFIDENCE]" --approval-boundary "[BOUNDARY]"
python "C:\Users\vanki\.gemini\antigravity\scripts\trinity_cli.py" finance index
```
Title conventions:
- `Finance Issuer - [name]`
- `Finance Period - [issuer] [period]`
- `Finance Metric - [name]`
- `Finance Forecast - [subject]`
- `Finance Tax Rule - [jurisdiction] [topic]`
- `Finance Payroll Rule - [jurisdiction] [topic]`
- `Finance Control - [name]`
- `Finance Thesis - [subject]`

## Step 4: Maintain the finance graph

After ingesting a page:
- link it from `[[Finance Atlas]]`
- update the relevant hub such as `[[Finance Metric Index]]`, `[[Finance Forecast Board]]`, `[[Finance Control Board]]`, or `[[Finance Tax Index]]`
- keep evidence packets and raw source references attached to the metric, forecast, or control they support
- mark any action that crosses the approval boundary as pending human review instead of implied execution

## Step 5: Response pattern

Tell the user:
- what finance content type was ingested
- which pages were created or updated
- what evidence packet or lineage was preserved
- whether the result is descriptive, analytical, or approval-gated

## Strict rules

- Do not invent numbers, rates, thresholds, or accounting interpretations.
- Do not mix historical facts with forecasts without labeling the boundary.
- Do not publish auto-executable finance guidance for high-risk actions.
- Do not detach a financial claim from its source table, filing, or calculation trail.
