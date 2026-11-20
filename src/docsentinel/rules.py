"""Plain-Python checks for an extracted invoice. No LLM involved.

Each check returns a Finding when something is wrong, or nothing when it's fine.
Severity "reject" means the invoice must not be paid.
Severity "review" means a human must look at it first.
"""

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from docsentinel.gstin import is_valid_gstin
from docsentinel.schemas import Invoice

TOLERANCE = 1.0  # rupees: allow small rounding differences


@dataclass
class Finding:
    rule: str
    severity: str  # "reject" or "review"
    message: str


def load_vendors(path: str | Path = "data/vendors.csv") -> dict[str, dict]:
    """Return the vendor master as {gstin: vendor row}."""
    with open(path, encoding="utf-8") as f:
        return {row["gstin"]: row for row in csv.DictReader(f)}


def check_required_fields(inv: Invoice) -> list[Finding]:
    missing = [
        name
        for name in ["invoice_number", "invoice_date", "vendor_gstin", "buyer_gstin"]
        if not getattr(inv, name).strip()
    ]
    if not inv.line_items:
        missing.append("line_items")
    if missing:
        return [Finding("missing_fields", "reject", f"Missing: {', '.join(missing)}")]
    return []


def check_gstins(inv: Invoice) -> list[Finding]:
    findings = []
    if not is_valid_gstin(inv.vendor_gstin):
        findings.append(
            Finding(
                "invalid_gstin", "reject", f"Vendor GSTIN {inv.vendor_gstin} is invalid"
            )
        )
    if not is_valid_gstin(inv.buyer_gstin):
        findings.append(
            Finding(
                "invalid_gstin", "reject", f"Buyer GSTIN {inv.buyer_gstin} is invalid"
            )
        )
    return findings


def check_tax_type(inv: Invoice) -> list[Finding]:
    """Same state: CGST + SGST only. Different states: IGST only."""
    same_state = inv.vendor_gstin[:2] == inv.buyer_gstin[:2]
    if same_state and inv.igst > 0:
        return [
            Finding("wrong_tax_type", "reject", "IGST charged on a same-state sale")
        ]
    if not same_state and (inv.cgst > 0 or inv.sgst > 0):
        return [
            Finding(
                "wrong_tax_type", "reject", "CGST/SGST charged on an inter-state sale"
            )
        ]
    return []


def check_tax_math(inv: Invoice) -> list[Finding]:
    """Total tax must match the line rates, and CGST must equal SGST."""
    expected = sum(item.amount * item.gst_rate / 100 for item in inv.line_items)
    charged = inv.cgst + inv.sgst + inv.igst
    findings = []
    if abs(charged - expected) > TOLERANCE:
        findings.append(
            Finding(
                "tax_math_error",
                "reject",
                f"Tax charged {charged:.2f}, expected {expected:.2f}",
            )
        )
    elif abs(inv.cgst - inv.sgst) > TOLERANCE:
        findings.append(Finding("tax_math_error", "reject", "CGST and SGST differ"))
    return findings


def check_line_items(inv: Invoice) -> list[Finding]:
    """Each line: qty x price = amount. All lines add up to the taxable value."""
    for item in inv.line_items:
        if abs(item.quantity * item.unit_price - item.amount) > TOLERANCE:
            return [
                Finding(
                    "line_items_mismatch",
                    "reject",
                    f"'{item.description}': qty x price doesn't equal amount",
                )
            ]
    lines_total = sum(item.amount for item in inv.line_items)
    if abs(lines_total - inv.taxable_value) > TOLERANCE:
        return [
            Finding(
                "line_items_mismatch",
                "reject",
                f"Lines add to {lines_total:.2f}, taxable value is {inv.taxable_value:.2f}",
            )
        ]
    return []


def check_total(inv: Invoice) -> list[Finding]:
    expected = inv.taxable_value + inv.cgst + inv.sgst + inv.igst
    if abs(inv.total - expected) > TOLERANCE:
        return [
            Finding(
                "total_mismatch",
                "reject",
                f"Total {inv.total:.2f}, expected {expected:.2f}",
            )
        ]
    return []


def check_dates(inv: Invoice, today: date) -> list[Finding]:
    try:
        invoice_day = date.fromisoformat(inv.invoice_date)
        due_day = date.fromisoformat(inv.due_date)
    except ValueError:
        return [Finding("bad_date", "review", "A date is not in YYYY-MM-DD format")]
    if invoice_day > today:
        return [
            Finding(
                "future_date", "reject", f"Invoice date {invoice_day} is in the future"
            )
        ]
    if due_day < invoice_day:
        return [
            Finding(
                "due_before_invoice", "review", "Due date is before the invoice date"
            )
        ]
    return []


def check_duplicate(inv: Invoice, seen: set[tuple[str, str]]) -> list[Finding]:
    if (inv.vendor_gstin, inv.invoice_number) in seen:
        return [
            Finding(
                "duplicate_invoice",
                "reject",
                f"Invoice {inv.invoice_number} from this vendor was already processed",
            )
        ]
    return []


def check_vendor(inv: Invoice, vendors: dict[str, dict]) -> list[Finding]:
    """Vendor must be in the master list, with the same bank account."""
    vendor = vendors.get(inv.vendor_gstin)
    if vendor is None:
        return [
            Finding("unknown_vendor", "review", "Vendor is not in the vendor master")
        ]
    if vendor["bank_account"] != inv.bank_account:
        return [
            Finding(
                "bank_account_changed",
                "review",
                "Bank account differs from the vendor master (possible fraud)",
            )
        ]
    return []


def run_all_rules(
    inv: Invoice,
    vendors: dict[str, dict],
    seen: set[tuple[str, str]],
    today: date,
) -> list[Finding]:
    """Run every check and return all findings. Empty list = clean invoice."""
    findings = check_required_fields(inv)
    if findings:
        return findings  # nothing else can be checked reliably
    gstin_findings = check_gstins(inv)
    findings += gstin_findings
    findings += check_tax_type(inv)
    findings += check_tax_math(inv)
    findings += check_line_items(inv)
    findings += check_total(inv)
    findings += check_dates(inv, today)
    findings += check_duplicate(inv, seen)
    if not gstin_findings:  # a broken GSTIN can't be looked up in the master
        findings += check_vendor(inv, vendors)
    return findings


def decide(findings: list[Finding]) -> str:
    """reject if any reject finding, review if any review finding, else approve."""
    severities = {f.severity for f in findings}
    if "reject" in severities:
        return "reject"
    if "review" in severities:
        return "review"
    return "approve"
