from docsentinel.rules import decide, run_all_rules

from .conftest import TODAY


def rule_names(findings):
    return {f.rule for f in findings}


def check(invoice, vendors, seen=None):
    return run_all_rules(invoice, vendors, seen or set(), TODAY)


# Clean invoices pass


def test_clean_same_state_invoice_passes(same_state_invoice, vendors):
    assert check(same_state_invoice, vendors) == []


def test_clean_other_state_invoice_passes(other_state_invoice, vendors):
    assert check(other_state_invoice, vendors) == []


def test_clean_invoice_is_approved(same_state_invoice, vendors):
    assert decide(check(same_state_invoice, vendors)) == "approve"


# Each planted problem is caught


def test_missing_invoice_number(same_state_invoice, vendors):
    inv = same_state_invoice.model_copy(update={"invoice_number": " "})
    assert rule_names(check(inv, vendors)) == {"missing_fields"}


def test_invalid_vendor_gstin(same_state_invoice, vendors):
    bad = same_state_invoice.vendor_gstin[:14] + "0"
    if bad == same_state_invoice.vendor_gstin:
        bad = same_state_invoice.vendor_gstin[:14] + "1"
    inv = same_state_invoice.model_copy(update={"vendor_gstin": bad})
    assert rule_names(check(inv, vendors)) == {"invalid_gstin"}


def test_igst_on_same_state_sale(same_state_invoice, vendors):
    inv = same_state_invoice.model_copy(update={"cgst": 0, "sgst": 0, "igst": 180})
    assert rule_names(check(inv, vendors)) == {"wrong_tax_type"}


def test_cgst_on_other_state_sale(other_state_invoice, vendors):
    inv = other_state_invoice.model_copy(update={"cgst": 90, "sgst": 90, "igst": 0})
    assert rule_names(check(inv, vendors)) == {"wrong_tax_type"}


def test_tax_too_high(same_state_invoice, vendors):
    inv = same_state_invoice.model_copy(update={"cgst": 190, "total": 1280})
    assert rule_names(check(inv, vendors)) == {"tax_math_error"}


def test_cgst_and_sgst_differ(same_state_invoice, vendors):
    inv = same_state_invoice.model_copy(update={"cgst": 100, "sgst": 80})
    assert rule_names(check(inv, vendors)) == {"tax_math_error"}


def test_small_rounding_difference_is_allowed(same_state_invoice, vendors):
    inv = same_state_invoice.model_copy(update={"total": 1180.5})
    assert check(inv, vendors) == []


def test_total_mismatch(same_state_invoice, vendors):
    inv = same_state_invoice.model_copy(update={"total": 1500})
    assert rule_names(check(inv, vendors)) == {"total_mismatch"}


def test_line_amount_wrong(same_state_invoice, vendors):
    item = same_state_invoice.line_items[0].model_copy(update={"amount": 900})
    inv = same_state_invoice.model_copy(update={"line_items": [item]})
    assert "line_items_mismatch" in rule_names(check(inv, vendors))


def test_lines_dont_add_up(same_state_invoice, vendors):
    inv = same_state_invoice.model_copy(update={"taxable_value": 1200, "total": 1380})
    assert rule_names(check(inv, vendors)) == {"line_items_mismatch"}


def test_future_date(same_state_invoice, vendors):
    inv = same_state_invoice.model_copy(
        update={"invoice_date": "2026-12-25", "due_date": "2027-01-24"}
    )
    assert rule_names(check(inv, vendors)) == {"future_date"}


def test_due_before_invoice(same_state_invoice, vendors):
    inv = same_state_invoice.model_copy(update={"due_date": "2026-05-20"})
    assert rule_names(check(inv, vendors)) == {"due_before_invoice"}


def test_bad_date_format(same_state_invoice, vendors):
    inv = same_state_invoice.model_copy(update={"invoice_date": "01/06/2026"})
    assert rule_names(check(inv, vendors)) == {"bad_date"}


def test_duplicate_invoice(same_state_invoice, vendors):
    seen = {(same_state_invoice.vendor_gstin, same_state_invoice.invoice_number)}
    assert rule_names(check(same_state_invoice, vendors, seen)) == {"duplicate_invoice"}


def test_unknown_vendor(same_state_invoice, vendors):
    assert rule_names(check(same_state_invoice, {})) == {"unknown_vendor"}


def test_bank_account_changed(same_state_invoice, vendors):
    inv = same_state_invoice.model_copy(update={"bank_account": "999988887777"})
    assert rule_names(check(inv, vendors)) == {"bank_account_changed"}


# Decisions


def test_reject_beats_review(same_state_invoice, vendors):
    inv = same_state_invoice.model_copy(update={"total": 1500, "bank_account": "1"})
    assert decide(check(inv, vendors)) == "reject"


def test_review_only(same_state_invoice, vendors):
    inv = same_state_invoice.model_copy(update={"bank_account": "1"})
    assert decide(check(inv, vendors)) == "review"
