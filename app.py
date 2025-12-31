"""Main Streamlit application for RS Fruit Bites Owner Dashboard."""
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, timedelta

from src.core.database import get_db_context, init_db
from src.services import CustomerService, AttendanceService, PaymentService, ReportService

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="RS Fruit Bites - Owner Dashboard",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
body, .stApp { background-color: #FFF6ED; }
section[data-testid="stSidebar"] { background-color: #FDE6D4; border-right: 2px solid #E8C9B0; }
section[data-testid="stSidebar"] * { color: #4A3F35; font-weight: 600; }
.big-title { font-size: 34px; font-weight: 900; color: #5A4638; }
.sub-title { font-size: 16px; color: #6A5648; margin-top:-6px; margin-bottom:10px; }
.stButton>button { 
    background-color: #E9A178 !important; 
    color: white !important; 
    border-radius: 8px !important; 
    font-weight: 700 !important; 
}
.metric-card {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='big-title'>🍎 RS Fruit Bites — Owner Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>PostgreSQL • Poetry • Clean Architecture • Real-time Sync</div>", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Menu",
    [
        "📊 Dashboard",
        "👥 Customers",
        "🗓 Attendance",
        "💸 Payments",
        "📈 Reports",
        "🕰 Past Members",
        "🗑 Audit Logs",
    ],
)

# Helper function
def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")


# ==================== DASHBOARD ====================
if page == "📊 Dashboard":
    st.header("📊 Dashboard Overview")
    
    with get_db_context() as db:
        report_service = ReportService(db)
        metrics = report_service.get_dashboard_metrics()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Active Customers", metrics["total_customers"])
        with col2:
            st.metric("Present Today", metrics["present_today"])
        with col3:
            st.metric("Extra Bowls Today", metrics["extra_bowls_today"])
        
        st.markdown("---")
        st.subheader("💰 Pending Bills")
        pending = report_service.get_pending_bills()
        
        if not pending.empty:
            st.dataframe(pending, use_container_width=True)
            st.download_button(
                "📥 Export Pending Bills CSV",
                data=to_csv_bytes(pending),
                file_name=f"pending_bills_{date.today().isoformat()}.csv",
                mime="text/csv",
            )
        else:
            st.info("No pending bills found.")


# ==================== CUSTOMERS ====================
elif page == "👥 Customers":
    st.header("👥 Customer Management")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Add New Customer")
        with st.form("add_customer", clear_on_submit=True):
            name = st.text_input("Name *")
            area = st.text_input("Area")
            mobile = st.text_input("Mobile")
            subscription = st.selectbox("Subscription", ["Basic", "Medium", "Premium"])
            custom_rate = st.number_input("Monthly Rate (₹)", min_value=0.0, value=0.0, step=50.0)
            
            if st.form_submit_button("➕ Add Customer"):
                if not name.strip():
                    st.error("Name is required")
                else:
                    try:
                        with get_db_context() as db:
                            customer_service = CustomerService(db)
                            customer_service.create_customer(
                                name=name.strip(),
                                area=area.strip(),
                                mobile=mobile.strip(),
                                subscription=subscription,
                                custom_rate=custom_rate,
                            )
                        st.success(f"✅ Added {name.strip()}")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
    
    with col2:
        st.subheader("Active Customers")
        # Subscription filter for easier identification
        sub_filter = st.radio(
            "Filter by subscription",
            ["All", "Basic", "Medium", "Premium"],
            horizontal=True,
        )
        
        with get_db_context() as db:
            customer_service = CustomerService(db)
            customers = customer_service.get_all_customers(active_only=True)
        
        if sub_filter != "All":
            customers = [c for c in customers if c["subscription"] == sub_filter]

        if not customers:
            st.info("No active customers")
        else:
            df = pd.DataFrame(customers)
            st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("Edit Customer")
            
            customer_names = [c["name"] for c in customers]
            selected = st.selectbox("Select customer to edit", customer_names)
            
            if selected:
                customer = next(c for c in customers if c["name"] == selected)
                
                with st.form("edit_customer"):
                    new_area = st.text_input("Area", value=customer["area"])
                    new_mobile = st.text_input("Mobile", value=customer["mobile"])
                    new_sub = st.selectbox(
                        "Subscription",
                        ["Basic", "Medium", "Premium"],
                        index=["Basic", "Medium", "Premium"].index(customer["subscription"]),
                    )
                    new_rate = st.number_input(
                        "Monthly Rate (₹)",
                        min_value=0.0,
                        value=float(customer["custom_rate"]),
                        step=50.0,
                    )
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.form_submit_button("💾 Save Changes"):
                            try:
                                with get_db_context() as db:
                                    customer_service = CustomerService(db)
                                    customer_service.update_customer(
                                        name=selected,
                                        area=new_area,
                                        mobile=new_mobile,
                                        subscription=new_sub,
                                        custom_rate=new_rate,
                                    )
                                st.success("✅ Customer updated")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
                    
                    with col_b:
                        if st.form_submit_button("🔄 Deactivate"):
                            try:
                                with get_db_context() as db:
                                    customer_service = CustomerService(db)
                                    customer_service.deactivate_customer(selected)
                                st.warning(f"⚠️ {selected} moved to Past Members")
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
                
                st.markdown("---")
                if st.button("🗑 Delete Permanently (Mistake Entry)"):
                    st.session_state.confirm_delete = selected
                
                if st.session_state.get("confirm_delete") == selected:
                    st.warning(f"⚠️ Permanently delete {selected}? This action logs the record.")
                    reason = st.text_input("Reason for deletion")
                    if st.button("✅ Confirm Delete"):
                        try:
                            with get_db_context() as db:
                                customer_service = CustomerService(db)
                                customer_service.delete_customer_permanently(selected, reason)
                            st.success(f"✅ {selected} deleted (audit log kept)")
                            st.session_state.confirm_delete = None
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))


# ==================== ATTENDANCE ====================
elif page == "🗓 Attendance":
    st.header("🗓 Attendance Management")
    
    with get_db_context() as db:
        customer_service = CustomerService(db)
        customers = customer_service.get_all_customers(active_only=True)
    
    if not customers:
        st.info("No active customers to mark attendance")
    else:
        selected_date = st.date_input("Select Date", date.today())
        
        st.markdown("---")
        st.write("✅ Check = Present | ❌ Unchecked = Absent | Enter extra bowls if applicable")

        # Helper: Use previous day's attendance to prefill today's controls
        ucol1, _ = st.columns([1, 3])
        with ucol1:
            if st.button("Use previous day's attendance"):
                prev_date = selected_date - timedelta(days=1)
                with get_db_context() as db:
                    attendance_service = AttendanceService(db)
                    prev_att = attendance_service.get_attendance_by_date(prev_date)
                prev_map = {}
                if not prev_att.empty:
                    for _, r in prev_att.iterrows():
                        prev_map[r["name"]] = {
                            "status": r.get("status", "Absent"),
                            "extra_bowls": int(r.get("extra_bowls", 0) or 0),
                        }
                # Prefill from previous day: Present/Extra => checked, Absent/None => unchecked
                for c in customers:
                    nm = c["name"]
                    key_cb = f"att_{nm}_{selected_date}"
                    key_ex = f"extra_{nm}_{selected_date}"
                    prev = prev_map.get(nm)
                    was_present = bool(prev and prev.get("status") in ("Present", "Extra"))
                    prev_extra = int(prev.get("extra_bowls", 0)) if prev else 0
                    st.session_state[key_cb] = was_present
                    st.session_state[key_ex] = prev_extra

        attendance_data = []
        
        for subscription in ["Basic", "Medium", "Premium"]:
            sub_customers = [c for c in customers if c["subscription"] == subscription]
            if sub_customers:
                st.subheader(f"{subscription} Plan")
                
                for customer in sub_customers:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        present = st.checkbox(
                            customer["name"],
                            key=f"att_{customer['name']}_{selected_date}",
                        )
                    with col2:
                        extra = 0
                        if present:
                            ex_key = f"extra_{customer['name']}_{selected_date}"
                            default_extra = int(st.session_state.get(ex_key, 0))
                            extra = st.number_input(
                                "Extra",
                                min_value=0,
                                value=default_extra,
                                key=ex_key,
                            )
                    
                    status = "Extra" if extra > 0 else ("Present" if present else "Absent")
                    attendance_data.append({
                        "name": customer["name"],
                        "subscription": subscription,
                        "status": status,
                        "extra_bowls": extra,
                    })
        
        st.markdown("---")
        if st.button("💾 Save Attendance"):
            try:
                with get_db_context() as db:
                    attendance_service = AttendanceService(db)
                    for record in attendance_data:
                        attendance_service.mark_attendance(
                            attendance_date=selected_date,
                            name=record["name"],
                            subscription=record["subscription"],
                            status=record["status"],
                            extra_bowls=record["extra_bowls"],
                        )
                st.success(f"✅ Attendance saved for {selected_date}")
                # Clear today's attendance widget states to avoid accidental double submission
                try:
                    for c in customers:
                        nm = c["name"]
                        cb_key = f"att_{nm}_{selected_date}"
                        ex_key = f"extra_{nm}_{selected_date}"
                        if cb_key in st.session_state:
                            del st.session_state[cb_key]
                        if ex_key in st.session_state:
                            del st.session_state[ex_key]
                except Exception:
                    pass
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        st.subheader(f"Today's Attendance ({selected_date})")
        
        with get_db_context() as db:
            attendance_service = AttendanceService(db)
            today_att = attendance_service.get_attendance_by_date(selected_date)
        
        if not today_att.empty:
            # Compute bowls: 1 for Present/Extra + extra_bowls, 0 for Absent
            df_att = today_att.copy()
            df_att["base_bowl"] = df_att["status"].isin(["Present", "Extra"]).astype(int)
            df_att["extra_bowls"] = df_att["extra_bowls"].fillna(0).astype(int)
            df_att["bowls"] = df_att["base_bowl"] + df_att["extra_bowls"]

            # Filters: subscription and status
            st.markdown("**Filters**")
            fcol1, fcol2 = st.columns(2)
            with fcol1:
                att_sub_filter = st.radio(
                    "Subscription",
                    ["All", "Basic", "Medium", "Premium"],
                    horizontal=True,
                    key="att_sub_filter_today",
                )
            with fcol2:
                att_status_filter = st.radio(
                    "Status",
                    ["All", "Present", "Absent", "Extra"],
                    horizontal=True,
                    key="att_status_filter_today",
                )

            df_view = df_att.copy()
            if att_sub_filter != "All":
                df_view = df_view[df_view["subscription"] == att_sub_filter]
            if att_status_filter != "All":
                df_view = df_view[df_view["status"] == att_status_filter]

            # Metrics based on filtered view
            total_bowls = int(df_view["bowls"].sum()) if not df_view.empty else 0
            by_plan = (
                df_view.groupby("subscription")["bowls"].sum().reindex(["Basic", "Medium", "Premium"]).fillna(0).astype(int)
                if not df_view.empty else None
            )

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Bowls", total_bowls)
            c2.metric("Basic Bowls", int(by_plan.get("Basic", 0)) if by_plan is not None else 0)
            c3.metric("Medium Bowls", int(by_plan.get("Medium", 0)) if by_plan is not None else 0)
            c4.metric("Premium Bowls", int(by_plan.get("Premium", 0)) if by_plan is not None else 0)

            st.markdown("---")
            st.dataframe(df_view.drop(columns=["base_bowl"], errors="ignore"), use_container_width=True)
        else:
            st.info("No attendance marked for this date")

        # Quick Update: modify a single person's attendance without affecting others
        st.markdown("---")
        st.subheader("Quick Update (Single Person)")

        # Fetch active customers for selection
        with get_db_context() as db:
            customer_service = CustomerService(db)
            quick_customers = customer_service.get_all_customers(active_only=True)

        if not quick_customers:
            st.info("No active customers to update.")
        else:
            names_quick = [c["name"] for c in quick_customers]
            with st.form("quick_update_attendance"):
                sel_person = st.selectbox("Select customer", names_quick)
                sel_status = st.selectbox("Status", ["Present", "Absent", "Extra"], index=0)
                # Determine default subscription and set extra bowls logic
                person_row = next((c for c in quick_customers if c["name"] == sel_person), None)
                person_sub = person_row["subscription"] if person_row else "Basic"
                if sel_status == "Extra":
                    sel_extra = st.number_input("Extra bowls", min_value=1, value=1)
                elif sel_status == "Present":
                    sel_extra = st.number_input("Extra bowls", min_value=0, value=0)
                else:
                    sel_extra = 0

                if st.form_submit_button(f"Update attendance for {selected_date}"):
                    try:
                        with get_db_context() as db:
                            attendance_service = AttendanceService(db)
                            attendance_service.mark_attendance(
                                attendance_date=selected_date,
                                name=sel_person,
                                subscription=person_sub,
                                status=sel_status,
                                extra_bowls=int(sel_extra),
                            )
                        st.success(f"✅ Updated {sel_person} on {selected_date} as {sel_status}")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))


# ==================== PAYMENTS ====================
elif page == "💸 Payments":
    st.header("💸 Payment Management")
    
    with get_db_context() as db:
        customer_service = CustomerService(db)
        customers = customer_service.get_all_customers(active_only=True)
    
    if not customers:
        st.info("No customers available")
    else:
        # Subscription filter to narrow down selection
        pay_sub_filter = st.radio(
            "Filter by subscription",
            ["All", "Basic", "Medium", "Premium"],
            horizontal=True,
        )
        filtered_customers = (
            [c for c in customers if c["subscription"] == pay_sub_filter]
            if pay_sub_filter != "All"
            else customers
        )

        st.subheader("Record New Payment")
        # Show success message from previous submission (persisted across rerun)
        if st.session_state.get("pay_success_msg"):
            st.success(st.session_state["pay_success_msg"])
            del st.session_state["pay_success_msg"]
        
        with st.form("record_payment"):
            customer_names = [c["name"] for c in filtered_customers]
            selected = st.selectbox("Select Customer", customer_names, key="pay_customer")
            amount = st.number_input("Amount (₹)", min_value=0.0, step=50.0, key="pay_amount")
            method = st.selectbox("Payment Method", ["Cash", "GPay", "PhonePe", "Other"], key="pay_method")
            remarks = st.text_input("Remarks (optional)", key="pay_remarks")
            
            if st.form_submit_button("💰 Record Payment"):
                if amount <= 0:
                    st.error("Amount must be greater than 0")
                else:
                    try:
                        with get_db_context() as db:
                            payment_service = PaymentService(db)
                            payment_service.record_payment(
                                payment_date=date.today(),
                                name=selected,
                                amount=amount,
                                method=method,
                                remarks=remarks,
                            )
                        # Persist a success message across rerun so the owner clearly sees it
                        st.session_state["pay_success_msg"] = f"✅ Payment of ₹{amount:,.2f} recorded for {selected}"
                        # Reset form fields to avoid accidental double submissions
                        try:
                            if customer_names:
                                st.session_state["pay_customer"] = customer_names[0]
                            st.session_state["pay_amount"] = 0.0
                            st.session_state["pay_method"] = "Cash"
                            st.session_state["pay_remarks"] = ""
                        except Exception:
                            pass
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
    
    st.markdown("---")
    st.subheader("Recent Payments")
    
    with get_db_context() as db:
        payment_service = PaymentService(db)
        payments = payment_service.get_all_payments()
    
    if not payments.empty:
        # Show payments with per-row delete buttons
        cols_keep = [c for c in ["id", "date", "name", "amount", "method", "remarks"] if c in payments.columns]
        view = payments[cols_keep].head(100).copy()

        # Header
        h1, h2, h3, h4, h5, h6, h7 = st.columns([0.8, 1.4, 1.6, 1.0, 1.0, 2.0, 0.8])
        h1.markdown("**ID**")
        h2.markdown("**Date**")
        h3.markdown("**Name**")
        h4.markdown("**Amount**")
        h5.markdown("**Method**")
        h6.markdown("**Remarks**")
        h7.markdown("**Action**")

        for _, row in view.iterrows():
            c1, c2, c3, c4, c5, c6, c7 = st.columns([0.8, 1.4, 1.6, 1.0, 1.0, 2.0, 0.8])
            c1.write(int(row.get("id", 0)))
            c2.write(str(row.get("date", "")))
            c3.write(str(row.get("name", "")))
            c4.write(f"₹{float(row.get('amount', 0)):,.2f}")
            c5.write(str(row.get("method", "")))
            c6.write(str(row.get("remarks", "")))
            if c7.button("🗑️", key=f"del_pay_{int(row.get('id', 0))}"):
                try:
                    with get_db_context() as db:
                        payment_service = PaymentService(db)
                        if payment_service.delete_payment(int(row["id"])):
                            st.success(f"✅ Deleted payment id={int(row['id'])}")
                            st.rerun()
                        else:
                            st.warning("Payment not found.")
                except Exception as e:
                    st.error(str(e))

        st.markdown("---")
        st.download_button(
            "📥 Export All Payments CSV",
            data=to_csv_bytes(payments),
            file_name=f"payments_{date.today().isoformat()}.csv",
            mime="text/csv",
        )
    else:
        st.info("No payment records found")


# ==================== REPORTS ====================
elif page == "📈 Reports":
    st.header("📈 Reports & Analytics")
    
    # Initialize persistent date range in session (defaults to current month)
    if "report_start" not in st.session_state or "report_end" not in st.session_state:
        first_of_month = date.today().replace(day=1)
        st.session_state.report_start = first_of_month
        st.session_state.report_end = date.today()

    col1, col2, col3 = st.columns([1,1,0.6])
    with col1:
        start_date = st.date_input("Start Date", value=st.session_state.report_start, key="report_start_input")
    with col2:
        end_date = st.date_input("End Date", value=st.session_state.report_end, key="report_end_input")
    with col3:
        if st.button("Use Current Month", help="Quickly set dates to the current month"):
            st.session_state.report_start = date.today().replace(day=1)
            st.session_state.report_end = date.today()
            st.rerun()

    # Persist any manual changes
    st.session_state.report_start = start_date
    st.session_state.report_end = end_date
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📅 Attendance", "💰 Payments", "📊 Pending Bills"])
    
    with tab1:
        st.subheader("Attendance Report")
        with get_db_context() as db:
            attendance_service = AttendanceService(db)
            att_report = attendance_service.get_attendance_by_range(start_date, end_date)
        
        if not att_report.empty:
            # Compute bowls per record
            df_att = att_report.copy()
            df_att["base_bowl"] = df_att["status"].isin(["Present", "Extra"]).astype(int)
            df_att["extra_bowls"] = df_att["extra_bowls"].fillna(0).astype(int)
            df_att["bowls"] = df_att["base_bowl"] + df_att["extra_bowls"]

            # Filters
            f1, f2 = st.columns([1,1])
            with f1:
                rep_sub_filter = st.radio(
                    "Subscription",
                    ["All", "Basic", "Medium", "Premium"],
                    horizontal=True,
                    key="rep_att_sub_filter",
                )
            with f2:
                hide_absent = st.checkbox("Hide Absent", value=True, key="rep_att_hide_absent")

            df_view = df_att.copy()
            if rep_sub_filter != "All":
                df_view = df_view[df_view["subscription"] == rep_sub_filter]
            if hide_absent:
                df_view = df_view[df_view["status"] != "Absent"]

            # Sorting options
            st.markdown("**Sort options**")
            sort_choice = st.selectbox(
                "Sort by",
                [
                    "Bowls (high → low)",
                    "Status (Absent → Present → Extra)",
                    "Name (A → Z)",
                    "Subscription (Basic → Premium)",
                    "Date (newest → oldest)",
                ],
                index=0,
                key="att_sort_choice",
            )

            df_sorted = df_view.copy()
            if sort_choice == "Bowls (high → low)":
                df_sorted = df_sorted.sort_values(["bowls", "extra_bowls"], ascending=[False, False])
            elif sort_choice == "Status (Absent → Present → Extra)":
                status_order = {"Absent": 0, "Present": 1, "Extra": 2}
                df_sorted["_status_order"] = df_sorted["status"].map(status_order).fillna(3)
                df_sorted = df_sorted.sort_values(["_status_order", "name"]).drop(columns=["_status_order"]) 
            elif sort_choice == "Name (A → Z)":
                df_sorted = df_sorted.sort_values(["name", "date"], ascending=[True, False])
            elif sort_choice == "Subscription (Basic → Premium)":
                sub_order = {"Basic": 0, "Medium": 1, "Premium": 2}
                df_sorted["_sub_order"] = df_sorted["subscription"].map(sub_order).fillna(3)
                df_sorted = df_sorted.sort_values(["_sub_order", "name"]).drop(columns=["_sub_order"]) 
            elif sort_choice == "Date (newest → oldest)":
                df_sorted = df_sorted.sort_values(["date", "name"], ascending=[False, True])

            # Summary metrics based on filtered data
            total_bowls = int(df_view["bowls"].sum())
            present_cnt = int((df_view["status"] == "Present").sum())
            extra_cnt = int((df_view["status"] == "Extra").sum())
            absent_cnt = int((df_view["status"] == "Absent").sum())
            bowls_by_plan = (
                df_view.groupby("subscription")["bowls"].sum().reindex(["Basic", "Medium", "Premium"]).fillna(0).astype(int)
            )

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Bowls", total_bowls)
            c2.metric("Basic Bowls", int(bowls_by_plan.get("Basic", 0)))
            c3.metric("Medium Bowls", int(bowls_by_plan.get("Medium", 0)))
            c4.metric("Premium Bowls", int(bowls_by_plan.get("Premium", 0)))

            show_status = st.checkbox("Show Present/Extra/Absent counts", value=True, key="att_status_counts_toggle")
            if show_status:
                s1, s2, s3 = st.columns(3)
                s1.metric("Present", present_cnt)
                s2.metric("Extra", extra_cnt)
                s3.metric("Absent", absent_cnt)

            # Print summary button
            if st.button("🖨️ Print Summary", key="att_print_summary"):
                summary_html = f"""
                <html>
                <head>
                  <meta charset='utf-8' />
                  <title>Attendance Summary</title>
                  <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    h2 {{ margin-bottom: 6px; }}
                    .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px 24px; }}
                    .item {{ padding: 6px 0; }}
                  </style>
                </head>
                <body onload="window.print()">
                  <h2>Attendance Summary</h2>
                  <div>Date range: {start_date} to {end_date}</div>
                  <hr/>
                  <div class="grid">
                    <div class="item"><strong>Total Bowls:</strong> {total_bowls}</div>
                    <div class="item"><strong>Basic Bowls:</strong> {int(bowls_by_plan.get('Basic', 0))}</div>
                    <div class="item"><strong>Medium Bowls:</strong> {int(bowls_by_plan.get('Medium', 0))}</div>
                    <div class="item"><strong>Premium Bowls:</strong> {int(bowls_by_plan.get('Premium', 0))}</div>
                    <div class="item"><strong>Present:</strong> {present_cnt}</div>
                    <div class="item"><strong>Extra:</strong> {extra_cnt}</div>
                    <div class="item"><strong>Absent:</strong> {absent_cnt}</div>
                  </div>
                </body>
                </html>
                """
                components.html(summary_html, height=250)

            # Bowl Summary with selectable granularity
            st.markdown("---")
            st.markdown("#### Bowl Summary")
            gran = st.radio("Granularity", ["Daily", "Monthly", "Yearly"], horizontal=True, key="att_summary_gran")
            gdf = df_view.copy()
            gdf["date"] = pd.to_datetime(gdf["date"])  # type: ignore
            if gran == "Daily":
                grouped = gdf.assign(key=gdf["date"].dt.date)
            elif gran == "Monthly":
                grouped = gdf.assign(key=gdf["date"].dt.to_period("M").astype(str))
            else:
                grouped = gdf.assign(key=gdf["date"].dt.year)

            agg = grouped.groupby(["key", "subscription"], as_index=False)["bowls"].sum()
            pivot = (
                agg.pivot(index="key", columns="subscription", values="bowls")
                .reindex(columns=["Basic", "Medium", "Premium"])
                .fillna(0)
                .astype(int)
            )
            pivot = pivot.sort_index(ascending=False).reset_index().rename(columns={"key": gran})
            pivot["Total"] = pivot[["Basic", "Medium", "Premium"]].sum(axis=1)
            total_basic = int(pivot["Basic"].sum())
            total_medium = int(pivot["Medium"].sum())
            total_premium = int(pivot["Premium"].sum())
            total_all = int(pivot["Total"].sum())
            totals_row = {gran: "Total", "Basic": total_basic, "Medium": total_medium, "Premium": total_premium, "Total": total_all}
            pivot = pd.concat([pivot, pd.DataFrame([totals_row])], ignore_index=True)
            # Headline metrics for selected granularity
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Bowls", total_all)
            m2.metric("Basic Total", total_basic)
            m3.metric("Medium Total", total_medium)
            m4.metric("Premium Total", total_premium)

            st.dataframe(pivot, use_container_width=True)
            st.download_button(
                "📥 Export Bowl Summary CSV",
                data=to_csv_bytes(pivot),
                file_name=f"attendance_summary_{gran.lower()}_{start_date}_{end_date}.csv",
                mime="text/csv",
            )

            # Optional detailed table view
            show_details = st.checkbox("Show detailed attendance rows", value=False, key="att_show_detailed_rows")
            if show_details:
                st.markdown("---")
                st.dataframe(df_sorted, use_container_width=True)

            st.download_button(
                "📥 Export Attendance CSV",
                data=to_csv_bytes(df_sorted),
                file_name=f"attendance_{start_date}_{end_date}.csv",
                mime="text/csv",
            )

            
        else:
            st.info("No attendance records in this range")
    
    with tab2:
        st.subheader("Payment Report")
        with get_db_context() as db:
            payment_service = PaymentService(db)
            pay_report = payment_service.get_payments_by_range(start_date, end_date)
        
        if not pay_report.empty:
            st.dataframe(pay_report, use_container_width=True)
            total = pay_report["amount"].sum()
            st.metric("Total Collected", f"₹{total:,.2f}")
            st.download_button(
                "📥 Export Payments CSV",
                data=to_csv_bytes(pay_report),
                file_name=f"payments_{start_date}_{end_date}.csv",
                mime="text/csv",
            )
            # Collections Summary with selectable granularity (mirrors daily style)
            st.markdown("---")
            st.markdown("#### Collections Summary")
            pgran = st.radio("Granularity", ["Daily", "Monthly", "Yearly"], horizontal=True, key="pay_summary_gran")
            pr = pay_report.copy()
            pr["date"] = pd.to_datetime(pr["date"])  # type: ignore
            if pgran == "Daily":
                pgroup = pr.assign(key=pr["date"].dt.date)
            elif pgran == "Monthly":
                pgroup = pr.assign(key=pr["date"].dt.to_period("M").astype(str))
            else:
                pgroup = pr.assign(key=pr["date"].dt.year)

            pay_summary = pgroup.groupby("key")["amount"].sum().reset_index().sort_values("key", ascending=False)
            pay_summary = pay_summary.rename(columns={"key": pgran, "amount": "Total Amount (₹)"})
            # Headline metrics
            total_collected = float(pr["amount"].sum())
            p1, p2 = st.columns(2)
            p1.metric("Total Collected", f"₹{total_collected:,.2f}")
            if not pay_summary.empty:
                top_row = pay_summary.iloc[0]
                p2.metric(f"Top {pgran}", f"{top_row[pgran]} (₹{float(top_row['Total Amount (₹)']):,.0f})")

            # Add grand total row
            grand_total = float(pay_summary["Total Amount (₹)"].sum()) if not pay_summary.empty else 0.0
            import pandas as pd
            gt_row = pd.DataFrame([{pgran: "Total", "Total Amount (₹)": grand_total}])
            pay_summary = pd.concat([pay_summary, gt_row], ignore_index=True)
            st.dataframe(pay_summary, use_container_width=True)
            st.download_button(
                "📥 Export Collections Summary CSV",
                data=to_csv_bytes(pay_summary),
                file_name=f"payments_summary_{pgran.lower()}_{start_date}_{end_date}.csv",
                mime="text/csv",
            )

            # Optional: per-subscription breakdown (Basic/Medium/Premium) similar to attendance
            st.markdown("---")
            show_pay_sub = st.checkbox("Show per-subscription collections (Basic/Medium/Premium)", value=False, key="pay_sub_breakdown_toggle")
            if show_pay_sub:
                # Build a name->subscription map from active + inactive customers
                with get_db_context() as db:
                    cs = CustomerService(db)
                    active = cs.get_all_customers(active_only=True)
                    inactive = cs.get_inactive_customers()
                name_to_sub = {c["name"]: c["subscription"] for c in (active + inactive)}

                psub = pgroup.copy()
                psub["subscription"] = psub["name"].map(name_to_sub).fillna("Unknown")  # type: ignore

                agg2 = psub.groupby(["key", "subscription"], as_index=False)["amount"].sum()
                pivot2 = (
                    agg2.pivot(index="key", columns="subscription", values="amount")
                    .reindex(columns=["Basic", "Medium", "Premium"])  # ignore Unknown
                    .fillna(0)
                )
                pivot2 = pivot2.sort_index(ascending=False).reset_index().rename(columns={"key": pgran})
                pivot2["Total Amount (₹)"] = pivot2[[c for c in ["Basic", "Medium", "Premium"] if c in pivot2.columns]].sum(axis=1)
                # Totals row
                tb = float(pivot2.get("Basic", pd.Series(dtype=float)).sum()) if "Basic" in pivot2.columns else 0.0
                tm = float(pivot2.get("Medium", pd.Series(dtype=float)).sum()) if "Medium" in pivot2.columns else 0.0
                tp = float(pivot2.get("Premium", pd.Series(dtype=float)).sum()) if "Premium" in pivot2.columns else 0.0
                ttot = float(pivot2["Total Amount (₹)"].sum()) if not pivot2.empty else 0.0
                totals_row2 = {pgran: "Total", "Basic": tb, "Medium": tm, "Premium": tp, "Total Amount (₹)": ttot}
                pivot2 = pd.concat([pivot2, pd.DataFrame([totals_row2])], ignore_index=True)

                st.subheader("Collections by Subscription")
                st.dataframe(pivot2, use_container_width=True)
                st.download_button(
                    "📥 Export Collections by Subscription CSV",
                    data=to_csv_bytes(pivot2),
                    file_name=f"payments_summary_subscription_{pgran.lower()}_{start_date}_{end_date}.csv",
                    mime="text/csv",
                )
        else:
            st.info("No payment records in this range")
    
    with tab3:
        st.subheader("Pending Bills")
        with get_db_context() as db:
            report_service = ReportService(db)
            pending = report_service.get_pending_bills()
        
        if not pending.empty:
            st.dataframe(pending, use_container_width=True)
            total_pending = pending["pending"].sum()
            st.metric("Total Pending", f"₹{total_pending:,.2f}")
            st.download_button(
                "📥 Export Pending Bills CSV",
                data=to_csv_bytes(pending),
                file_name=f"pending_bills_{date.today().isoformat()}.csv",
                mime="text/csv",
            )
        else:
            st.info("No pending bills")


# ==================== PAST MEMBERS ====================
elif page == "🕰 Past Members":
    st.header("🕰 Past Members (Inactive)")
    
    with get_db_context() as db:
        customer_service = CustomerService(db)
        inactive = customer_service.get_inactive_customers()
    
    if not inactive:
        st.info("No past members")
    else:
        # Subscription filter for past members
        past_sub_filter = st.radio(
            "Filter by subscription",
            ["All", "Basic", "Medium", "Premium"],
            horizontal=True,
        )
        filtered_inactive = (
            [c for c in inactive if c["subscription"] == past_sub_filter]
            if past_sub_filter != "All"
            else inactive
        )

        df = pd.DataFrame(filtered_inactive)
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Reactivate Member")
        
        names = [c["name"] for c in filtered_inactive]
        selected = st.selectbox("Select member to reactivate", names)
        
        if st.button("🔄 Reactivate"):
            try:
                with get_db_context() as db:
                    customer_service = CustomerService(db)
                    customer_service.reactivate_customer(selected)
                st.success(f"✅ {selected} reactivated")
                st.rerun()
            except ValueError as e:
                st.error(str(e))


# ==================== AUDIT LOGS ====================
elif page == "🗑 Audit Logs":
    st.header("🗑 Audit Logs & Deleted Members")
    
    with get_db_context() as db:
        report_service = ReportService(db)
        deleted = report_service.get_deleted_members()
    
    if not deleted.empty:
        st.dataframe(deleted, use_container_width=True)
        st.download_button(
            "📥 Export Audit Logs CSV",
            data=to_csv_bytes(deleted),
            file_name=f"audit_logs_{date.today().isoformat()}.csv",
            mime="text/csv",
        )
    else:
        st.info("No deleted member records")


# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6A5648;'>"
    "RS Fruit Bites Owner Dashboard • Built with Poetry, PostgreSQL & Clean Architecture"
    "</div>",
    unsafe_allow_html=True,
)
