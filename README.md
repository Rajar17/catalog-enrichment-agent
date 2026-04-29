HP Laptop Catalog Enrichment Agent

An AI agentic POC that transforms raw HP laptop product entries into fully
enriched catalog listings using Claude claude-sonnet-4-6.

as an open-source contribution to the Gen AI community.

## What it does

| Input | Output |
|-------|--------|
| Model number + name | SEO-optimised title |
| Raw spec string | Marketing description |
| (optional) image URL | Structured key specs |
| | Category path |
| | Search tags |
| | Use case mapping |
| | Completeness score |

## Architecture

```
Raw product input
      │
      ▼
Orchestrator Agent (Claude claude-sonnet-4-6)
      │
   ┌──┴──────────────────┐
   ▼                      ▼                      ▼
analyze_product_specs  web_research_tool    generate_use_case_tags
   │                      │                      │
   └──────────────────────┴──────────────────────┘
                          │
                          ▼
               generate_seo_metadata
                          │
                          ▼
               Enriched catalog JSON
```

## Quickstart

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3a. Run the CLI agent
python main.py

# 3b. Run the Streamlit demo UI
streamlit run streamlit_app.py

# 3c. Run the FastAPI backend
uvicorn api:app --reload
# → POST http://localhost:8000/enrich
```

## API usage

```bash
curl -X POST http://localhost:8000/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "name": "HP Laptop 15s-eq2144AU",
    "model_number": "15s-eq2144AU",
    "raw_specs": "AMD Ryzen 5, 8GB, 512GB"
  }'
```

## Project structure

```
catalog-agent/
├── agents/
│   └── enrichment_agent.py   # Core agentic loop + tool implementations
├── data/
│   └── sample_products.py    # Demo HP laptop products
├── output/                   # Enriched JSON saved here
├── main.py                   # CLI runner
├── api.py                    # FastAPI backend
├── streamlit_app.py          # Demo UI
└── requirements.txt
```

## Extending to production

- Replace `analyze_product_specs` stub with real HP Product API calls
- Add a `scrape_product_page` tool using BeautifulSoup or Playwright
- Add multimodal image analysis using Claude's vision capability
- Connect to your PIM/ERP via a write-back tool
- Deploy to Hugging Face Spaces for public demo

## Contributing

This project is open-source under MIT license.
Contributions welcome — open an issue or PR on GitHub.
