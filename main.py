

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

    penalty_rate_percent = 2.0  # Illustrative annual penalty rate for this synthetic POC.
    days_overdue = 0

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

    outstanding_amount = float(record["outstanding_amount_inr"])
    penalty_amount = 0.0
    if maturity_status == "OVERDUE" and outstanding_amount > 0:
        penalty_amount = round(
            outstanding_amount * (penalty_rate_percent / 100) * days_overdue / 365,
            2
        )

    total_payable = round(outstanding_amount + penalty_amount, 2)

    return {
        "status": "success",
        "obligation_reference_id": record["obligation_reference_id"],
        "obligation_type": record["obligation_type"],
        "due_date": record["due_date"],
        "outstanding_amount_inr": outstanding_amount,
        "payment_status": payment_status,
        "maturity_status": maturity_status,
        "days_overdue": days_overdue,
        "penalty_rate_percent": penalty_rate_percent,
        "penalty_amount_inr": penalty_amount,
        "total_payable_inr": total_payable,
        "penalty_calculation_basis": "Simple interest: outstanding amount x annual penalty rate x days overdue / 365. Applied only to unpaid overdue obligations.",
        "message": message,
        "next_action": next_action,
        "disclaimer": "Synthetic demonstration data only. The 2% per annum penalty rate is illustrative and must not be treated as a contractual or live banking charge."
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
