from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import uuid4
from datetime import datetime, timezone, date
import os

app = FastAPI(
    title="TradeSure Voice AI API",
    description="Demo API for LC discrepancy checking, SCF early-payment estimates, obligation maturity checks, and specialist case creation.",
    version="2.1"
)

# Synthetic demo records only. These are not live banking or trade-finance records.
LC_RECORDS = {
    "TS-LC-2026-001": {
        "lc_status": "Discrepancy detected",
        "discrepancy_type": "Beneficiary name mismatch",
        "discrepancy_details": (
            "The beneficiary name in the commercial invoice "
            "does not match the LC document."
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

# In-memory demo cases. Records reset whenever the service restarts.
DEMO_CASES = {}

# Synthetic obligation records for maturity-status demonstrations.
# Dates are intentionally relative to the demo date (2026-11-22).
# These are not live banking or customer records.
OBLIGATION_RECORDS = {
    "TS-OBL-2026-001": {
        "obligation_reference_id": "TS-OBL-2026-001",
        "due_date": "2026-11-25",
        "outstanding_amount_inr": 125000.00,
        "payment_status": "UNPAID",
        "obligation_type": "Trade payment"
    },
    "TS-OBL-2026-002": {
        "obligation_reference_id": "TS-OBL-2026-002",
        "due_date": "2026-11-22",
        "outstanding_amount_inr": 85000.00,
        "payment_status": "UNPAID",
        "obligation_type": "Supplier invoice"
    },
    "TS-OBL-2026-003": {
        "obligation_reference_id": "TS-OBL-2026-003",
        "due_date": "2026-11-18",
        "outstanding_amount_inr": 210000.00,
        "payment_status": "UNPAID",
        "obligation_type": "Trade payment"
    },
    "TS-OBL-2026-004": {
        "obligation_reference_id": "TS-OBL-2026-004",
        "due_date": "2026-11-20",
        "outstanding_amount_inr": 0.00,
        "payment_status": "PAID",
        "obligation_type": "Supplier invoice"
    }
}



class LCRequest(BaseModel):
    lc_reference_number: str = Field(..., min_length=1)


class EarlyPaymentRequest(BaseModel):
    invoice_amount: float = Field(..., gt=0, description="Invoice amount in INR")
    annual_rate_percent: float = Field(..., ge=0, le=100)
    days_early: int = Field(..., gt=0, le=365)


class ObligationMaturityRequest(BaseModel):
    obligation_reference_id: str = Field(..., min_length=1)


class SpecialistCaseRequest(BaseModel):
    case_type: Literal[
        "EXPORT_LC_DISCREPANCY",
        "SCF_SUPPLIER_ONBOARDING",
        "SCF_EARLY_PAYMENT_ENQUIRY",
        "PAYMENT_NOT_REFLECTED",
        "PROMISE_TO_PAY",
        "ROLLOVER_REQUEST",
        "OTHER"
    ]
    caller_role: Literal["EXPORTER", "IMPORTER", "SUPPLIER", "BUYER", "OTHER"]
    case_summary: str = Field(..., min_length=10, max_length=1000)
    reference_id: Optional[str] = None
    urgency: Literal["LOW", "MEDIUM", "HIGH"] = "MEDIUM"
    callback_requested: bool = False
    callback_consent: bool = False
    callback_number: Optional[str] = None
    preferred_callback_time: Optional[str] = None


def verify_demo_api_key(x_api_key: Optional[str]):
    expected_key = os.getenv("DEMO_API_KEY", "tradesure-demo-key")
    if not x_api_key or x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/")
def home():
    return {
        "status": "running",
        "service": "TradeSure Voice AI API",
        "available_endpoints": [
            "/check-lc-discrepancy",
            "/calculate-early-payment",
            "/create-specialist-case",
            "/check-obligation-maturity"
        ]
    }


# Existing endpoint: preserve its request and response structure for the
# Gupshup tool that is already configured.
@app.post("/check-lc-discrepancy")
def check_lc_discrepancy(request: LCRequest):
    reference = request.lc_reference_number.strip().upper()

    if reference in LC_RECORDS:
        return LC_RECORDS[reference]

    return {
        "lc_status": "Record not found",
        "discrepancy_type": "Not available",
        "discrepancy_details": "No matching record exists in the demo dataset.",
        "document_name": "Not available",
        "next_action": "Verify the LC reference number or contact the trade operations team."
    }


@app.post("/calculate-early-payment")
def calculate_early_payment(
    request: EarlyPaymentRequest,
    x_api_key: Optional[str] = Header(default=None)
):
    verify_demo_api_key(x_api_key)

    # Simple-interest discount estimate using a 365-day year.
    discount = (
        request.invoice_amount
        * (request.annual_rate_percent / 100)
        * (request.days_early / 365)
    )
    estimated_payment = request.invoice_amount - discount

    return {
        "status": "success",
        "calculation_type": "Illustrative simple-interest estimate",
        "invoice_amount_inr": round(request.invoice_amount, 2),
        "annual_rate_percent": request.annual_rate_percent,
        "days_early": request.days_early,
        "estimated_discount_inr": round(discount, 2),
        "estimated_early_payment_inr": round(estimated_payment, 2),
        "disclaimer": (
            "Demo estimate only. Actual discount, fees, eligibility, "
            "and payment terms are subject to the financier's approval."
        )
    }


@app.post("/check-obligation-maturity")
def check_obligation_maturity(
    request: ObligationMaturityRequest,
    x_api_key: Optional[str] = Header(default=None)
):
    verify_demo_api_key(x_api_key)

    reference = request.obligation_reference_id.strip().upper()
    record = OBLIGATION_RECORDS.get(reference)

    if not record:
        return {
            "status": "not_found",
            "obligation_reference_id": reference,
            "maturity_status": "NOT_FOUND",
            "message": "No matching obligation exists in the synthetic demo dataset.",
            "next_action": "Verify the obligation reference or contact the relevant operations team."
        }

    due_date = date.fromisoformat(record["due_date"])
    today = date.today()
    payment_status = record["payment_status"]

    if payment_status == "PAID":
        maturity_status = "PAID"
        message = "This obligation is marked as paid in the synthetic demo dataset."
        next_action = "No payment action is required for this demo record."
    elif due_date > today:
        maturity_status = "UPCOMING"
        message = f"This obligation is upcoming and is due on {record['due_date']}."
        next_action = "Ensure payment is arranged on or before the due date."
    elif due_date == today:
        maturity_status = "DUE"
        message = "This obligation is due today."
        next_action = "Arrange payment today or verify whether payment has already been initiated."
    else:
        maturity_status = "OVERDUE"
        days_overdue = (today - due_date).days
        message = f"This unpaid obligation is overdue by {days_overdue} day(s)."
        next_action = "Review the outstanding payment and contact the relevant team if assistance is required."

    return {
        "status": "success",
        "obligation_reference_id": record["obligation_reference_id"],
        "obligation_type": record["obligation_type"],
        "due_date": record["due_date"],
        "outstanding_amount_inr": record["outstanding_amount_inr"],
        "payment_status": payment_status,
        "maturity_status": maturity_status,
        "days_overdue": max((today - due_date).days, 0) if maturity_status == "OVERDUE" else 0,
        "message": message,
        "next_action": next_action,
        "disclaimer": "Synthetic demonstration data only; this is not a live account or payment-status check."
    }


@app.post("/create-specialist-case")
def create_specialist_case(
    request: SpecialistCaseRequest,
    x_api_key: Optional[str] = Header(default=None)
):
    verify_demo_api_key(x_api_key)

    if request.callback_requested:
        if not request.callback_consent:
            raise HTTPException(
                status_code=400,
                detail="Explicit consent is required before a callback can be requested."
            )
        if not request.callback_number:
            raise HTTPException(
                status_code=400,
                detail="A callback number is required when a callback is requested."
            )

    case_id = f"TS-{uuid4().hex[:8].upper()}"
    case_record = {
        "case_id": case_id,
        "case_status": "RECEIVED_FOR_DEMO",
        "case_type": request.case_type,
        "caller_role": request.caller_role,
        "reference_id": request.reference_id,
        "case_summary": request.case_summary,
        "urgency": request.urgency,
        "callback_requested": request.callback_requested,
        "callback_number": request.callback_number if request.callback_requested else None,
        "preferred_callback_time": (
            request.preferred_callback_time if request.callback_requested else None
        ),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "message": (
            "Your demo case has been recorded. This is a simulated workflow; "
            "no real bank or operations team has been notified."
        )
    }
    DEMO_CASES[case_id] = case_record
    return case_record


@app.get("/cases/{case_id}")
def get_demo_case(
    case_id: str,
    x_api_key: Optional[str] = Header(default=None)
):
    verify_demo_api_key(x_api_key)
    case = DEMO_CASES.get(case_id.upper())
    if not case:
        raise HTTPException(status_code=404, detail="Demo case not found")
    return case
