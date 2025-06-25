import streamlit as st

"""
Orbit Document Generator  — unified script
✓ Quotation Summary
✓ Partial Proforma Receipt (advance)
✓ Full Proforma Receipt
Each branch exports DOCX + PDF (docx2pdf first, ReportLab fallback).
Template files expected in the working directory:
  • Orbit_Agritech_Quotation_Summary_Template.docx
  • Orbit_Agritech_Partial_Proforma_Receipt.docx
  • Orbit_Agritech_Full_Proforma_Receipt.docx
A4 letter-pad image: letterpad design-01.jpg
"""

# --------------------------------------------------------------------
#  General page config
# --------------------------------------------------------------------
st.set_page_config(page_title="Orbit Docs Generator", layout="wide")
st.title("Orbit Document Generator")

# --------------------------------------------------------------------
#  Sidebar selector
# --------------------------------------------------------------------
DOC_TYPE = st.radio(
    "Select Document Type:",
    [
        "Quotation Summary",
        "Partial Proforma Receipt",  # advance / part-payment
        "Full Proforma Receipt",     # full-payment
    ],
)

# ════════════════════════════════════════════════════════════════════
#  Shared helpers & constants
# ════════════════════════════════════════════════════════════════════
from datetime import datetime
from io import BytesIO
from PIL import Image
from docxtpl import DocxTemplate, RichText
from docx2pdf import convert
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import os

# --- product catalogue ------------------------------------------------
ITEMS_MASTER = [
    {"name": "12 HP PT Pro",                           "price": 112_000},
    {"name": "Battery Sets",                           "price":  56_000},
    {"name": "Fast Chargers",                          "price":   6_500},
    {"name": "1 Set of Sugarcane Blades (Weeding)",    "price":   4_400},
    {"name": "1 Set of Sugarcane Blades (Earthing-up)", "price":  4_400},
    {"name": "1 Set of Tyres (5×10)",                  "price":   8_000},
    {"name": "Toolkit",                                "price":   1_200},
    {"name": "Ginger Kit",                             "price":  10_000},
    {"name": "Seat",                                   "price":   6_500},
    {"name": "Jack",                                   "price":   1_100},
    {"name": "BuyBack Guarantee",                      "price":  10_000},
    {"name": "Front Dead Weight",                      "price":      0},  # price TBD
    {"name": "Wheel Dead Weight",                      "price":      0},  # price TBD
]

# --- role-wise subsidy caps (single- / double-battery) ---------------
SUBSIDY_CAPS = {
    "Telecaller":                    (55_000, 75_000),
    "Business Development Officer":  (60_000, 80_000),
    "Manager":                       (65_000, 85_000),
    "Co-Founder":                   (100_000, 120_000),
}

LETTER_PAD   = "letterpad design-01.jpg"
CURRENT_YEAR = datetime.today().year

# ════════════════════════════════════════════════════════════════════
#  Utility: make PDF from simple letter-pad (fallback when docx2pdf fails)
# ════════════════════════════════════════════════════════════════════
def fallback_pdf(title: str, header_lines: list[str], outfile: BytesIO | None = None):
    """Return BytesIO containing a one-page branded PDF."""
    buf = outfile or BytesIO()
    c   = canvas.Canvas(buf, pagesize=A4)
    c.drawImage(ImageReader(LETTER_PAD), 0, 0, width=A4[0], height=A4[1])

    y = 760
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, title)
    c.setFont("Helvetica", 10)
    y -= 25
    for line in header_lines:
        c.drawString(50, y, line)
        y -= 15
    c.drawString(50, y - 15, "Authorised Signatory")
    c.save()
    buf.seek(0)
    return buf

# ════════════════════════════════════════════════════════════════════
#  1 · QUOTATION SUMMARY  (unchanged except Toolkit rename done earlier)
# ════════════════════════════════════════════════════════════════════
if DOC_TYPE == "Quotation Summary":
    # ─────────────────────────────────────────────────────────────
    # 1. Customer & role input
    # ─────────────────────────────────────────────────────────────
    st.subheader("Customer Information")
    quotation_no   = st.text_input("Quotation Number (4 digits)", max_chars=4)
    customer_name  = st.text_input("Customer Name *")
    customer_addr  = st.text_area("Address *")
    customer_phone = st.text_input("Phone Number *")

    st.subheader("Who is filling this form? *")
    role = st.selectbox("Select Role", ["", *SUBSIDY_CAPS.keys()])

    # ─────────────────────────────────────────────────────────────
    # 2. Item quantities
    # ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("Enter Quantities for Items (Minimum quantities enforced)")

    def qty(label: str, min_val: int, key: str):
        return st.number_input(label, min_value=min_val, value=min_val, step=1, key=key)

    q_pt   = qty("12 HP PT Pro",                                         1, "q_pt")
    q_bat  = qty("Battery Sets",                                         2, "q_bat")
    q_chg  = qty("Fast Chargers",                                        2, "q_chg")
    q_bw   = qty("1 Set of Sugarcane Blades (Weeding)",                  1, "q_bw")
    q_be   = qty("1 Set of Sugarcane Blades (Earthing-up)",              1, "q_be")
    q_ty   = qty("1 Set of Tyres (5×10)",                                1, "q_ty")
    q_tk   = qty("Toolkit",                                              1, "q_tk")
    q_gk   = qty("Ginger Kit",                                           0, "q_gk")
    q_st   = qty("Seat",                                                 1, "q_st")
    q_jk   = qty("Jack",                                                 0, "q_jk")
    q_bb   = qty("BuyBack Guarantee",                                    0, "q_bb")
    q_fdw  = qty("Front Dead Weight",                                    0, "q_fdw")
    q_wdw  = qty("Wheel Dead Weight",                                    0, "q_wdw")

    # ─────────────────────────────────────────────────────────────
    # 3. Price maths
    # ─────────────────────────────────────────────────────────────
    PRICE = {item["name"]: item["price"] for item in ITEMS_MASTER}

    qty_table = [
        ("12 HP PT Pro",                                q_pt),
        ("Battery Sets",                                q_bat),
        ("Fast Chargers",                               q_chg),
        ("1 Set of Sugarcane Blades (Weeding)",         q_bw),
        ("1 Set of Sugarcane Blades (Earthing-up)",     q_be),
        ("1 Set of Tyres (5×10)",                       q_ty),
        ("Toolkit",                                     q_tk),
        ("Ginger Kit",                                  q_gk),
        ("Seat",                                        q_st),
        ("Jack",                                        q_jk),
        ("BuyBack Guarantee",                           q_bb),
        ("Front Dead Weight",                           q_fdw),
        ("Wheel Dead Weight",                           q_wdw),
    ]

    selected_items = [{"name": n, "qty": q} for n, q in qty_table if q > 0]
    total_price    = sum(PRICE[n] * q for n, q in qty_table)
    battery_qty    = q_bat  # for subsidy logic

    # ─────────────────────────────────────────────────────────────
    # 4. Subsidy calculation (unchanged logic)
    # ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.write("### 💸 Subsidy Options")
    apply_subsidy = st.radio("Apply a Subsidy?", ("No", "Yes"))

    if "selected_subsidy" not in st.session_state:
        st.session_state.selected_subsidy = 0

    if apply_subsidy == "Yes" and role:
        cap_single, cap_double = SUBSIDY_CAPS[role]
        max_subsidy = cap_single if battery_qty <= 1 else cap_double
        st.slider("Subsidy Slider", 0, max_subsidy, step=1_000, key="selected_subsidy")
    else:
        st.session_state.selected_subsidy = 0

    subsidy     = st.session_state.selected_subsidy
    final_price = total_price - subsidy

    # ─────────────────────────────────────────────────────────────
    # 5. Bill preview
    # ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.write("### 📟 Bill Summary")

    if not selected_items:
        st.info("Enter at least one quantity to proceed.")
        st.stop()

    st.table({
        "Item Name": [i["name"] for i in selected_items],
        "Quantity":  [i["qty"]  for i in selected_items],
    })
    st.write(f"**Total Price:** ₹ {total_price:,.0f}")
    st.write(f"**Subsidy Applied:** ₹ {subsidy:,.0f}")
    st.write(f"**Subsidised Price (All Inclusive):** ₹ {final_price:,.0f}")

    # ─────────────────────────────────────────────────────────────
    # 6. File generation
    # ─────────────────────────────────────────────────────────────
    if st.button("📄 Generate Quotation (DOCX + PDF)"):
        if not quotation_no.isdigit():
            st.error("Quotation number must be numeric (4 digits).")
            st.stop()

        ctx = {
            "quotation_no": quotation_no,
            "date": datetime.today().strftime("%d/%m/%Y"),
            "customer_name": RichText(customer_name, bold=True),
            "address_line1": RichText(customer_addr, bold=True),
            "phone": RichText(customer_phone, bold=True),
            # quantities
            "quantity_pt_pro":             q_pt,
            "quantity_battery":            q_bat,
            "quantity_charger":            q_chg,
            "quantity_blade_weeding":      q_bw,
            "quantity_blade_earthing":     q_be,
            "quantity_tyres":              q_ty,
            "quantity_toolkit":            q_tk,
            "quantity_ginger":             q_gk,
            "quantity_seat":               q_st,
            "quantity_jack":               q_jk,
            "quantity_buyback_guarantee":  q_bb,
            "quantity_front_dead_weight":  q_fdw,
            "quantity_wheel_dead_weight":  q_wdw,
            # price fields
            "total_price": f"{total_price:,.0f}",
            "subsidy": f"{subsidy:,.0f}",
            "final_price": f"{final_price:,.0f}",
        }

        TEMPLATE   = "Orbit_Agritech_Quotation_Summary_Template.docx"
        doc        = DocxTemplate(TEMPLATE)
        doc.render(ctx)
        docx_file  = f"Orbit_Agritech_Quotation_{quotation_no}.docx"
        doc.save(docx_file)

        with open(docx_file, "rb") as f:
            st.download_button(
                "⬇️ Download DOCX Quotation",
                f,
                docx_file,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

        # try DOCX → PDF
        pdf_file = docx_file.replace(".docx", ".pdf")
        try:
            convert(docx_file, pdf_file)
            pdf_stream = open(pdf_file, "rb")
        except Exception:
            header = [
                f"Quotation No: ORBIT/{CURRENT_YEAR}/1/{quotation_no}  Date: {ctx['date']}",
                f"Customer: {customer_name}",
                f"Address: {customer_addr}",
                f"Phone: {customer_phone}",
                f"Total Price: ₹ {total_price:,.0f}",
                f"Subsidy: ₹ {subsidy:,.0f}",
                f"Subsidised Price: ₹ {final_price:,.0f}",
            ]
            pdf_stream = fallback_pdf("Quotation Summary", header)
            pdf_file   = "Orbit_Quotation.pdf"

        st.download_button(
            "⬇️ Download PDF Quotation",
            pdf_stream,
            file_name=os.path.basename(pdf_file),
            mime="application/pdf",
        )

# ════════════════════════════════════════════════════════════════════
#  2 · PARTIAL PROFORMA RECEIPT (Advance Payment)
# ════════════════════════════════════════════════════════════════════
elif DOC_TYPE == "Partial Proforma Receipt":
    st.subheader("Proforma Receipt (Advance) Generator")

    # ---------- helper for numeric text fields ----------
    def num_input(label, max_len, key=None):
        val = st.text_input(label, key=key)
        return ''.join(filter(str.isdigit, val))[:max_len]

    # ---------- core fields ----------
    receipt_no  = num_input("Receipt Number (Enter 4 digits)", 4, "adv_no")
    date        = st.date_input("Date", datetime.today()).strftime("%d/%m/%Y")
    cust_name   = st.text_input("Customer Name", max_chars=50)
    address     = st.text_input("Address", max_chars=200)
    phone       = num_input("Phone Number (10 digits)", 10, "adv_phone")
    email       = st.text_input("Email (optional)")

    amount_rec  = st.text_input("Amount Received (₹)")

    pay_mode    = st.selectbox("Payment Mode", ["Cashfree", "Cash", "Other"])
    if pay_mode == "Other":
        pay_mode = st.text_input("Enter Other Mode", key="adv_other") or "Other"

    reference_id = st.text_input("Reference ID (optional)")
    pay_date     = st.date_input("Date of Payment", datetime.today()).strftime("%d/%m/%Y")
    balance_due  = st.text_input("Balance Due (₹)")
    tentative_del= st.date_input("Tentative Delivery Date", datetime.today()).strftime("%d/%m/%Y")

    st.markdown("---")
    st.subheader("Enter Quantities for Items (Minimum quantities enforced)")

    def qty(label, min_val, key):
        return st.number_input(label, min_value=min_val, value=min_val, step=1, key=key)

    q_pt   = qty("12 HP PT Pro",                                   1, "adv_q_pt")
    q_bat  = qty("Battery Sets",                                   2, "adv_q_bat")
    q_chg  = qty("Fast Chargers",                                  2, "adv_q_chg")
    q_bw   = qty("1 Set of Sugarcane Blades(Weeding)",             1, "adv_q_bw")
    q_be   = qty("1 Set of Sugarcane Blades(Earthing-up)",         1, "adv_q_be")
    q_ty   = qty("1 Set of Tyres (5×10)",                          1, "adv_q_ty")
    q_tk   = qty("Toolkit",                                        1, "adv_q_tk")
    q_gk   = qty("Ginger Kit",                                     0, "adv_q_gk")
    q_st   = qty("Seat",                                           1, "adv_q_st")
    q_jk   = qty("Jack",                                           0, "adv_q_jk")
    q_bb   = qty("BuyBack Guarantee",                              0, "adv_q_bb")
    q_fdw  = qty("Front Dead Weight",                              0, "adv_q_fdw")
    q_wdw  = qty("Wheel Dead Weight",                              0, "adv_q_wdw")

    if st.button("Generate Receipt (DOCX + PDF)"):
        if not receipt_no:
            st.error("Receipt Number is required (numeric up to 5 digits).")
            st.stop()
        if len(phone) != 10:
            st.error("Phone Number must be exactly 10 digits.")
            st.stop()

        ctx = {
            "receipt_no": RichText(receipt_no, bold=True),
            "date": RichText(date, bold=True),
            "customer_name": RichText(cust_name, bold=True),
            "address_line1": RichText(address, bold=True),
            "phone": RichText(phone, bold=True),
            "email": RichText(email or "N/A", bold=True),
            "amount_received": RichText(amount_rec, bold=True),
            "payment_mode": RichText(pay_mode, bold=True),
            "reference_id": RichText(reference_id or "N/A", bold=True),
            "payment_date": RichText(pay_date, bold=True),
            "balance_due": RichText(balance_due, bold=True),
            "tentative_delivery": RichText(tentative_del, bold=True),
            "quantity_pt_pro":            q_pt,
            "quantity_battery":           q_bat,
            "quantity_charger":           q_chg,
            "quantity_blade_weeding":     q_bw,
            "quantity_blade_earthing":    q_be,
            "quantity_tyres":             q_ty,
            "quantity_toolkit":           q_tk,
            "quantity_ginger":            q_gk,
            "quantity_seat":              q_st,
            "quantity_jack":              q_jk,
            "quantity_buyback_guarantee": q_bb,
            "quantity_front_dead_weight": q_fdw,
            "quantity_wheel_dead_weight": q_wdw,
        }

        TEMPLATE  = "Orbit_Agritech_Partial_Proforma_Receipt.docx"
        doc       = DocxTemplate(TEMPLATE)
        doc.render(ctx)
        docx_name = f"Orbit_Agritech_Proforma_Receipt_{receipt_no}.docx"
        doc.save(docx_name)

        with open(docx_name, "rb") as f:
            st.download_button("⬇️ Download DOCX Receipt", f, docx_name,
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        # PDF conversion
        pdf_name = docx_name.replace(".docx", ".pdf")
        try:
            convert(docx_name, pdf_name)
            pdf_handle = open(pdf_name, "rb")
        except Exception:
            hdr = [
                f"Receipt No: ORBIT/{CURRENT_YEAR}/1/{receipt_no}    Date: {date}",
                f"Customer: {cust_name}",
                f"Amount Received: ₹ {amount_rec}/-  Mode: {pay_mode}",
            ]
            pdf_handle = fallback_pdf("Proforma Receipt (Advance Payment)", hdr)
            pdf_name   = "Orbit_Proforma_Receipt.pdf"

        st.download_button("⬇️ Download PDF Receipt", pdf_handle,
                           file_name=os.path.basename(pdf_name), mime="application/pdf")

# ════════════════════════════════════════════════════════════════════
#  3 · FULL PROFORMA RECEIPT
# ════════════════════════════════════════════════════════════════════
elif DOC_TYPE == "Full Proforma Receipt":
    st.subheader("Full Payment Receipt Generator")

    def num_in(label, max_len, key=None):
        val = st.text_input(label, key=key)
        return ''.join(filter(str.isdigit, val))[:max_len]

    r_no  = num_in("Receipt Number (Enter 4 digits)", 4, "full_no")
    date  = st.date_input("Date", datetime.today()).strftime("%d/%m/%Y")
    cname = st.text_input("Customer Name", max_chars=50)
    addr  = st.text_input("Address", max_chars=200)
    phone = num_in("Phone Number (10 digits)", 10, "full_phone")
    email = st.text_input("Email (optional)")

    amount = st.text_input("Amount Received (₹)")

    p_mode = st.selectbox("Payment Mode", ["Cashfree", "Cash", "Other"])
    if p_mode == "Other":
        p_mode = st.text_input("Enter Other Mode", key="full_other") or "Other"

    ref_id = st.text_input("Reference ID (optional)")
    pay_dt = st.date_input("Date of Payment", datetime.today()).strftime("%d/%m/%Y")
    del_dt = st.date_input("Delivery Date", datetime.today()).strftime("%d/%m/%Y")

    st.markdown("---")
    st.subheader("Enter Quantities for Items (Minimum quantities enforced)")

    def q(label, minv, key):
        return st.number_input(label, min_value=minv, value=minv, step=1, key=key)

    q_pt   = q("12 HP PT Pro",                        1, "full_q_pt")
    q_bat  = q("Battery Sets",                        2, "full_q_bat")
    q_chg  = q("Fast Chargers",                       2, "full_q_chg")
    q_bw   = q("1 Set Sugarcane Blades–Weeding",      1, "full_q_bw")
    q_be   = q("1 Set Sugarcane Blades–Earthing",     1, "full_q_be")
    q_ty   = q("1 Set Tyres (5×10)",                  1, "full_q_ty")
    q_tk   = q("Toolkit",                             1, "full_q_tk")
    q_gk   = q("Ginger Kit",                          0, "full_q_gk")
    q_st   = q("Seat",                                1, "full_q_st")
    q_jk   = q("Jack",                                0, "full_q_jk")
    q_bb   = q("BuyBack Guarantee",                   0, "full_q_bb")
    q_fdw  = q("Front Dead Weight",                   0, "full_q_fdw")
    q_wdw  = q("Wheel Dead Weight",                   0, "full_q_wdw")

    if st.button("Generate Full-Payment Receipt (DOCX + PDF)"):
        if not r_no:
            st.error("Receipt Number required (numeric up to 5 digits).")
            st.stop()
        if len(phone) != 10:
            st.error("Phone Number must be 10 digits.")
            st.stop()

        ctx = {
            "receipt_no": RichText(r_no, bold=True),
            "date": RichText(date, bold=True),
            "customer_name": RichText(cname, bold=True),
            "address_line1": RichText(addr, bold=True),
            "phone": RichText(phone, bold=True),
            "email": RichText(email or "N/A", bold=True),
            "amount_received": RichText(amount, bold=True),
            "payment_mode": RichText(p_mode, bold=True),
            "reference_id": RichText(ref_id or "N/A", bold=True),
            "payment_date": RichText(pay_dt, bold=True),
            "delivery_date": RichText(del_dt, bold=True),
            "quantity_pt_pro":            q_pt,
            "quantity_battery":           q_bat,
            "quantity_charger":           q_chg,
            "quantity_blade_weeding":     q_bw,
            "quantity_blade_earthing":    q_be,
            "quantity_tyres":             q_ty,
            "quantity_toolkit":           q_tk,
            "quantity_ginger":            q_gk,
            "quantity_seat":              q_st,
            "quantity_jack":              q_jk,
            "quantity_buyback_guarantee": q_bb,
            "quantity_front_dead_weight": q_fdw,
            "quantity_wheel_dead_weight": q_wdw,
        }

        TEMPLATE  = "Orbit_Agritech_Full_Proforma_Receipt.docx"
        doc       = DocxTemplate(TEMPLATE)
        doc.render(ctx)
        docx_name = f"Orbit_Agritech_Proforma_Receipt_{r_no}_FULL.docx"
        doc.save(docx_name)

        with open(docx_name, "rb") as f:
            st.download_button("⬇️ Download DOCX Receipt", f, docx_name,
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        pdf_name = docx_name.replace(".docx", ".pdf")
        try:
            convert(docx_name, pdf_name)
            pdf_handle = open(pdf_name, "rb")
        except Exception:
            hdr = [
                f"Receipt No: ORBIT/{CURRENT_YEAR}/1/{r_no}    Date: {date}",
                f"Customer: {cname}",
                f"Amount Received: ₹ {amount}/-  Mode: {p_mode}",
            ]
            pdf_handle = fallback_pdf("Proforma Receipt (Full Payment)", hdr)
            pdf_name   = "Orbit_Receipt.pdf"

        st.download_button("⬇️ Download PDF Receipt", pdf_handle,
                           file_name=os.path.basename(pdf_name), mime="application/pdf")
