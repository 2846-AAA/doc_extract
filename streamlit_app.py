import streamlit as st
import requests
import json
from PIL import Image
import io

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Doc Extractor", page_icon="📄", layout="wide")

st.title("📄 Intelligent Document Extraction")
st.markdown("Upload a document to extract structured information using OCR + AI")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Upload Document")

    doc_type = st.selectbox(
        "Document Type",
        ["aadhaar", "passport", "driving_licence", "invoice", "pan_card"]
    )

    uploaded_file = st.file_uploader(
        "Choose image or PDF",
        type=["jpg", "jpeg", "png", "pdf"]
    )

    if uploaded_file:
        # show preview for images
        if uploaded_file.type.startswith("image"):
            img = Image.open(uploaded_file)
            st.image(img, caption="Uploaded Document", use_column_width=True)
            uploaded_file.seek(0)  # reset after reading

    extract_btn = st.button("Extract Information", type="primary", disabled=not uploaded_file)

with col2:
    st.subheader("Extracted Fields")

    if extract_btn and uploaded_file:
        with st.spinner("Processing document..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                params = {"doc_type": doc_type}
                response = requests.post(
                    f"{API_BASE}/extract",
                    files=files,
                    params=params,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success("Extraction successful!")

                    st.markdown("### Document Info")
                    info_cols = st.columns(2)
                    info_cols[0].metric("Document Type", result.get("doc_type", "-").upper())
                    info_cols[1].metric("Record ID", result.get("id", "-"))

                    st.markdown("### Extracted Data")
                    extracted = result.get("extracted_data", {})

                    if extracted:
                        for field, value in extracted.items():
                            if value:
                                st.text_input(
                                    field.replace("_", " ").title(),
                                    value=str(value),
                                    disabled=True
                                )
                    else:
                        st.warning("No data extracted. Check if the document is readable.")

                    with st.expander("Raw OCR Text"):
                        st.text(result.get("raw_text", "Not available"))

                    with st.expander("Full JSON Response"):
                        st.json(result)

                else:
                    err = response.json()
                    st.error(f"Error: {err.get('detail', 'Something went wrong')}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Make sure the FastAPI server is running on port 8000.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")

st.divider()

st.subheader("Previous Extractions")
if st.button("Load History"):
    try:
        resp = requests.get(f"{API_BASE}/extractions", timeout=10)
        if resp.status_code == 200:
            records = resp.json()
            if records:
                for rec in records[:10]:
                    with st.expander(f"#{rec['id']} - {rec['doc_type'].upper()} ({rec['created_at'][:10]})"):
                        st.json(rec.get("extracted_data", {}))
            else:
                st.info("No extractions found yet.")
        else:
            st.error("Failed to load history")
    except requests.exceptions.ConnectionError:
        st.error("API not reachable")

st.caption("Made by Anuja Dhamdhere | 2026")
