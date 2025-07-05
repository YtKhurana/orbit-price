import streamlit as st
# The following imports are moved to their respective sections
# to maintain the original structure of your code.

# App Title and Selector
st.set_page_config(page_title="Orbit Docs Generator", layout="wide")
st.title("Orbit Document Generator")

# App Selector
option = st.radio("Select Document Type:", ["Quotation Summary", "Partial Proforma Receipt", "Full Proforma Receipt" ])

# ----------------------------------------------------------------------
# Option 1: Quotation Summary (MODIFIED)
# ----------------------------------------------------------------------
if option == "Quotation Summary":
    from docxtpl import DocxTemplate
    from datetime import datetime

    TEMPLATE_PATH = "Orbit Agritech Quotation Summary.docx"

    if "selected_subsidy" not in st.session_state:
        st.session_state.selected_subsidy = 0

    if "form_filled_by" not in st.session_state:
        st.session_state.form_filled_by = ""

    st.subheader("Customer Information")

    def numeric_input(label, max_length, key=None):
        val = st.text_input(label, key=key)
        val = ''.join(filter(str.isdigit, val))[:max_length]
        return val

    receipt_no = numeric_input("Quotation Number (4 digits)", max_length=4, key="quote_receipt_no")
    date = st.date_input("Date", datetime.today(), key="quote_date").strftime("%d/%m/%Y")
    customer_name = st.text_input("Customer Name *", key="quote_customer_name")
    customer_address = st.text_area("Address *", key="quote_address")
    customer_phone = numeric_input("Phone Number * (10 digits)", max_length=10, key="quote_phone")
    email = st.text_input("Email (optional)", max_chars=50, key="quote_email")

    st.subheader("Who is filling this form? *")
    form_filled_by = st.selectbox("Select Role", ["", "Telecaller", "Business Development Officer", "Manager", "Co-Founder"], key="quote_filler")
    st.session_state.form_filled_by = form_filled_by

    subsidy_caps = {
        "Telecaller": (55000, 75000),
        "Business Development Officer": (60000, 80000),
        "Manager": (65000, 85000),
        "Co-Founder": (100000, 120000),
    }
    
    # Master list of all items with their properties
    items = [
        {"name": "12 HP PT Pro", "price": 112000, "key": "quantity_pt_pro"},
        {"name": "Battery Sets", "price": 56000, "key": "quantity_battery"},
        {"name": "Fast Chargers", "price": 6500, "key": "quantity_charger"},
        {"name": "1 Set of Sugarcane Blades(Weeding)", "price": 4400, "key": "quantity_blade_weeding"},
        {"name": "1 Set of Sugarcane Blades(Earthing-up)", "price": 4400, "key": "quantity_blade_earthing"},
        {"name": "1 Set of Tyres (5x10)", "price": 8000, "key": "quantity_tyres"},
        {"name": "Toolkit", "price": 1200, "key": "quantity_toolkit"},
        {"name": "Ginger Kit", "price": 10000, "key": "quantity_ginger"},
        {"name": "Seat", "price": 6500, "key": "quantity_seat"},
        {"name": "Jack", "price": 1100, "key": "quantity_jack"},
        {"name": "BuyBack Guarantee", "price": 10000, "key": "quantity_buyback_guarantee"},
        {"name":"Front Dead Weight", "price": 0, "key": "quantity_front_dead_weight"},
        {"name":"Wheel Dead Weight", "price": 0, "key": "quantity_wheel_dead_weight"},
    ]

    st.markdown("---")
    st.subheader("Enter Quantities for Items")

    # Static UI for item selection, similar to proforma receipts
    quantity_pt_pro = st.number_input("12 HP PT Pro", min_value=0, step=1, value=1, key="quote_qty_pt_pro")
    quantity_battery = st.number_input("Battery Sets", min_value=0, step=1, value=1, key="quote_qty_battery")
    quantity_charger = st.number_input("Fast Chargers", min_value=0, step=1, value=2, key="quote_qty_charger")
    quantity_blade_weeding = st.number_input("1 Set of Sugarcane Blades(Weeding)", min_value=0, step=1, value=0, key="quote_qty_blade_weeding")
    quantity_blade_earthing = st.number_input("1 Set of Sugarcane Blades(Earthing-up)", min_value=0, step=1, value=0, key="quote_qty_blade_earthing")
    quantity_tyres = st.number_input("1 Set of Tyres (5x10)", min_value=0, step=1, value=0, key="quote_qty_tyres")
    quantity_toolkit = st.number_input("Toolkit", min_value=0, step=1, value=0, key="quote_qty_toolkit")
    quantity_ginger = st.number_input("Ginger Kit", min_value=0, step=1, value=0, key="quote_qty_ginger")
    quantity_seat = st.number_input("Seat", min_value=0, step=1, value=0, key="quote_qty_seat")
    quantity_jack = st.number_input("Jack", min_value=0, step=1, value=0, key="quote_qty_jack")
    quantity_buyback_guarantee = st.number_input("BuyBack Guarantee", min_value=0, step=1, value=0, key="quote_qty_buyback_guarantee")
    quantity_front_dead_weight = st.number_input("Front Dead Weight", min_value=0, step=1, value=0, key="quote_qty_front_dead_weight")
    quantity_wheel_dead_weight = st.number_input("Wheel Dead Weight", min_value=0, step=1, value=0, key="quote_qty_wheel_dead_weight")

    # Consolidate quantities into a dictionary for processing
    quantities = {
        "quantity_pt_pro": quantity_pt_pro,
        "quantity_battery": quantity_battery,
        "quantity_charger": quantity_charger,
        "quantity_blade_weeding": quantity_blade_weeding,
        "quantity_blade_earthing": quantity_blade_earthing,
        "quantity_tyres": quantity_tyres,
        "quantity_toolkit": quantity_toolkit,
        "quantity_ginger": quantity_ginger,
        "quantity_seat": quantity_seat,
        "quantity_jack": quantity_jack,
        "quantity_buyback_guarantee": quantity_buyback_guarantee,
        "quantity_front_dead_weight": quantity_front_dead_weight,
        "quantity_wheel_dead_weight": quantity_wheel_dead_weight,
    }

    # Calculate total price and create summary list for UI table
    total_price = 0
    selected_items_summary = []
    for item in items:
        qty = quantities.get(item["key"], 0)
        if qty > 0:
            total_price += qty * item["price"]
            selected_items_summary.append({"name": item["name"], "qty": qty})
    
    battery_qty = quantities.get("quantity_battery", 0)

    st.markdown("---")
    st.write("### 💸 Subsidy Options")

    apply_subsidy = st.radio("Do you want to apply a Subsidy?", ("No", "Yes"), key="quote_subsidy_radio")

    if apply_subsidy == "Yes" and form_filled_by:
        st.markdown("#### Select Subsidy Amount")
        single_cap, double_cap = subsidy_caps[form_filled_by]
        max_subsidy = single_cap if battery_qty <= 1 else double_cap
        st.slider(
            "Subsidy Slider",
            min_value=0,
            max_value=max_subsidy,
            step=1000,
            key="selected_subsidy"
        )
        st.success(f"Selected Subsidy: ₹{st.session_state.selected_subsidy:,.0f}")
    else:
        st.session_state.selected_subsidy = 0

    selected_subsidy = st.session_state.selected_subsidy
    final_price = total_price - selected_subsidy

    st.markdown("---")
    st.write("### 📟 Bill Summary")

    if selected_items_summary:
        st.table({
            "Item Name": [item["name"] for item in selected_items_summary],
            "Quantity": [item["qty"] for item in selected_items_summary]
        })

        st.write(f"**Total Price:** Rs {total_price:,.0f}")
        st.write(f"**Subsidy Applied:** Rs {selected_subsidy:,.0f}")
        st.write(f"**Subsidized Price (All Inclusive):** Rs {final_price:,.0f}")

        if st.button("📄 Generate Quotation DOCX"):
            if not receipt_no:
                st.error("Quotation Number is required and must be numeric up to 4 digits.")
            elif len(customer_phone) != 10:
                st.error("Phone Number must be exactly 10 digits.")
            else:
                doc = DocxTemplate(TEMPLATE_PATH)
                context = {
                    "receipt_no": receipt_no,
                    "date": date,
                    "customer_name": customer_name,
                    "address_line1": customer_address,
                    "phone": customer_phone,
                    "email": email if email else "N/A",
                    "total_price": f"Rs {total_price:,.0f}",
                    "subsidy": f"Rs {selected_subsidy:,.0f}",
                    "final_price": f"Rs {final_price:,.0f}",
                }
                context.update(quantities)

                try:
                    doc.render(context)
                    output_filename = f"Orbit_Agritech_Quotation_{receipt_no}.docx"
                    doc.save(output_filename)
                    st.success(f"Quotation generated: {output_filename}")

                    with open(output_filename, "rb") as file:
                        st.download_button(
                            label="⬇️ Click here to Download DOCX Quotation",
                            data=file,
                            file_name=output_filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                except Exception as e:
                    st.error("❌ Error rendering document. Make sure 'Orbit Agritech Quotation Summary.docx' is in the same directory.")
                    st.exception(e)
    else:
        st.info("Please enter quantities for items to see the bill.")

# ----------------------------------------------------------------------
# Option 2: Proforma Receipt
# ----------------------------------------------------------------------
elif option == "Partial Proforma Receipt":
    from docxtpl import DocxTemplate
    from datetime import datetime

    TEMPLATE_PATH = "Orbit Agritech Proforma Receipt Partial.docx"

    st.subheader("Proforma Receipt Generator")

    def numeric_input(label, max_length, key=None):
        val = st.text_input(label, key=key)
        val = ''.join(filter(str.isdigit, val))[:max_length]
        return val

    receipt_no = numeric_input("Receipt Number (4 digits)", max_length=4, key="receipt_no")
    date = st.date_input("Date", datetime.today(), key="date").strftime("%d/%m/%Y")
    customer_name = st.text_input("Customer Name", max_chars=50, key="customer_name")
    address_line1 = st.text_input("Address", max_chars=200, key="address_line1")
    phone = numeric_input("Phone Number (10 digits)", max_length=10, key="phone")
    email = st.text_input("Email (optional)", max_chars=50, key="email")
    amount_received = st.text_input("Amount Received (₹)", max_chars=10, key="amount_received")

    st.markdown("**Payment Mode:**")
    payment_mode = st.selectbox("", ["Cashfree", "Cash", "Other"], key="payment_mode")

    if payment_mode == "Other":
        custom_payment_mode = st.text_input("Enter Other Payment Mode", key="custom_payment_mode")
        final_payment_mode = custom_payment_mode.strip() if custom_payment_mode else "Other"
    else:
        final_payment_mode = payment_mode

    reference_id = st.text_input("Reference ID (optional)", max_chars=20, key="reference_id")
    payment_date = st.date_input("Date of Payment", datetime.today(), key="payment_date").strftime("%d/%m/%Y")
    balance_due = st.text_input("Balance Due (Rs.)", max_chars=10, key="balance_due")
    tentative_delivery = st.date_input("Tentative Delivery Date", datetime.today(), key="tentative_delivery").strftime("%d/%m/%Y")

    st.markdown("---")
    st.subheader("Enter Quantities for Items (Minimum quantities enforced)")

    quantity_pt_pro = st.number_input(
        "12 HP PT Pro", min_value=0, step=1, value=1, key="qty_pt_pro"
    )
    quantity_battery = st.number_input(
        "Battery Sets", min_value=0, step=1, value=1, key="qty_battery"
    )
    quantity_charger = st.number_input(
        "Fast Chargers", min_value=0, step=1, value=2, key="qty_charger"
    )
    quantity_blade_weeding = st.number_input(
        "1 Set of Sugarcane Blades(Weeding)", min_value=0, step=1, value=0, key="qty_blade_weeding"
    )
    quantity_blade_earthing = st.number_input(
        "1 Set of Sugarcane Blades(Earthing-up)", min_value=0, step=1, value=0, key="qty_blade_earthing"
    )
    quantity_tyres = st.number_input(
        "1 Set of Tyres (5x10)", min_value=0, step=1, value=0, key="qty_tyres"
    )
    quantity_toolkit = st.number_input(
        "Toolkit", min_value=0, step=1, value=0, key="qty_toolkit"
    )
    quantity_ginger = st.number_input(
        "Ginger Kit", min_value=0, step=1, value=0, key="qty_ginger"
    )
    quantity_seat = st.number_input(
        "Seat", min_value=0, step=1, value=0, key="qty_seat"
    )
    quantity_jack = st.number_input(
        "Jack", min_value=0, step=1, value=0, key="qty_jack"
    )
    quantity_buyback_guarantee = st.number_input(
        "BuyBack Guarantee", min_value=0, step=1, value=0, key="qty_buyback_guarantee"
    )
    quantity_front_dead_weight = st.number_input(
        "Front Dead Weight", min_value=0, step=1, value=0, key="qty_front_dead_weight"
    )
    quantity_wheel_dead_weight = st.number_input(
        "Wheel Dead Weight", min_value=0, step=1, value=0, key="qty_wheel_dead_weight"
    )

    if st.button("Generate Receipt DOCX"):
        if not receipt_no:
            st.error("Receipt Number is required and must be numeric up to 4 digits.")
        elif len(phone) != 10:
            st.error("Phone Number must be exactly 10 digits.")
        else:
            doc = DocxTemplate(TEMPLATE_PATH)

            context = {
                "receipt_no": receipt_no,
                "date": date,
                "customer_name": customer_name,
                "address_line1": address_line1,
                "phone": phone,
                "email": email if email else "N/A",
                "amount_received": amount_received,
                "payment_mode": final_payment_mode,
                "reference_id": reference_id if reference_id else "N/A",
                "payment_date": payment_date,
                "balance_due": balance_due,
                "tentative_delivery": tentative_delivery,

                # Quantities passed as placeholders
                "quantity_pt_pro": quantity_pt_pro,
                "quantity_battery": quantity_battery,
                "quantity_charger": quantity_charger,
                "quantity_blade_weeding": quantity_blade_weeding,
                "quantity_blade_earthing": quantity_blade_earthing,
                "quantity_tyres": quantity_tyres,
                "quantity_toolkit": quantity_toolkit,
                "quantity_ginger": quantity_ginger,
                "quantity_seat": quantity_seat,
                "quantity_jack": quantity_jack,
                "quantity_buyback_guarantee": quantity_buyback_guarantee,
                "quantity_front_dead_weight": quantity_front_dead_weight,
                "quantity_wheel_dead_weight": quantity_wheel_dead_weight
            }

            try:
                doc.render(context)
                output_filename = f"Orbit_Agritech_Proforma_Receipt_{receipt_no}.docx"
                doc.save(output_filename)
                st.success(f"Receipt generated: {output_filename}")

                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="Download Receipt DOCX",
                        data=file,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error("❌ Error rendering document.")
                st.exception(e)

# ----------------------------------------------------------------------
# Option 3: FULL Proforma Receipt
# ----------------------------------------------------------------------
elif option == "Full Proforma Receipt":
    from docxtpl import DocxTemplate
    from datetime import datetime

    TEMPLATE_PATH = "Orbit Agritech Proforma Receipt Full.docx"

    st.subheader("Proforma Receipt Generator")

    def numeric_input(label, max_length, key=None):
        val = st.text_input(label, key=key)
        val = ''.join(filter(str.isdigit, val))[:max_length]
        return val

    receipt_no = numeric_input("Receipt Number (4 digits)", max_length=4, key="receipt_no")
    date = st.date_input("Date", datetime.today(), key="date").strftime("%d/%m/%Y")
    customer_name = st.text_input("Customer Name", max_chars=50, key="customer_name")
    address_line1 = st.text_input("Address", max_chars=200, key="address_line1")
    phone = numeric_input("Phone Number (10 digits)", max_length=10, key="phone")
    email = st.text_input("Email (optional)", max_chars=50, key="email")
    amount_received = st.text_input("Amount Received (₹)", max_chars=10, key="amount_received")

    st.markdown("**Payment Mode:**")
    payment_mode = st.selectbox("", ["Cashfree", "Cash", "Other"], key="payment_mode")

    if payment_mode == "Other":
        custom_payment_mode = st.text_input("Enter Other Payment Mode", key="custom_payment_mode")
        final_payment_mode = custom_payment_mode.strip() if custom_payment_mode else "Other"
    else:
        final_payment_mode = payment_mode

    reference_id = st.text_input("Reference ID (optional)", max_chars=20, key="reference_id")
    payment_date = st.date_input("Date of Payment", datetime.today(), key="payment_date").strftime("%d/%m/%Y")
    delivery_date = st.date_input("Delivery Date", datetime.today(), key="delivery_date").strftime("%d/%m/%Y")

    st.markdown("---")
    st.subheader("Enter Quantities for Items (Minimum quantities enforced)")

    quantity_pt_pro = st.number_input(
        "12 HP PT Pro", min_value=0, step=1, value=1, key="qty_pt_pro"
    )
    quantity_battery = st.number_input(
        "Battery Sets", min_value=0, step=1, value=1, key="qty_battery"
    )
    quantity_charger = st.number_input(
        "Fast Chargers", min_value=0, step=1, value=2, key="qty_charger"
    )
    quantity_blade_weeding = st.number_input(
        "1 Set of Sugarcane Blades(Weeding)", min_value=0, step=1, value=0, key="qty_blade_weeding"
    )
    quantity_blade_earthing = st.number_input(
        "1 Set of Sugarcane Blades(Earthing-up)", min_value=0, step=1, value=0, key="qty_blade_earthing"
    )
    quantity_tyres = st.number_input(
        "1 Set of Tyres (5x10)", min_value=0, step=1, value=0, key="qty_tyres"
    )
    quantity_toolkit = st.number_input(
        "Toolkit", min_value=0, step=1, value=0, key="qty_toolkit"
    )
    quantity_ginger = st.number_input(
        "Ginger Kit", min_value=0, step=1, value=0, key="qty_ginger"
    )
    quantity_seat = st.number_input(
        "Seat", min_value=0, step=1, value=0, key="qty_seat"
    )
    quantity_jack = st.number_input(
        "Jack", min_value=0, step=1, value=0, key="qty_jack"
    )
    quantity_buyback_guarantee = st.number_input(
        "BuyBack Guarantee", min_value=0, step=1, value=0, key="qty_buyback_guarantee"
    )
    quantity_front_dead_weight = st.number_input(
        "Front Dead Weight", min_value=0, step=1, value=0, key="qty_front_dead_weight"
    )
    quantity_wheel_dead_weight = st.number_input(
        "Wheel Dead Weight", min_value=0, step=1, value=0, key="qty_wheel_dead_weight"
    )

    if st.button("Generate Receipt DOCX"):
        if not receipt_no:
            st.error("Receipt Number is required and must be numeric up to 4 digits.")
        elif len(phone) != 10:
            st.error("Phone Number must be exactly 10 digits.")
        else:
            doc = DocxTemplate(TEMPLATE_PATH)

            context = {
                "receipt_no": receipt_no,
                "date": date,
                "customer_name": customer_name,
                "address_line1": address_line1,
                "phone": phone,
                "email": email if email else "N/A",
                "amount_received": amount_received,
                "payment_mode": final_payment_mode,
                "reference_id": reference_id if reference_id else "N/A",
                "payment_date": payment_date,
                # "balance_due": balance_due,
                "delivery_date": delivery_date,

                # Quantities passed as placeholders
                "quantity_pt_pro": quantity_pt_pro,
                "quantity_battery": quantity_battery,
                "quantity_charger": quantity_charger,
                "quantity_blade_weeding": quantity_blade_weeding,
                "quantity_blade_earthing": quantity_blade_earthing,
                "quantity_tyres": quantity_tyres,
                "quantity_toolkit": quantity_toolkit,
                "quantity_ginger": quantity_ginger,
                "quantity_seat": quantity_seat,
                "quantity_jack": quantity_jack,
                "quantity_buyback_guarantee": quantity_buyback_guarantee,
                "quantity_front_dead_weight": quantity_front_dead_weight,
                "quantity_wheel_dead_weight": quantity_wheel_dead_weight
            }

            try:
                doc.render(context)
                output_filename = f"Orbit_Agritech_Proforma_Receipt_{receipt_no}.docx"
                doc.save(output_filename)
                st.success(f"Receipt generated: {output_filename}")

                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="Download Receipt DOCX",
                        data=file,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error("❌ Error rendering document.")
                st.exception(e)