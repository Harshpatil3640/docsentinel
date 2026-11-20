"""Shared test helpers: a clean invoice that passes every rule."""

from datetime import date

import pytest

from docsentinel.gstin import checksum_char
from docsentinel.schemas import Invoice, LineItem

TODAY = date(2026, 11, 17)


def gstin(first14: str) -> str:
    return first14 + checksum_char(first14)


VENDOR_SAME_STATE = gstin("27ABCDE1234F1Z")  # Maharashtra, like the buyer
VENDOR_OTHER_STATE = gstin("29PQRSX5678Y1Z")  # Karnataka
BUYER = gstin("27AABCD1234E1Z")


@pytest.fixture
def vendors():
    return {
        VENDOR_SAME_STATE: {"gstin": VENDOR_SAME_STATE, "bank_account": "111122223333"},
        VENDOR_OTHER_STATE: {
            "gstin": VENDOR_OTHER_STATE,
            "bank_account": "444455556666",
        },
    }


@pytest.fixture
def same_state_invoice():
    """Clean intra-state invoice: 1000 at 18% = 90 CGST + 90 SGST."""
    return Invoice(
        invoice_number="V001-2026-0001",
        invoice_date="2026-06-01",
        due_date="2026-07-01",
        vendor_name="Test Traders",
        vendor_gstin=VENDOR_SAME_STATE,
        vendor_state="Maharashtra",
        buyer_name="DocSentinel Demo Pvt Ltd",
        buyer_gstin=BUYER,
        place_of_supply="Maharashtra",
        bank_account="111122223333",
        line_items=[
            LineItem(
                description="Chair",
                quantity=2,
                unit_price=500,
                gst_rate=18,
                amount=1000,
            )
        ],
        taxable_value=1000,
        cgst=90,
        sgst=90,
        igst=0,
        total=1180,
    )


@pytest.fixture
def other_state_invoice(same_state_invoice):
    """Clean inter-state invoice: 1000 at 18% = 180 IGST."""
    return same_state_invoice.model_copy(
        update={
            "vendor_gstin": VENDOR_OTHER_STATE,
            "vendor_state": "Karnataka",
            "bank_account": "444455556666",
            "cgst": 0,
            "sgst": 0,
            "igst": 180,
        }
    )
