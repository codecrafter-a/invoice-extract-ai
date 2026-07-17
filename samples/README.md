# Sample Invoice PDFs

This folder contains sample utility invoice PDFs for testing the extraction pipeline.

## Generating Samples

```bash
pip install fpdf2
python scripts/generate_sample_invoices.py
```

## Included Samples (after generation)

| File | Language | Utility | Notes |
|------|----------|---------|-------|
| electricity_bill_english.pdf | English | Electricity | Full invoice, ISO billing period |
| gas_bill_spanish.pdf | Spanish | Gas | Multilingual, numeric-date billing period |
| water_bill_french.pdf | French | Water | Multilingual, textual-date billing period |
| electricity_bill_german.pdf | German | Electricity | Multilingual, `DD.MM.YYYY` billing period |
| electricity_bill_minimal.pdf | English | Electricity | Minimal layout, no billing period |
| gas_bill_partial.pdf | English | Gas | Missing billing period |

## Usage

Upload any of these PDFs through the web UI at http://localhost:5173 to test extraction.
