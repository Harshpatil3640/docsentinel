"""Run the rules on the correct answers of all 100 invoices.

Every clean invoice must pass, and every planted problem must be caught by
its own rule and nothing else. No LLM is used: this tests the rules alone.
"""

import json

from docsentinel.rules import load_vendors, run_all_rules
from docsentinel.schemas import Invoice

from .conftest import TODAY


def test_rules_catch_every_planted_problem():
    vendors = load_vendors("data/vendors.csv")
    seen = set()
    with open("data/labels.jsonl", encoding="utf-8") as f:
        labels = [json.loads(line) for line in f]

    wrong = []
    for label in labels:
        inv = Invoice(**label["fields"])
        found = {f.rule for f in run_all_rules(inv, vendors, seen, TODAY)}
        expected = {label["problem"]} if label["problem"] else set()
        if found != expected:
            wrong.append(f"{label['file']}: expected {expected}, got {found}")
        seen.add((inv.vendor_gstin, inv.invoice_number))

    assert not wrong, "\n".join(wrong)
