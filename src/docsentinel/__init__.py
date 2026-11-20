"""DocSentinel command line: uv run docsentinel <command>."""

import argparse
import json
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30), "IST")


def main() -> None:
    parser = argparse.ArgumentParser(prog="docsentinel")
    commands = parser.add_subparsers(dest="command", required=True)

    extract = commands.add_parser("extract", help="extract fields from one PDF")
    extract.add_argument("pdf", help="path to an invoice PDF")
    extract.add_argument("--show-text", action="store_true", help="print PDF text")

    validate = commands.add_parser("validate", help="extract, then check the rules")
    validate.add_argument("pdf", help="path to an invoice PDF")
    validate.add_argument(
        "--save", action="store_true", help="remember it, to catch duplicates later"
    )
    args = parser.parse_args()

    from docsentinel.extraction import extract_invoice
    from docsentinel.llm import get_llm
    from docsentinel.parsing import pdf_to_text

    text = pdf_to_text(args.pdf)

    if args.command == "extract":
        if args.show_text:
            print(text, end="\n\n")
        invoice = extract_invoice(text, get_llm())
        print(json.dumps(invoice.model_dump(), indent=2))

    elif args.command == "validate":
        from docsentinel import db
        from docsentinel.rules import decide, load_vendors, run_all_rules

        invoice = extract_invoice(text, get_llm())
        conn = db.connect()
        findings = run_all_rules(
            invoice, load_vendors(), db.seen_invoices(conn), datetime.now(IST).date()
        )
        decision = decide(findings)

        print(f"Invoice {invoice.invoice_number} from {invoice.vendor_name}")
        if not findings:
            print("  All checks passed")
        for f in findings:
            print(f"  [{f.severity.upper()}] {f.rule}: {f.message}")
        print(f"Decision: {decision.upper()}")

        if args.save:
            db.save_invoice(
                conn, invoice.vendor_gstin, invoice.invoice_number, args.pdf, decision
            )
            print("Saved to docsentinel.db")
