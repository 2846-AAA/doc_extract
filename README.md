# Intelligent Document Extraction Platform

A FastAPI + Streamlit app that extracts structured info from documents like Aadhaar, Passport, Driving Licence, Invoice, and PAN Card using OCR (Tesseract) and OpenAI LLM.

## What it does
- Upload a document image/PDF
- OCR extracts raw text, LLM parses it into structured fields
- Results saved to PostgreSQL and shown in a clean UI

## Requirements
- Python 3.12
- PostgreSQL running locally
- Tesseract OCR installed (Windows: https://github.com/UB-Mannheim/tesseract/wiki)
- OpenAI API key

## How to run

1. Clone the repo and go into the folder:
```
git clone <your-repo-url>
cd doc_extraction
```

2. Create virtual env and install deps:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your values

4. Set up the database (make sure postgres is running):
```
python -c "from app.db.database import init_db; init_db()"
```

5. Run the FastAPI backend:
```
uvicorn main:app --reload --port 8000
```

6. In another terminal, run Streamlit:
```
streamlit run streamlit_app.py
```

7. Open http://localhost:8501 in browser

## Running tests
```
pytest
```

## Notes
- Tesseract path in .env needs to point to your actual install
- Some tests are skipped without a real DB (marked with skip reason)
- PAN Card support added as extra (not in original spec)
