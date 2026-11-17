# DocSentinel dataset

Synthetic Indian GST invoices for testing DocSentinel. No real company or personal data.

## How to rebuild

    uv run python scripts/generate_invoices.py --n 100 --seed 42

The same seed always gives the same files.

## Files

| File | What it holds |
| --- | --- |
| `invoices/INV-0001.pdf` ... `INV-0100.pdf` | One tax invoice per PDF |
| `labels.jsonl` | The correct answer for each invoice: `problem` (null = clean) and `fields` (every value printed on the PDF) |
| `vendors.csv` | The vendor master list: 15 trusted suppliers with GSTIN, state and bank account |

## What's inside

- 100 invoices: 70 clean, 30 with one planted problem each
- Buyer: DocSentinel Demo Pvt Ltd, Maharashtra (state code 27)
- GST rates: 5%, 18%, 40% (the slabs in force since 22 Sep 2025)
- Same-state supplier: CGST + SGST. Other states: IGST.

## Planted problems

| Problem | Count | What's wrong |
| --- | --- | --- |
| `invalid_gstin` | 4 | Supplier GSTIN checksum is wrong |
| `wrong_tax_type` | 4 | IGST charged for a same-state sale, or CGST+SGST for another state |
| `tax_math_error` | 4 | Tax amount doesn't match the rates |
| `total_mismatch` | 3 | Total doesn't equal taxable value + taxes |
| `duplicate_invoice` | 3 | Same supplier and invoice number as an earlier invoice |
| `unknown_vendor` | 3 | Supplier isn't in `vendors.csv` |
| `bank_account_changed` | 3 | Bank account differs from the vendor master (a common fraud signal) |
| `future_date` | 3 | Invoice date is after 17 Nov 2026 |
| `due_before_invoice` | 3 | Due date is before the invoice date |

## Limitations

Real invoices are messier: scanned images, many layouts, handwriting, missing fields. These PDFs use one clean layout, so results on this dataset will be better than on real invoices.