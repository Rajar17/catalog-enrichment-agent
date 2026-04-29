"""
Tenarai Catalog Enrichment — Streamlit Demo UI
Run: streamlit run streamlit_app.py
"""

import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from agents.enrichment_agent import enrich_product

st.set_page_config(
    page_title="Tenarai — Catalog Enrichment Agent",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Tenarai — HP Laptop Catalog Enrichment Agent")
st.caption("Powered by Claude claude-sonnet-4-6 · Built by Tenarai")

st.divider()

# ── Input form ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Raw Product Input")
    product_name = st.text_input("Product name", value="HP Laptop 15s-eq2144AU")
    model_number = st.text_input("Model number", value="15s-eq2144AU")
    raw_specs = st.text_area(
        "Raw specs (optional)",
        value="AMD Ryzen 5, 8GB, 512GB",
        height=80,
    )

    st.markdown("**Or pick a demo product:**")
    demo = st.selectbox(
        "Demo products",
        options=[
            "HP 15s (AMD Ryzen 5, Budget)",
            "HP Pavilion 15 (Intel i5, Mid-range)",
            "HP ENVY x360 13 (Intel i7, Premium OLED)",
        ],
    )

    demo_map = {
        "HP 15s (AMD Ryzen 5, Budget)": ("HP Laptop 15s-eq2144AU", "15s-eq2144AU", "AMD Ryzen 5, 8GB, 512GB"),
        "HP Pavilion 15 (Intel i5, Mid-range)": ("HP Pavilion 15-eg2006TX", "pavilion-15-eg2006TX", "Intel i5, 16GB, 512GB SSD"),
        "HP ENVY x360 13 (Intel i7, Premium OLED)": ("HP ENVY x360 13-bf0107TU", "envy-x360-13-bf0107TU", "Intel i7, 16GB, 1TB SSD, OLED touch"),
    }

    if st.button("Load demo product"):
        product_name, model_number, raw_specs = demo_map[demo]
        st.rerun()

    run = st.button("🚀 Enrich Product", type="primary", use_container_width=True)

with col2:
    st.subheader("Enriched Output")

    if run:
        product = {"name": product_name, "model_number": model_number, "raw_specs": raw_specs}

        with st.spinner("Agent is enriching your product..."):
            result = enrich_product(product)

        if result["status"] == "success":
            e = result["enriched"]

            st.success(f"Enriched successfully — Completeness: {e.get('completeness_score', '?')}%")

            st.markdown(f"**{e.get('enriched_title', '—')}**")
            st.caption(e.get("category_path", ""))

            st.markdown("**Description**")
            st.write(e.get("marketing_description", "—"))

            st.markdown("**Key specs**")
            specs = e.get("key_specs", {})
            if specs:
                cols = st.columns(2)
                items = list(specs.items())
                for i, (k, v) in enumerate(items):
                    cols[i % 2].markdown(f"**{k}:** {v}")

            st.markdown("**Use cases**")
            uses = e.get("use_cases", [])
            st.write(" · ".join(uses))

            st.markdown("**Search tags**")
            tags = e.get("search_tags", [])
            st.write("  ".join([f"`{t}`" for t in tags]))

            st.markdown("**SEO meta description**")
            st.info(e.get("meta_description", "—"))

            with st.expander("View full JSON output"):
                st.json(e)
        else:
            st.error(f"Enrichment failed: {result.get('status')}")
            if result.get("raw_output"):
                st.text(result["raw_output"])
    else:
        st.info("Fill in the product details on the left and click **Enrich Product**.")
