"""
Tenarai Catalog Enrichment Agent — Runner
Run: python main.py
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.enrichment_agent import enrich_catalog
from data.sample_products import SAMPLE_PRODUCTS


def print_enriched(result: dict):
    e = result.get("enriched")
    if not e:
        print(f"  [FAILED] {result['input']['name']} — {result.get('status')}")
        return

    print(f"\n{'─'*60}")
    print(f"  Product : {result['input']['name']}")
    print(f"  Title   : {e.get('enriched_title', '—')}")
    print(f"  Category: {e.get('category_path', '—')}")
    print(f"  Score   : {e.get('completeness_score', '—')}%")
    print(f"  Tags    : {', '.join(e.get('search_tags', [])[:6])}")
    print(f"  Uses    : {', '.join(e.get('use_cases', [])[:4])}")
    print(f"  SEO     : {e.get('meta_description', '—')[:100]}...")
    print(f"{'─'*60}")


def main():
    print("\n╔══════════════════════════════════════════════════╗")
    print("║   Tenarai — HP Laptop Catalog Enrichment Agent  ║")
    print("╚══════════════════════════════════════════════════╝")

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n[ERROR] ANTHROPIC_API_KEY not set.")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    print(f"\nProcessing {len(SAMPLE_PRODUCTS)} products...\n")

    results = enrich_catalog(SAMPLE_PRODUCTS)

    print("\n\n══════════ ENRICHMENT RESULTS ══════════")
    for r in results:
        print_enriched(r)

    # Save output
    out_path = Path("output/enriched_catalog.json")
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\n[Saved] {out_path}")

    success = sum(1 for r in results if r["status"] == "success")
    print(f"\n[Summary] {success}/{len(results)} products enriched successfully.\n")


if __name__ == "__main__":
    main()
