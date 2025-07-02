# streamlit_app.py  –  Orbit Agritech DOCX generator (no PDF)

import streamlit as st
from datetime import datetime
from io import BytesIO
from docxtpl import DocxTemplate, RichText

# ─────────────────────────────────────────────────────────────────────
#  1.  Constants
# ─────────────────────────────────────────────────────────────────────
TEMPLATES = {
    "Quotation Summary":        "Orbit_Agritech_Quotation_Summary_Template.docx",
    "Partial Proforma Receipt": "Orbit_Agritech_Partial_Proforma_Receipt.docx",
    "Full Proforma Receipt":    "Orbit_Agritech_Full_Proforma_Receipt.docx",
}

ITEMS = [
    ("12 HP PT Pro",                               112_000, 1),
    ("Battery Sets",                                                 56_000, 1),
    ("Fast Chargers",                                                 6_5000, 2),
    ("Front Dead Weight",                                             0, 0),
    ("Wheel Dead Weight",                                             0, 0),
    ("1 Set of Sugarcane Blades(Weeding)",   4_400, 0),
    ("1 Set of Sugarcane Blades(Earthing-up)", 4_400, 0),
    ("1 Set of Tyres (5x10)",                                         8_000, 0),
    ("Toolkit",                           1_200, 0),
    ("Ginger Kit",                                                   10_000, 0),
    ("Seat",                                                          6_500, 0),
    ("Jack",                                                          1_100, 0),
    ("BuyBack Guarantee",                                            10_000, 0),
]

PLACEHOLDERS = {
    "12 HP PT Pro": "quantity_pt_pro",
    "Battery Sets":                   "quantity_battery",
    "Fast Chargers":                  "quantity_charger",
    "Front Dead Weight":              "quantity_front_dead_weight",
    "Wheel Dead Weight":              "quantity_wheel_dead_weight",
    "1 Set of Sugarcane Blades(Weeding)":   "quantity_blade_weeding",
    "1 Set of Sugarcane Blades(Earthing-up)": "quantity_blade_earthing",
    "1 Set of Tyres (5x10)":           "quantity_tyres",
    "Toolkit": "quantity_toolkit",
    "Ginger Kit":                     "quantity_ginger",
    "Seat":                            "quantity_seat",
    "Jack":                            "quantity_jack",
    "BuyBack Guarantee":              "quantity_buyback_guarantee",
}

SUBSIDY_CAPS = {
    "Telecaller":                  (55_000, 75_000),
    "Business Development Officer": (60_000, 80_000),
    "Manager":                     (65_000, 85_000),
    "Co-Founder":                 (100_000,120_000),
}

def numeric_only(raw: str, length: int) -> str:
    return ''.join(filter(str.isdigit, raw))[:length]

# ─────────────────────────────────────────────────────────────────────
#  2.  UI
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Orbit Docs Generator", layout="wide")
st.title("Orbit Document Generator")

doc_type = st.radio(
    "Select Document Type:",
    ["Quotation Summary", "Partial Proforma Receipt", "Full Proforma Receipt"]
)

doc_no = numeric_only(
    st.text_input("Document / Receipt Number *  (max 4 digits)", max_chars=4),
    4
)
date = st.date_input("Date", datetime.today()).strftime("%d/%m/%Y")
customer_name    = st.text_input("Customer Name *", max_chars=50)
customer_address = st.text_area("Address *", height=80)
customer_phone   = numeric_only(
    st.text_input("Phone Number * (10 digits)", max_chars=10),
    10
)
customer_email   = st.text_input("Email (optional)", max_chars=50)
form_filled_by   = st.selectbox(
    "Filled By *", ["Telecaller", "Business Development Officer", "Manager", "Co-Founder"]
)

# Quantities
st.markdown("---")
st.subheader("Enter Quantities for Each Item")
selected_items, total_price, battery_qty = [], 0, 0
for name, price, min_qty in ITEMS:
    qty = st.number_input(name, min_value=min_qty, step=1, value=min_qty, key=f"qty_{name}")
    if qty:
        selected_items.append((name, qty))
        total_price += price * qty
        if name == "Battery Sets":
            battery_qty = qty

# Subsidy (quotation only)
subsidy = 0
if doc_type == "Quotation Summary":
    st.markdown("---")
    st.subheader("Subsidy")
    if st.radio("Apply Subsidy?", ("No", "Yes")) == "Yes":
        cap = SUBSIDY_CAPS[form_filled_by][0 if battery_qty <= 1 else 1]
        subsidy = st.slider("Select Subsidy Amount (₹)", 0, cap, step=1000)

final_price = total_price - subsidy

# Receipt-specific extras
amount_received = payment_mode = reference_id = payment_date = ""
balance_due = tentative_delivery = delivery_date = ""
if "Proforma" in doc_type:
    amount_received = st.text_input("Amount Received (₹) *", max_chars=12)
    payment_mode    = st.selectbox("Payment Mode", ["Cashfree", "Cash", "Other"])
    reference_id    = st.text_input("Reference ID (optional)", max_chars=20)
    payment_date    = st.date_input("Payment Date", datetime.today()).strftime("%d/%m/%Y")
    if doc_type == "Partial Proforma Receipt":
        balance_due        = st.text_input("Balance Due (₹) *", max_chars=12)
        tentative_delivery = st.date_input("Tentative Delivery Date", datetime.today()).strftime("%d/%m/%Y")
    else:
        delivery_date      = st.date_input("Delivery Date", datetime.today()).strftime("%d/%m/%Y")

# Preview
if selected_items:
    st.markdown("---")
    st.write("### Preview")
    st.table({"Item": [n for n, _ in selected_items], "Quantity": [q for _, q in selected_items]})
    st.markdown(f"**Total Price:** ₹ {total_price:,.0f}")
    if doc_type == "Quotation Summary":
        st.markdown(f"**Subsidy:** ₹ {subsidy:,.0f}")
    st.markdown(f"**Final Price:** ₹ {final_price:,.0f}")

# ─────────────────────────────────────────────────────────────────────
#  3.  Generate DOCX
# ─────────────────────────────────────────────────────────────────────
st.markdown("---")
if st.button(f"Generate {doc_type} DOCX"):
    if not selected_items:
        st.error("Please enter quantities for at least one item.")
        st.stop()
    if not (doc_no and customer_name and customer_address and customer_phone):
        st.error("Please fill all mandatory customer fields.")
        st.stop()
    if len(customer_phone) != 10:
        st.error("Phone number must be exactly 10 digits.")
        st.stop()
    if "Proforma" in doc_type and not amount_received:
        st.error("Amount Received is required for Proforma receipts.")
        st.stop()

    # Context
    context = {
        "quotation_no": doc_no,
        "receipt_no":   doc_no,
        "date":         date,
        "customer_name":  customer_name,
        "address_line1":  customer_address,
        "phone":         customer_phone,
        "email":         customer_email or "N/A",
        "total_price":   f"{total_price:,.0f}",
        "subsidy":       f"{subsidy:,.0f}",
        "final_price":   f"{final_price:,.0f}",
        "amount_received": amount_received,
        "payment_mode":    payment_mode,
        "reference_id":    reference_id or "N/A",
        "payment_date":    payment_date,
        "balance_due":     balance_due,
        "tentative_delivery": tentative_delivery,
        "delivery_date":   delivery_date,
    }

    # Quantities: default blank; fill only if qty>0
    for ph in PLACEHOLDERS.values():
        context[ph] = "0"                         # BLANK, not zero
    for name, qty in selected_items:
        context[PLACEHOLDERS[name]] = qty        # overwrite for >0

    # Bold text where useful
    for k in [
        "quotation_no","receipt_no","customer_name","address_line1","phone","email",
        "amount_received","payment_mode","reference_id","payment_date",
        "balance_due","tentative_delivery","delivery_date"
    ]:
        if context.get(k):
            context[k] = RichText(str(context[k]), bold=True)

    tpl = DocxTemplate(TEMPLATES[doc_type])
    tpl.render(context)
    buf = BytesIO()
    tpl.save(buf)
    buf.seek(0)

    st.success("DOCX generated successfully.")
    st.download_button(
        "⬇️ Download DOCX",
        data=buf,
        file_name=f"{doc_type.replace(' ', '_')}_{doc_no}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
