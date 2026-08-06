# Lead Enricher AI

Script que pega uma lista crua de leads (nome, email, empresa) e devolve cada
um qualificado: cargo provável, porte da empresa, temperatura de compra e uma
sugestão de abordagem específica para aquele contato.

Motivação: em prospecção manual, qualificar lead a lead consome tempo que
deveria ir pra abordagem em si. Esse script terceiriza a etapa de pesquisa
inicial pro modelo, e devolve uma tabela pronta pra priorizar quem abordar
primeiro.

## Uso

```bash
pip install -r requirements.txt
cp .env.example .env   # cole sua GEMINI_API_KEY (gratuita em aistudio.google.com/apikey)
python enricher.py --input leads.csv --output leads_enriched.csv
```

Saída: `leads_enriched.csv` com as colunas originais + `cargo_estimado`,
`tamanho_empresa`, `intencao_compra`, `sugestao_abordagem`, mais um resumo no
terminal da distribuição de temperatura dos leads processados.

## Por que Gemini

Camada gratuita permanente, sem cartão de crédito. Pra um script de
prospecção rodado em lote, isso importa mais que ganhos marginais de
qualidade de um modelo pago.
