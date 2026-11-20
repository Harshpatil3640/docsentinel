"""The data models: what an extracted invoice looks like."""

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str = Field(description="Item or service name")
    quantity: int = Field(description="Quantity, a whole number")
    unit_price: float = Field(description="Price of one unit, in rupees")
    gst_rate: float = Field(description="GST rate in percent, for example 18")
    amount: float = Field(description="Line amount before tax, in rupees")


class Invoice(BaseModel):
    invoice_number: str = Field(description="Invoice number exactly as printed")
    invoice_date: str = Field(description="Invoice date as YYYY-MM-DD")
    due_date: str = Field(description="Due date as YYYY-MM-DD")
    vendor_name: str = Field(description="Supplier name")
    vendor_gstin: str = Field(description="Supplier GSTIN, 15 characters")
    vendor_state: str = Field(description="Supplier state")
    buyer_name: str = Field(description="Bill-to company name")
    buyer_gstin: str = Field(description="Buyer GSTIN, 15 characters")
    place_of_supply: str = Field(description="Place of supply (a state)")
    bank_account: str = Field(description="Bank account number to pay into")
    line_items: list[LineItem] = Field(description="Every row of the items table")
    taxable_value: float = Field(description="Taxable value before tax")
    cgst: float = Field(description="CGST amount; 0 if not charged")
    sgst: float = Field(description="SGST amount; 0 if not charged")
    igst: float = Field(description="IGST amount; 0 if not charged")
    total: float = Field(description="Invoice total including tax")
