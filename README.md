# Lead Enricher AI

Built solo with AI-assisted development to solve a real prospecting
bottleneck fast, not a software engineering exercise. Takes a raw list of
leads (name, email, company) and returns each one qualified: likely job
title, company size, buying intent, and a specific outreach angle for that
contact.

Why: in manual prospecting, qualifying leads one by one eats time that
should go into the actual outreach. This tool offloads that research step
to the model and returns a ready-to-prioritize table, going from raw list
to ready-to-work output in one run.

## Usage

```bash
pip install -r requirements.txt
cp .env.example .env   # paste your GEMINI_API_KEY (free tier at aistudio.google.com/apikey)
python enricher.py --input leads.csv --output leads_enriched.csv
```

Output: `leads_enriched.csv` with the original columns plus `cargo_estimado`
(job title), `tamanho_empresa` (company size), `intencao_compra` (buying
intent), `sugestao_abordagem` (outreach angle), plus a terminal summary of
intent distribution across the processed leads.

## Why Gemini

Permanent free tier, no credit card. For a batch prospecting script, that
matters more than marginal quality gains from a paid model.
