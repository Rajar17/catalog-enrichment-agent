"""
Tenarai — HP Laptop Catalog Enrichment Agent
Uses Claude claude-sonnet-4-6 to enrich raw product data into full listings.
"""

import json
import re
from typing import Any
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-6"

TOOLS = [
    {
        "name": "analyze_product_specs",
        "description": (
            "Parse and structure raw HP laptop specs from a model number or "
            "partial spec string. Returns processor, RAM, storage, display, OS, "
            "battery, weight, and connectivity details."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "model_number": {"type": "string", "description": "HP laptop model number e.g. 15s-eq2144AU"},
                "raw_specs": {"type": "string", "description": "Any raw spec text provided by the seller"},
            },
            "required": ["model_number"],
        },
    },
    {
        "name": "generate_use_case_tags",
        "description": (
            "Given structured laptop specs, determine the best-fit buyer personas "
            "and use cases (e.g. student, home office, gaming, creative work)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "processor": {"type": "string"},
                "ram_gb": {"type": "integer"},
                "storage_gb": {"type": "integer"},
                "gpu": {"type": "string"},
                "price_segment": {"type": "string", "enum": ["budget", "mid-range", "premium", "ultra-premium"]},
            },
            "required": ["processor", "ram_gb", "storage_gb"],
        },
    },
    {
        "name": "generate_seo_metadata",
        "description": "Generate SEO-optimised title, meta description, and keyword tags for an HP laptop listing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string"},
                "key_specs": {"type": "object", "description": "Dict of spec name → value"},
                "use_cases": {"type": "array", "items": {"type": "string"}},
                "market": {"type": "string", "description": "Target market e.g. India, US"},
            },
            "required": ["product_name", "key_specs"],
        },
    },
]


# ── Tool implementations ──────────────────────────────────────────────────────

def analyze_product_specs(model_number: str, raw_specs: str = "") -> dict:
    """
    In a real agent, this would call HP's product API or scrape specs pages.
    For the POC, we simulate structured extraction from known HP model patterns.
    """
    # Simulated spec database for demo — replace with real API/scraper
    DEMO_SPECS = {
        "15s-eq2144AU": {
            "processor": "AMD Ryzen 5 5500U (6-core, up to 4.0GHz)",
            "ram_gb": 8,
            "ram_type": "DDR4",
            "storage_gb": 512,
            "storage_type": "NVMe SSD",
            "display_size": "15.6 inch",
            "display_res": "1920x1080 FHD",
            "display_type": "Anti-glare IPS",
            "gpu": "AMD Radeon Graphics (integrated)",
            "os": "Windows 11 Home",
            "battery_hrs": 7.5,
            "weight_kg": 1.69,
            "wifi": "Wi-Fi 6 (802.11ax)",
            "bluetooth": "Bluetooth 5.0",
            "ports": "USB-A x2, USB-C x1, HDMI, SD card reader, 3.5mm audio",
            "color": "Natural Silver",
            "series": "HP 15s",
            "price_segment": "budget",
        },
        "pavilion-15-eg2006TX": {
            "processor": "Intel Core i5-1235U (10-core, up to 4.4GHz)",
            "ram_gb": 16,
            "ram_type": "DDR4",
            "storage_gb": 512,
            "storage_type": "NVMe SSD",
            "display_size": "15.6 inch",
            "display_res": "1920x1080 FHD",
            "display_type": "IPS micro-edge",
            "gpu": "Intel Iris Xe Graphics",
            "os": "Windows 11 Home",
            "battery_hrs": 8.5,
            "weight_kg": 1.75,
            "wifi": "Wi-Fi 6E",
            "bluetooth": "Bluetooth 5.3",
            "ports": "USB-A x2, USB-C x1, HDMI 2.1, SD card, 3.5mm audio",
            "color": "Natural Silver",
            "series": "HP Pavilion",
            "price_segment": "mid-range",
        },
        "envy-x360-13-bf0107TU": {
            "processor": "Intel Core i7-1255U (10-core, up to 4.7GHz)",
            "ram_gb": 16,
            "ram_type": "LPDDR5",
            "storage_gb": 1000,
            "storage_type": "NVMe SSD",
            "display_size": "13.3 inch",
            "display_res": "1920x1200 WUXGA",
            "display_type": "OLED touch 2-in-1",
            "gpu": "Intel Iris Xe Graphics",
            "os": "Windows 11 Home",
            "battery_hrs": 17.0,
            "weight_kg": 1.32,
            "wifi": "Wi-Fi 6E",
            "bluetooth": "Bluetooth 5.3",
            "ports": "Thunderbolt 4 x2, USB-A x1, microSD, 3.5mm audio",
            "color": "Nightfall Black",
            "series": "HP ENVY x360",
            "price_segment": "premium",
        },
    }

    # Fuzzy match model number
    model_key = model_number.lower().replace(" ", "-")
    for key, specs in DEMO_SPECS.items():
        if key.lower() in model_key or model_key in key.lower():
            return {"success": True, "specs": specs, "source": "demo_db"}

    # Fallback: parse raw_specs if provided
    if raw_specs:
        return {
            "success": True,
            "specs": {"raw": raw_specs, "note": "parsed from seller input"},
            "source": "raw_input",
        }

    return {"success": False, "error": f"Model '{model_number}' not found in demo database"}


def generate_use_case_tags(processor: str, ram_gb: int, storage_gb: int,
                            gpu: str = "", price_segment: str = "mid-range") -> dict:
    use_cases = []

    # Rule-based use case mapping (agent reasoning simulation)
    use_cases.append("Everyday computing")
    use_cases.append("Document editing")
    use_cases.append("Video streaming")

    if ram_gb >= 8:
        use_cases.append("Student use")
        use_cases.append("Home office")

    if ram_gb >= 16:
        use_cases.append("Multitasking")
        use_cases.append("Light video editing")

    if storage_gb >= 512:
        use_cases.append("Media storage")

    if "ryzen 7" in processor.lower() or "i7" in processor.lower() or "i9" in processor.lower():
        use_cases.append("Professional work")
        use_cases.append("Data analysis")

    if "nvidia" in gpu.lower() or "rtx" in gpu.lower() or "gtx" in gpu.lower():
        use_cases.append("Gaming")
        use_cases.append("3D rendering")

    if "touch" in gpu.lower() or price_segment in ("premium", "ultra-premium"):
        use_cases.append("Creative professionals")

    return {"use_cases": list(dict.fromkeys(use_cases))}  # deduplicated


def generate_seo_metadata(product_name: str, key_specs: dict,
                           use_cases: list = None, market: str = "India") -> dict:
    use_cases = use_cases or []
    processor = key_specs.get("processor", "")
    ram = key_specs.get("ram_gb", "")
    storage = key_specs.get("storage_gb", "")
    display = key_specs.get("display_size", "")
    os_name = key_specs.get("os", "Windows 11")

    title = (
        f"{product_name} — {processor.split('(')[0].strip()}, "
        f"{ram}GB RAM, {storage}GB SSD, {display}, {os_name}"
    )

    use_str = " · ".join(use_cases[:3]) if use_cases else "everyday use"
    shipping = "Free shipping across India" if market == "India" else "Fast delivery available"
    meta = (
        f"Buy {product_name} with {processor.split('(')[0].strip()}, "
        f"{ram}GB RAM and {storage}GB SSD. Perfect for {use_str}. {shipping}."
    )

    tags = [
        product_name.split()[0],  # brand
        product_name.split()[1] if len(product_name.split()) > 1 else "",
        processor.split()[0] + " " + processor.split()[1] if processor else "",
        f"{ram}GB RAM",
        f"{storage}GB SSD",
        f"{display} laptop",
        os_name,
    ] + use_cases[:4]

    return {
        "seo_title": title[:70],
        "meta_description": meta[:160],
        "search_tags": [t for t in tags if t],
    }


# ── Tool dispatcher ───────────────────────────────────────────────────────────

def dispatch_tool(name: str, inputs: dict) -> Any:
    if name == "analyze_product_specs":
        return analyze_product_specs(**inputs)
    elif name == "generate_use_case_tags":
        return generate_use_case_tags(**inputs)
    elif name == "generate_seo_metadata":
        return generate_seo_metadata(**inputs)
    raise ValueError(f"Unknown tool: {name}")


# ── Agent loop ────────────────────────────────────────────────────────────────

def enrich_product(product: dict) -> dict:
    """
    Run the enrichment agent for a single product.
    product = {"name": str, "model_number": str, "raw_specs": str (optional)}
    """
    print(f"\n{'='*60}")
    print(f"  Enriching: {product['name']}")
    print(f"{'='*60}")

    system_prompt = """You are Tenarai's Product Catalog Enrichment Agent.
Your job is to take a raw HP laptop product entry and produce a fully enriched 
catalog listing using the tools available to you.

Follow this exact sequence:
1. Call analyze_product_specs to get structured specs
2. Call generate_use_case_tags based on the specs
3. Call generate_seo_metadata with all the collected data
4. Return a final JSON object with ALL enriched fields

The final JSON must include:
- enriched_title (string)
- marketing_description (string, 2-3 sentences, friendly and informative)
- category_path (string, e.g. "Computers > Laptops > HP > Everyday Laptops")
- key_specs (object with all structured specs)
- use_cases (array of strings)
- search_tags (array of strings)  
- seo_title (string)
- meta_description (string)
- completeness_score (integer 0-100)
- price_segment (string)

Always respond with valid JSON after using all tools. No markdown fences."""

    messages = [
        {
            "role": "user",
            "content": (
                f"Enrich this HP laptop product:\n\n"
                f"Name: {product['name']}\n"
                f"Model: {product.get('model_number', 'unknown')}\n"
                f"Raw specs: {product.get('raw_specs', 'none provided')}\n\n"
                f"Use your tools to gather all information, then return the enriched JSON."
            ),
        }
    ]

    # Agentic loop
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        print(f"  [Agent] stop_reason={response.stop_reason}")

        # Collect tool calls
        tool_calls = [b for b in response.content if b.type == "tool_use"]
        text_blocks = [b for b in response.content if b.type == "text"]

        if tool_calls:
            # Add assistant message
            messages.append({"role": "assistant", "content": response.content})

            # Execute all tools and collect results
            tool_results = []
            for tc in tool_calls:
                print(f"  [Tool] {tc.name}({json.dumps(tc.input, indent=None)[:80]}...)")
                result = dispatch_tool(tc.name, tc.input)
                print(f"  [Result] {str(result)[:100]}...")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tc.id,
                    "content": json.dumps(result),
                })

            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            # Extract final JSON from text
            final_text = " ".join(b.text for b in text_blocks)
            try:
                # Strip any accidental markdown fences
                clean = re.sub(r"```(?:json)?|```", "", final_text).strip()
                enriched = json.loads(clean)
                print(f"  [Done] completeness_score={enriched.get('completeness_score', '?')}%")
                return {"input": product, "enriched": enriched, "status": "success"}
            except json.JSONDecodeError as e:
                print(f"  [Error] JSON parse failed: {e}")
                return {"input": product, "enriched": None, "raw_output": final_text, "status": "parse_error"}
        else:
            break

    return {"input": product, "status": "incomplete"}


# ── Batch runner ──────────────────────────────────────────────────────────────

def enrich_catalog(products: list[dict]) -> list[dict]:
    results = []
    for product in products:
        result = enrich_product(product)
        results.append(result)
    return results
