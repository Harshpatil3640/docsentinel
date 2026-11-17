"""Generate synthetic Indian GST invoices as PDFs, with the correct answers.

Run:  uv run python scripts/generate_invoices.py --n 100 --seed 42

Creates:
  data/vendors.csv          the vendor master list (our "trusted" records)
  data/invoices/*.pdf       one PDF per invoice
  data/labels.jsonl         the correct answer for every invoice, one JSON per line
"""

import argparse
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker
from fpdf import FPDF

from docsentinel.gstin import STATES, checksum_char, make_gstin

REFERENCE_DATE = date(2026, 11, 17)  # "today" for this dataset, so runs repeat exactly
BUYER = {
    "name": "DocSentinel Demo Pvt Ltd",
    "state_code": "27",
}  # buyer is in Maharashtra
GST_RATES = [5, 18, 18, 18, 40]  # 18% is most common, so it appears more often
ITEMS = [
    "Laptop stand",
    "Office chair",
    "Printer paper (box)",
    "Network cable",
    "Cloud hosting (monthly)",
    "Software licence",
    "Consulting hours",
    "Courier service",
    "LED monitor",
    "Cleaning service",
    "Training session",
    "Air conditioner service",
    "Stationery kit",
    "Security audit",
]
PROBLEMS = [
    "invalid_gstin",
    "wrong_tax_type",
    "tax_math_error",
    "total_mismatch",
    "duplicate_invoice",
    "unknown_vendor",
    "bank_account_changed",
    "future_date",
    "due_before_invoice",
]


def make_vendor(vendor_id: str, fake: Faker, rng: random.Random) -> dict:
    state_code = rng.choice(list(STATES))
    return {
        "vendor_id": vendor_id,
        "name": fake.company(),
        "gstin": make_gstin(state_code, rng),
        "state_code": state_code,
        "state": STATES[state_code],
        "bank_account": str(rng.randint(10**11, 10**12 - 1)),
    }


def compute_taxes(items: list, same_state: bool) -> dict:
    """Same state: CGST + SGST (half each). Different states: IGST."""
    taxable = round(sum(i["amount"] for i in items), 2)
    tax = round(sum(i["amount"] * i["gst_rate"] / 100 for i in items), 2)
    if same_state:
        cgst = round(tax / 2, 2)
        return {"taxable_value": taxable, "cgst": cgst, "sgst": cgst, "igst": 0.0}
    return {"taxable_value": taxable, "cgst": 0.0, "sgst": 0.0, "igst": tax}


def make_invoice(
    number: int, vendor: dict, buyer_gstin: str, rng: random.Random
) -> dict:
    items = []
    for _ in range(rng.randint(1, 5)):
        qty = rng.randint(1, 20)
        price = round(rng.uniform(150, 25000), 2)
        items.append(
            {
                "description": rng.choice(ITEMS),
                "quantity": qty,
                "unit_price": price,
                "gst_rate": rng.choice(GST_RATES),
                "amount": round(qty * price, 2),
            }
        )
    inv_date = date(2026, 4, 1) + timedelta(days=rng.randint(0, 200))
    taxes = compute_taxes(items, vendor["state_code"] == BUYER["state_code"])
    total = round(
        taxes["taxable_value"] + taxes["cgst"] + taxes["sgst"] + taxes["igst"], 2
    )
    return {
        "invoice_number": f"{vendor['vendor_id']}-{2026}-{number:04d}",
        "invoice_date": inv_date.isoformat(),
        "due_date": (inv_date + timedelta(days=30)).isoformat(),
        "vendor_name": vendor["name"],
        "vendor_gstin": vendor["gstin"],
        "vendor_state": vendor["state"],
        "buyer_name": BUYER["name"],
        "buyer_gstin": buyer_gstin,
        "place_of_supply": STATES[BUYER["state_code"]],
        "bank_account": vendor["bank_account"],
        "line_items": items,
        **taxes,
        "total": total,
    }


def plant_problem(
    inv: dict, problem: str, rng: random.Random, fake: Faker, earlier: list
) -> dict:
    """Change one thing in a clean invoice so a rule should catch it."""
    if problem == "invalid_gstin":
        good = inv["vendor_gstin"]
        wrong = rng.choice(
            [c for c in "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ" if c != good[-1]]
        )
        inv["vendor_gstin"] = good[:14] + wrong
    elif problem == "wrong_tax_type":
        same_state = inv["igst"] == 0  # flip it: charge the wrong kind of tax
        inv.update(compute_taxes(inv["line_items"], not same_state))
        inv["total"] = round(
            inv["taxable_value"] + inv["cgst"] + inv["sgst"] + inv["igst"], 2
        )
    elif problem == "tax_math_error":
        extra = round(rng.uniform(50, 500), 2)
        key = "igst" if inv["igst"] else "cgst"
        inv[key] = round(inv[key] + extra, 2)
        inv["total"] = round(
            inv["taxable_value"] + inv["cgst"] + inv["sgst"] + inv["igst"], 2
        )
    elif problem == "total_mismatch":
        inv["total"] = round(inv["total"] + rng.uniform(100, 1000), 2)
    elif problem == "duplicate_invoice":
        original = rng.choice(
            earlier
        )  # same vendor + same number as an earlier invoice
        for key in [
            "invoice_number",
            "vendor_name",
            "vendor_gstin",
            "vendor_state",
            "bank_account",
        ]:
            inv[key] = original[key]
        same_state = inv["vendor_gstin"][:2] == BUYER["state_code"]
        inv.update(compute_taxes(inv["line_items"], same_state))
        inv["total"] = round(
            inv["taxable_value"] + inv["cgst"] + inv["sgst"] + inv["igst"], 2
        )
    elif problem == "unknown_vendor":
        stranger = make_vendor("VNEW", fake, rng)
        for key, src in [
            ("vendor_name", "name"),
            ("vendor_gstin", "gstin"),
            ("vendor_state", "state"),
            ("bank_account", "bank_account"),
        ]:
            inv[key] = stranger[src]
        same_state = stranger["state_code"] == BUYER["state_code"]
        inv.update(compute_taxes(inv["line_items"], same_state))
        inv["total"] = round(
            inv["taxable_value"] + inv["cgst"] + inv["sgst"] + inv["igst"], 2
        )
    elif problem == "bank_account_changed":
        inv["bank_account"] = str(rng.randint(10**11, 10**12 - 1))
    elif problem == "future_date":
        future = REFERENCE_DATE + timedelta(days=rng.randint(10, 90))
        inv["invoice_date"] = future.isoformat()
        inv["due_date"] = (future + timedelta(days=30)).isoformat()
    elif problem == "due_before_invoice":
        invoice_day = date.fromisoformat(inv["invoice_date"])
        inv["due_date"] = (invoice_day - timedelta(days=rng.randint(1, 15))).isoformat()
    return inv


def write_pdf(inv: dict, path: Path) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "TAX INVOICE", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", size=10)
    header = [
        ("Invoice No", inv["invoice_number"]),
        ("Invoice Date", inv["invoice_date"]),
        ("Due Date", inv["due_date"]),
        ("Supplier", inv["vendor_name"]),
        ("Supplier GSTIN", inv["vendor_gstin"]),
        ("Supplier State", inv["vendor_state"]),
        ("Bill To", inv["buyer_name"]),
        ("Buyer GSTIN", inv["buyer_gstin"]),
        ("Place of Supply", inv["place_of_supply"]),
    ]
    for label, value in header:
        pdf.cell(45, 7, f"{label}:")
        pdf.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    widths = [70, 20, 35, 20, 35]
    pdf.set_font("Helvetica", "B", 10)
    for w, title in zip(
        widths, ["Description", "Qty", "Unit Price", "GST %", "Amount"]
    ):
        pdf.cell(w, 8, title, border=1)
    pdf.ln()
    pdf.set_font("Helvetica", size=10)
    for item in inv["line_items"]:
        row = [
            item["description"],
            item["quantity"],
            f"{item['unit_price']:.2f}",
            item["gst_rate"],
            f"{item['amount']:.2f}",
        ]
        for w, value in zip(widths, row):
            pdf.cell(w, 8, str(value), border=1)
        pdf.ln()
    pdf.ln(4)

    totals = [
        ("Taxable Value", inv["taxable_value"]),
        ("CGST", inv["cgst"]),
        ("SGST", inv["sgst"]),
        ("IGST", inv["igst"]),
        ("Total (INR)", inv["total"]),
    ]
    for label, value in totals:
        pdf.cell(145, 7, label, align="R")
        pdf.cell(35, 7, f"{value:.2f}", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.cell(
        0,
        7,
        f"Pay to bank account: {inv['bank_account']}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.output(str(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic GST invoices")
    parser.add_argument("--n", type=int, default=100, help="number of invoices")
    parser.add_argument(
        "--seed", type=int, default=42, help="same seed = same invoices"
    )
    parser.add_argument("--out", default="data", help="output folder")
    parser.add_argument(
        "--problem-share", type=float, default=0.3, help="share with a problem"
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    fake = Faker("en_IN")
    fake.seed_instance(args.seed)

    out = Path(args.out)
    (out / "invoices").mkdir(parents=True, exist_ok=True)

    vendors = [make_vendor(f"V{i:03d}", fake, rng) for i in range(1, 16)]
    with open(out / "vendors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(vendors[0]))
        writer.writeheader()
        writer.writerows(vendors)

    buyer_first14 = "27AABCD1234E1Z"
    buyer_gstin = buyer_first14 + checksum_char(buyer_first14)

    n_problems = round(args.n * args.problem_share)
    plan = [None] * (args.n - n_problems) + [
        PROBLEMS[i % len(PROBLEMS)] for i in range(n_problems)
    ]
    rng.shuffle(plan)
    first_clean = plan.index(None)  # a duplicate needs an earlier invoice to copy
    if plan[0] == "duplicate_invoice":
        plan[0], plan[first_clean] = plan[first_clean], plan[0]

    labels, earlier = [], []
    for number, problem in enumerate(plan, start=1):
        inv = make_invoice(number, rng.choice(vendors), buyer_gstin, rng)
        if problem:
            inv = plant_problem(inv, problem, rng, fake, earlier)
        earlier.append(inv)
        file_name = f"INV-{number:04d}.pdf"
        write_pdf(inv, out / "invoices" / file_name)
        labels.append(
            {"file": f"invoices/{file_name}", "problem": problem, "fields": inv}
        )

    with open(out / "labels.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps(label) + "\n" for label in labels)

    counts = {}
    for label in labels:
        key = label["problem"] or "clean"
        counts[key] = counts.get(key, 0) + 1
    print(f"Created {len(labels)} invoices in {out / 'invoices'}")
    for key, count in sorted(counts.items()):
        print(f"  {key}: {count}")


if __name__ == "__main__":
    main()