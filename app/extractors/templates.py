from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DocumentTemplate:
    doc_type: str
    display_name: str
    fields: list[str]
    prompt_hint: str  # extra context for the LLM


TEMPLATES: dict[str, DocumentTemplate] = {
    "aadhaar": DocumentTemplate(
        doc_type="aadhaar",
        display_name="Aadhaar Card",
        fields=["name", "date_of_birth", "gender", "aadhaar_number", "address", "pincode"],
        prompt_hint="This is an Indian Aadhaar card. The 12-digit number is the Aadhaar number. Extract address carefully including state and pincode."
    ),
    "passport": DocumentTemplate(
        doc_type="passport",
        display_name="Passport",
        fields=["surname", "given_names", "nationality", "date_of_birth", "sex",
                "place_of_birth", "date_of_issue", "date_of_expiry", "passport_number", "mrz_line1", "mrz_line2"],
        prompt_hint="This is an Indian passport. MRZ lines are at the bottom of the bio page starting with P<. Extract all fields from the visual zone and machine readable zone."
    ),
    "driving_licence": DocumentTemplate(
        doc_type="driving_licence",
        display_name="Driving Licence",
        fields=["name", "father_or_husband_name", "date_of_birth", "address",
                "licence_number", "issue_date", "expiry_date", "vehicle_classes", "blood_group"],
        prompt_hint="This is an Indian driving licence. Licence number format is usually like MH01-XXXXXXXX. Vehicle classes are like LMV, MCWG etc."
    ),
    "invoice": DocumentTemplate(
        doc_type="invoice",
        display_name="Invoice",
        fields=["invoice_number", "invoice_date", "vendor_name", "vendor_address",
                "customer_name", "customer_address", "line_items", "subtotal",
                "tax_amount", "total_amount", "payment_terms"],
        prompt_hint="This is a commercial invoice. Line items should be extracted as a list with description, quantity, unit price, and total. Amounts should include currency symbol."
    ),
    # added PAN card as extra - not in original requirements but useful for Indian docs
    "pan_card": DocumentTemplate(
        doc_type="pan_card",
        display_name="PAN Card",
        fields=["name", "father_name", "date_of_birth", "pan_number"],
        prompt_hint="This is an Indian PAN card issued by Income Tax Department. PAN number is a 10-character alphanumeric code in format AAAAA0000A (5 letters, 4 digits, 1 letter). The 4th character indicates taxpayer type: P=Individual."
    ),
}


def get_template(doc_type: str) -> Optional[DocumentTemplate]:
    return TEMPLATES.get(doc_type.lower())


def list_supported_types() -> list[str]:
    return list(TEMPLATES.keys())
