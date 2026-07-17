#!/usr/bin/env python3
"""Generate sample utility invoice PDFs for testing."""

from pathlib import Path

try:
    from fpdf import FPDF
except ImportError:
    print("Install fpdf2: pip install fpdf2")
    raise

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"

INVOICES = [
    {
        "filename": "electricity_bill_english.pdf",
        "title": "Pacific Power & Light",
        "lines": [
            "PACIFIC POWER & LIGHT",
            "Utility Invoice",
            "",
            "Invoice Number: INV-2025-00847",
            "Account Number: 100294883",
            "Invoice Date: March 15, 2025",
            "Due Date: April 5, 2025",
            "Billing Period: 2025-02-01 to 2025-02-28",
            "Service Address: 742 Evergreen Terrace, Springfield, IL 62704",
            "Meter Number: MTR-55219",
            "",
            "Utility Type: Electricity",
            "Energy Consumption: 847 kWh",
            "",
            "Subtotal: USD 118.60",
            "Tax: USD 9.49",
            "Total Amount Due: USD 128.09",
            "",
            "Thank you for your business.",
        ],
    },
    {
        "filename": "gas_bill_spanish.pdf",
        "title": "Gas Natural del Norte",
        "lines": [
            "GAS NATURAL DEL NORTE S.A.",
            "Factura de Servicios",
            "",
            "Numero de Factura: FAC-2025-3391",
            "Numero de Cuenta: ES-88452019",
            "Fecha de Factura: 10 de marzo de 2025",
            "Fecha de Vencimiento: 31 de marzo de 2025",
            "Periodo de Facturacion: 01/02/2025 - 28/02/2025",
            "Direccion de Servicio: Calle Mayor 45, Madrid, 28013, Espana",
            "Numero de Contador: CNT-40921",
            "",
            "Tipo de Servicio: Gas",
            "Consumo: 34.5 therms",
            "",
            "Impuesto (IVA): EUR 9.66",
            "Importe Total: EUR 55.86",
            "",
            "Gracias por confiar en nosotros.",
        ],
    },
    {
        "filename": "water_bill_french.pdf",
        "title": "Eau de Paris",
        "lines": [
            "EAU DE PARIS",
            "Facture d'eau",
            "",
            "Numero de facture: FR-2025-1187",
            "Numero de compte: FR-70045512",
            "Date de facture: 5 mars 2025",
            "Date d'echeance: 25 mars 2025",
            "Periode de facturation: 1 fevrier 2025 au 28 fevrier 2025",
            "Adresse de service: 12 Rue de Rivoli, 75004 Paris, France",
            "Numero de compteur: CPT-20488",
            "",
            "Type de service: Eau / Water",
            "Consommation: 12.8 m3",
            "",
            "TVA: EUR 2.15",
            "Montant total: EUR 39.90",
            "",
            "Merci de votre confiance.",
        ],
    },
    {
        "filename": "electricity_bill_german.pdf",
        "title": "Stadtwerke Muenchen",
        "lines": [
            "STADTWERKE MUENCHEN GmbH",
            "Stromrechnung",
            "",
            "Rechnungsnummer: DE-2025-6120",
            "Kundennummer: DE-33110897",
            "Rechnungsdatum: 12.03.2025",
            "Faelligkeitsdatum: 02.04.2025",
            "Abrechnungszeitraum: 01.02.2025 - 28.02.2025",
            "Adresse: Marienplatz 8, 80331 Muenchen, Deutschland",
            "Zaehlernummer: ZAE-71903",
            "",
            "Art: Strom (Electricity)",
            "Verbrauch: 612 kWh",
            "",
            "Mehrwertsteuer: EUR 18.36",
            "Gesamtbetrag: EUR 114.96",
            "",
            "Vielen Dank.",
        ],
    },
    {
        "filename": "electricity_bill_minimal.pdf",
        "title": "City Electric Co",
        "lines": [
            "CITY ELECTRIC CO",
            "",
            "Invoice Date: 2025-01-20",
            "Address: 100 Main St, Austin, TX",
            "Electric - 520 kWh",
        ],
    },
    {
        "filename": "gas_bill_partial.pdf",
        "title": "Metro Gas Services",
        "lines": [
            "METRO GAS SERVICES",
            "Invoice #8842",
            "",
            "Date: April 2, 2025",
            "Service Location: 55 Oak Avenue, Denver, CO 80202",
            "",
            "Natural Gas Usage: 28 therms",
            "Total Amount Due: USD 61.40",
        ],
    },
]


def create_pdf(filename: str, lines: list[str]) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    for line in lines:
        pdf.cell(0, 8, line, new_x="LMARGIN", new_y="NEXT")

    output_path = SAMPLES_DIR / filename
    pdf.output(str(output_path))
    print(f"Created: {output_path}")


def main() -> None:
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    for invoice in INVOICES:
        create_pdf(invoice["filename"], invoice["lines"])

    print(f"\nGenerated {len(INVOICES)} sample PDFs in {SAMPLES_DIR}")


if __name__ == "__main__":
    main()
