
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="TradeSure Voice AI API",
    description="Demo API for LC discrepancy checking",
    version="1.0"
)

# Synthetic demo records only
LC_RECORDS = {
    "TS-LC-2026-001": {
        "lc_status": "Discrepancy detected",
        "discrepancy_type": "Beneficiary name mismatch",
        "discrepancy_details": (
            "The beneficiary name in the commercial "
            "invoice does not match the LC document."
        ),
        "document_name": "Commercial Invoice",
        "next_action": (
            "Request the corrected commercial invoice "
            "and forward it to the trade operations team."
        )
    },
    "TS-LC-2026-002": {
        "lc_status": "Under review",
        "discrepancy_type": "Document verification pending",
        "discrepancy_details": (
            "The submitted bill of lading is awaiting "
            "verification by the operations team."
        ),
        "document_name": "Bill of Lading",
        "next_action": (
            "Wait for document verification and contact "
            "the trade operations team if delayed."
        )
    },
    "TS-LC-2026-003": {
        "lc_status": "No discrepancy detected",
        "discrepancy_type": "None",
        "discrepancy_details": (
            "All documents in this synthetic demo record "
            "match the configured LC requirements."
        ),
        "document_name": "All submitted documents",
        "next_action": "Continue with the next processing stage."
    }
}


class LCRequest(BaseModel):
    lc_reference_number: str


@app.get("/")
def home():
    return {
        "status": "running",
        "service": "TradeSure Voice AI API"
    }


@app.post("/check-lc-discrepancy")
def check_lc_discrepancy(request: LCRequest):

    reference = request.lc_reference_number.strip().upper()

    if reference in LC_RECORDS:
        return LC_RECORDS[reference]

    return {
        "lc_status": "Record not found",
        "discrepancy_type": "Not available",
        "discrepancy_details": (
            "No matching record exists in the demo dataset."
        ),
        "document_name": "Not available",
        "next_action": (
            "Verify the LC reference number or contact "
            "the trade operations team."
        )
    }
