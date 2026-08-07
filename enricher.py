import argparse
import json
import os
import time
from collections import Counter

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

FIELDS = ["estimated_title", "company_size", "buying_intent", "outreach_angle"]

FALLBACK = {field: "N/A" for field in FIELDS}

PROMPT_TEMPLATE = """Analyze this marketing lead and respond in JSON:
Name: {name}
Email: {email}
Company: {company}

Expected keys:
- estimated_title
- company_size (Startup, Small, Medium, Large)
- buying_intent (Hot, Warm, Cold)
- outreach_angle (a short, specific line to open a conversation with this person)

Respond with JSON only, no extra text."""


def enrich_lead(name, email, company, retries=2):
    prompt = PROMPT_TEMPLATE.format(name=name, email=email, company=company)
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 200},
    }

    for attempt in range(retries + 1):
        try:
            resp = requests.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                json=body,
                timeout=30,
            )
            resp.raise_for_status()
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            text = text.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(text)
        except Exception as exc:
            if attempt == retries:
                print(f"Failed to process {name}: {exc}")
                return dict(FALLBACK)
            time.sleep(2 * (attempt + 1))


def run(input_path, output_path):
    try:
        df = pd.read_csv(input_path, encoding="utf-8")
    except FileNotFoundError:
        print(f"{input_path} not found. Expected columns: name, email, company.")
        return

    print(f"Processing {len(df)} leads via {GEMINI_MODEL}...")

    backup_path = output_path.replace(".csv", "_backup.csv")
    for index, row in df.iterrows():
        data = enrich_lead(row["name"], row["email"], row["company"])
        for field in FIELDS:
            df.loc[index, field] = data.get(field, FALLBACK[field])
        # per-row checkpoint so a crash mid-run doesn't lose already-processed leads
        df.to_csv(backup_path, index=False, encoding="utf-8-sig")
        time.sleep(1)

    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    counts = Counter(df["buying_intent"])
    print(f"\nDone: {output_path}")
    print("Buying intent distribution:")
    for intent, total in counts.most_common():
        print(f"  {intent}: {total}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enrich leads (name, email, company) via the Gemini API.")
    parser.add_argument("--input", default="leads.csv")
    parser.add_argument("--output", default="leads_enriched.csv")
    args = parser.parse_args()
    run(args.input, args.output)
