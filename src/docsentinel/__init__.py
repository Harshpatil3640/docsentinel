"""DocSentinel command line: uv run docsentinel <command>."""

import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser(prog="docsentinel")
    commands = parser.add_subparsers(dest="command", required=True)
    extract = commands.add_parser("extract", help="extract fields from one PDF")
    extract.add_argument("pdf", help="path to an invoice PDF")
    extract.add_argument("--show-text", action="store_true", help="print PDF text")
    args = parser.parse_args()

    if args.command == "extract":
        from docsentinel.extraction import extract_invoice
        from docsentinel.llm import get_llm
        from docsentinel.parsing import pdf_to_text

        text = pdf_to_text(args.pdf)
        if args.show_text:
            print(text, end="\n\n")
        invoice = extract_invoice(text, get_llm())
        print(json.dumps(invoice.model_dump(), indent=2))