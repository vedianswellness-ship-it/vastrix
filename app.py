import streamlit as st
from datetime import datetime
from db_manager import DatabaseManager

# Optimize configuration for mobile viewports
st.set_page_config(
    page_title="Vastrix Mobile", 
    page_icon="🏭", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# Mobile Custom Layout Adjustments
st.markdown("""
    <style>
    .block-container { padding: 1.5rem 1rem !important; }
    div.stButton > button { width: 100%; height: 3.2rem; font-size: 1.1rem; border-radius: 8px; font-weight: bold; }
    .kpi-card { background: #ffffff; padding: 16px; border-radius: 12px; border-top: 4px solid #FF4B4B; box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: center; margin-bottom: 10px; }
    .kpi-value { font-size: 1.8rem; font-weight: bold; color: #111; }
    .kpi-label { font-size: 0.85rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }
    .log-card { background: #fdfdfd; padding: 12px; border-radius: 8px; border-left: 4px solid #1E88E5; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .bundle-badge { background: #e3f2fd; color: #0d47a1; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
    .op-row { background: #f1f3f4; padding: 8px; border-radius: 6px; margin-bottom: 5px; font-size: 0.9rem; }
    </style>
""", unsafe_allow_html=True)

db = DatabaseManager()

# Top App Brand bar
st.markdown("<h2 style='margin-bottom:0;'>🏭 Vastrix Smart ERP</h2>", unsafe_allow_html=True)
st.caption("Garment Production Tracking System • Mobile Supervisor Interface")

# Native mobile-friendly tab bar navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Stats", "📝 Daily Log", "✂️ Cutting", "⚙️ Masters", "👥 Workers"])

# --- TAB 1: OVERVIEW & DASHBOARD ---
with tab1:
    st.subheader("Today's Factory Pulse")
    stats = db.get_daily_summary_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{stats['pieces_produced']}</div><div class='kpi-label'>Pieces Checked</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>₹{stats['payout_incurred']:.2f}</div><div class='kpi-label'>Total Wage Earned</div></div>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Recent Activity Logs")
    all_logs = sorted(db.daily_work.find(), key=lambda x: x.get('timestamp', datetime.now()), reverse=True)[:5]
    if not all_logs:
        st.info("No logs entry submitted yet today.")
    else:
        for log in all_logs:
            if log.get("type") == "Salary Attendance":
                st.markdown(f"""
                <div class='log-card' style='border-left-color: #4CAF50;'>
                    <strong>{log.get('employee')} (Salary Base)</strong>: {log.get('status')}<br/>
                    <span style='color:#2e7d32; font-weight:600;'>Wage: ₹{log.get('total_amount'):.2f}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='log-card'>
                    <strong>{log.get('employee')}</strong> — Lot: {log.get('lot_no')} (Bundle: {log.get('bundle_no')})<br/>
                    Done: {log.get('qty')} pcs ({log.get('process')}) <br/>
                    <span style='color:#2e7d32; font-weight:600;'>Earnings: ₹{log.get('total_amount'):.2f}</span>
                </div>
                """, unsafe_allow_html=True)

# --- TAB 2: SMART DAILY WORK / ATTENDANCE ENTRY ---
with tab2:
    st.subheader("Daily Work Entry System")
    employees = db.get_all_employees()
    active_lots = db.get_active_lots()
    
    if not employees:
        st.warning("⚠️ Setup your Workers in the Workers tab first!")
    else:
        emp_map = {e["name"]: e for e in employees}
        selected_emp_name = st.selectbox("Select Worker Name", list(emp_map.keys()))
        selected_emp_profile = emp_map[selected_emp_name]
        
        st.info(f"📋 Profile Target Type: **{selected_emp_profile['emp_type']}**")
        
        # --- BRANCH 1: FIXED SALARY ATTENDANCE ---
        if selected_emp_profile["emp_type"] == "Salary Basis":
            status = st.radio("Attendance Status", ["Full Present", "Half Day", "Leave/Absent"], horizontal=True)
            overtime_hours = st.number_input("Overtime Hours", min_value=0, max_value=8, value=0)
            
            monthly_base = selected_emp_profile.get("base_salary", 0.0)
            daily_rate = monthly_base / 30.0
            calculated_daily_wage = (daily_rate * (1.0 if status == "Full Present" else 0.5 if status == "Half Day" else 0.0)) + (overtime_hours * (daily_rate / 8.0 * 1.5))
            st.metric(label="Calculated Day Pay", value=f"₹{calculated_daily_wage:.2f}")
            
            if st.button("⚡ Submit Attendance"):
                payload = {"date": datetime.today().strftime("%Y-%m-%d"), "employee": selected_emp_name, "type": "Salary Attendance", "status": status, "ot_hours": overtime_hours, "total_amount": calculated_daily_wage}
                if db.log_daily_entry(payload):
                    st.success("Attendance recorded safely!")
                    st.rerun()
                    
        # --- BRANCH 2: PIECE RATE / BUNDLE ALLOCATION FROM BLUEPRINT ---
        else:
            if not active_lots:
                st.warning("⚠️ Ensure active Lots are created in the Cutting tab first!")
            else:
                lot_nos = [l["lot_no"] for l in active_lots]
                selected_lot_no = st.selectbox("Select Cut Lot Number", lot_nos)
                selected_lot_profile = next(l for l in active_lots if l["lot_no"] == selected_lot_no)
                
                available_bundles = [b for b in selected_lot_profile["bundles"] if b["status"] == "Available"]
                
                if not available_bundles:
                    st.success("🎉 All bundles for this Lot have been completed!")
                else:
                    bundle_nos = [b["bundle_no"] for b in available_bundles]
                    selected_bundle_no = st.selectbox("Assign Bundle Card", bundle_nos)
                    selected_bundle_profile = next(b for b in available_bundles if b["bundle_no"] == selected_bundle_no)
                    
                    relevant_procs = selected_lot_profile.get("operations_blueprint", [])
                    
                    if not relevant_procs:
                        st.error("No operation workflows are attached to this product template profile!")
                    else:
                        proc_labels = [f"{p['op_name']} (₹{p['rate']}/pc)" for p in relevant_procs]
                        selected_proc_idx = st.selectbox("Select Completed Operation Step", range(len(proc_labels)), format_func=lambda x: proc_labels[x])
                        target_process = relevant_procs[selected_proc_idx]
                        
                        qty = selected_bundle_profile["qty"]
                        est_payout = qty * target_process['rate']
                        
                        st.markdown(f"**Pieces inside Bundle:** <span class='bundle-badge'>{qty} Pcs</span>", unsafe_allow_html=True)
                        st.metric(label="Calculated Payout", value=f"₹{est_payout:.2f}")
                        
                        if st.button("⚡ Submit Bundle Completion"):
                            payload = {
                                "date": datetime.today().strftime("%Y-%m-%d"), "employee": selected_emp_name,
                                "type": "Piece Rate Work", "lot_no": selected_lot_no, "bundle_no": selected_bundle_no,
                                "item_type": selected_lot_profile["product_name"], "process": target_process["op_name"],
                                "qty": int(qty), "rate": float(target_process["rate"]), "total_amount": est_payout
                            }
                            if db.log_daily_entry(payload):
                                db.update_bundle_status(selected_lot_no, selected_bundle_no, selected_emp_name)
                                st.success("Bundle logged and saved to history!")
                                st.rerun()

# --- TAB 3: CUTTING DEPARTMENT LOG ---
with tab3:
    st.subheader("✂️ Cutting Department Lot Setup")
    products = db.get_all_products()
    
    if not products:
        st.warning("⚠️ Setup a Product Template Routing list in the Masters tab first!")
    else:
        prod_names = [p["product_name"] for p in products]
        
        with st.form("cutting_form", clear_on_submit=True):
            lot_no = st.text_input("New Lot Number (Unique ID)", placeholder="e.g., LOT-101")
            selected_product = st.selectbox("Select Product Template Routing", prod_names)
            total_pcs = st.number_input("Total Cut Pieces", min_value=1, value=500, step=50)
            bundle_qty = st.number_input("Bundle Size Limit (Pcs/Bundle)", min_value=1, value=50, step=5)
            
            if st.form_submit_button("Generate Lot & Bundle Cards"):
                if lot_no:
                    db.create_cutting_lot(lot_no, selected_product, total_pcs, bundle_qty)
                    st.success(f"Lot {lot_no} created and split into operational bundle runs!")
                    st.rerun()

# --- TAB 4: PRODUCT & PROCESS MASTERS CONFIGURATION ---
with tab4:
    st.subheader("⚙️ Global Configuration Masters")
    st.write("### Create Product Process Workflow Blueprint")
    
    product_name = st.text_input("Product Name", placeholder="e.g., Round Neck T-Shirt")
    st.caption("Define cost parameters per single piece processing:")
    
    col1, col2 = st.columns(2)
    with col1:
        c_rate = st.number_input("Cutting Rate (₹)", min_value=0.0, value=1.0, step=0.10)
        s_ol_rate = st.number_input("Stitching: Overlock Rate (₹)", min_value=0.0, value=3.0, step=0.10)
        s_fl_rate = st.number_input("Stitching: Flatlock Rate (₹)", min_value=0.0, value=4.0, step=0.10)
        s_sg_rate = st.number_input("Stitching: Singer Rate (₹)", min_value=0.0, value=2.5, step=0.10)
    with col2:
        pr_rate = st.number_input("Printing/Embroidery Rate (₹)", min_value=0.0, value=2.0, step=0.10)
        ps_rate = st.number_input("Pressing (Steam/Manual) Rate (₹)", min_value=0.0, value=1.0, step=0.10)
        pk_rate = st.number_input("Packing/Manual Boxing Rate (₹)", min_value=0.0, value=0.5, step=0.10)

    if st.button("💾 Save Full Product Master Template"):
        if product_name:
            ops_blueprint = [
                {"op_name": "Cutting", "rate": c_rate},
                {"op_name": "Stitching: Overlock", "rate": s_ol_rate},
                {"op_name": "Stitching: Flatlock", "rate": s_fl_rate},
                {"op_name": "Stitching: Singer", "rate": s_sg_rate},
                {"op_name": "Printing", "rate": pr_rate},
                {"op_name": "Pressing", "rate": ps_rate},
                {"op_name": "Packing", "rate": pk_rate}
            ]
            db.add_product_template(product_name, ops_blueprint)
            st.success(f"Product Template for '{product_name}' saved successfully!")
            st.rerun()

    st.write("---")
    st.write("### Existing Configuration Blueprints")
    existing_prods = db.get_all_products()
    for ep in existing_prods:
        with st.expander(f"📋 {ep['product_name']}"):
            for op in ep["operations"]:
                st.markdown(f"<div class='op-row'>🔹 **{op['op_name']}:** ₹{op['rate']}/pc</div>", unsafe_allow_html=True)

# --- TAB 5: WORKER PROFILING ---
with tab5:
    st.subheader("Add Factory Hand / Contractor")
    with st.form("employee_form", clear_on_submit=True):
        emp_id = st.text_input("Employee Card/ID Number")
        emp_name = st.text_input("Full Name")
        mobile = st.text_input("Mobile Number")
        emp_type = st.selectbox("Compensation Model", ["Piece Rate Basis", "Salary Basis", "Contractor"])
        
        base_salary = 0.0
        if emp_type == "Salary Basis":
            base_salary = st.number_input("Monthly Base Salary (₹)", min_value=0, value=15000, step=500)
            
        address = st.text_input("Residential Address/Village Name")
        
        if st.form_submit_button("Register Employee Account"):
            if emp_name and emp_id:
                db.add_employee(emp_id, emp_name, mobile, emp_type, address, base_salary)
                st.success("Registered worker cleanly!")
                st.rerun()
