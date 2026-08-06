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

FIELDS = ["cargo_estimado", "tamanho_empresa", "intencao_compra", "sugestao_abordagem"]

FALLBACK = {field: "N/A" for field in FIELDS}

PROMPT_TEMPLATE = """Analise este lead de marketing e responda em JSON:
Nome: {nome}
Email: {email}
Empresa: {empresa}

Chaves esperadas:
- cargo_estimado
- tamanho_empresa (Startup, Pequena, Media, Grande)
- intencao_compra (Quente, Morno, Frio)
- sugestao_abordagem (uma frase curta e especifica pra abordar essa pessoa)

Responda apenas o JSON, sem texto adicional."""


def enrich_lead(nome, email, empresa, retries=2):
    prompt = PROMPT_TEMPLATE.format(nome=nome, email=email, empresa=empresa)
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
                print(f"Falha ao processar {nome}: {exc}")
                return dict(FALLBACK)
            time.sleep(2 * (attempt + 1))


def run(input_path, output_path):
    try:
        df = pd.read_csv(input_path, encoding="utf-8")
    except FileNotFoundError:
        print(f"{input_path} nao encontrado. Colunas esperadas: nome, email, empresa.")
        return

    print(f"Processando {len(df)} leads via {GEMINI_MODEL}...")

    backup_path = output_path.replace(".csv", "_backup.csv")
    for index, row in df.iterrows():
        dados = enrich_lead(row["nome"], row["email"], row["empresa"])
        for field in FIELDS:
            df.loc[index, field] = dados.get(field, FALLBACK[field])
        df.to_csv(backup_path, index=False, encoding="utf-8-sig")
        time.sleep(1)

    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    counts = Counter(df["intencao_compra"])
    print(f"\nConcluido: {output_path}")
    print("Distribuicao de intencao de compra:")
    for intencao, total in counts.most_common():
        print(f"  {intencao}: {total}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enriquece leads (nome, email, empresa) via Gemini API.")
    parser.add_argument("--input", default="leads.csv")
    parser.add_argument("--output", default="leads_enriched.csv")
    args = parser.parse_args()
    run(args.input, args.output)
