import streamlit as st
from datetime import datetime
from db_manager import DatabaseManager

st.set_page_config(page_title="Vastrix Mobile", page_icon="🏭", layout="centered", initial_sidebar_state="collapsed")

# Mobile Custom Layout Adjustments
st.markdown("""
    <style>
    .block-container { padding: 1.5rem 1rem !important; }
    div.stButton > button { width: 100%; height: 3.2rem; font-size: 1.1rem; border-radius: 8px; font-weight: bold; }
    .kpi-card { background: #ffffff; padding: 16px; border-radius: 12px; border-top: 4px solid #FF4B4B; box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: center; margin-bottom: 10px; }
    .kpi-value { font-size: 1.8rem; font-weight: bold; color: #111; }
    .kpi-label { font-size: 0.85rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }
    .log-card { background: #fdfdfd; padding: 12px; border-radius: 8px; border-left: 4px solid #1E88E5; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

db = DatabaseManager()

# Top App Brand bar
st.markdown("<h2 style='margin-bottom:0;'>🏭 Vastrix Smart ERP</h2>", unsafe_allow_html=True)
st.caption("Garment Production Tracking System • Mobile Supervisor Interface")

# Native mobile-friendly tab bar navigation
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🪡 Piece Entry", "⚙️ Masters", "👥 Workers"])

# --- TAB 1: OVERVIEW & DASHBOARD ---
with tab1:
    st.subheader("Today's Factory Pulse")
    stats = db.get_daily_summary_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{stats['pieces_produced']}</div><div class='kpi-label'>Pieces Checked</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-card'><div class='kpi-value'>₹{stats['payout_incurred']:.2f}</div><div class='kpi-label'>Piece Wage Owed</div></div>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("Recent Production Logs")
    # Quick pull of all records for proof of concept
    all_logs = sorted(db.daily_work.find(), key=lambda x: x.get('timestamp', datetime.now()), reverse=True)[:5]
    if not all_logs:
        st.info("No pieces processed yet today.")
    for log in all_logs:
        st.markdown(f"""
        <div class='log-card'>
            <strong>{log.get('employee')}</strong> completed <strong>{log.get('qty')} pcs</strong> of {log.get('item_type')} ({log.get('process')})<br/>
            <span style='color:#2e7d32; font-weight:600;'>Earnings: ₹{log.get('total_amount')}</span> <span style='color:#888; font-size:0.8rem; float:right;'>{log.get('date')}</span>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 2: ONE-CLICK DAILY PIECE WORK ENTRY ---
with tab2:
    st.subheader("Supervisor Piece-Work Log")
    
    employees = db.get_all_employees()
    processes = db.get_all_processes()
    
    if not employees or not processes:
        st.warning("⚠️ Setup your Workers and Process Rates in the Masters tabs first before logging work!")
    else:
        emp_names = [e["name"] for e in employees]
        process_labels = [f"{p['item_type']} - {p['process_name']} (₹{p['rate']}/pc)" for p in processes]
        
        selected_emp = st.selectbox("Select Tailor / Operator", emp_names)
        selected_proc_idx = st.selectbox("Select Process & Operation", range(len(process_labels)), format_func=lambda x: process_labels[x])
        
        target_process = processes[selected_proc_idx]
        qty_input = st.number_input("Quantity Checked (Pcs)", min_value=1, value=100, step=10)
        
        # Real-time calculated feedback layout directly below inputs
        est_payout = qty_input * target_process['rate']
        st.metric(label="Calculated Payout Amount", value=f"₹{est_payout:.2f}", delta=f"Rate: ₹{target_process['rate']}/pc")
        
        if st.button("⚡ Submit Log to Wallet"):
            res = db.log_piece_work(datetime.today(), selected_emp, target_process, qty_input)
            if res:
                st.success(f"Successfully tracked {qty_input} pieces for {selected_emp}!")
                st.rerun()

# --- TAB 3: PROCESS MASTER SETTING ---
with tab3:
    st.subheader("Process & Rate Master Configuration")
    with st.form("process_form", clear_on_submit=True):
        item_type = st.text_input("Garment Type", placeholder="e.g., T-Shirt, Joggers")
        process_name = st.text_input("Operation Description", placeholder="e.g., Overlock, Flatlock, Stitching")
        machine = st.text_input("Machine Used", placeholder="e.g., Singer 4-Thread, Steam Press")
        rate = st.number_input("Rate Per Single Piece (₹)", min_value=0.0, value=3.50, step=0.10)
        
        if st.form_submit_button("Save Operation Details"):
            if item_type and process_name:
                db.add_process(item_type, process_name, machine, rate)
                st.success(f"Added operation profile for {item_type}!")
                st.rerun()

# --- TAB 4: WORKER PROFILING ---
with tab4:
    st.subheader("Add Factory Hand / Contractor")
    with st.form("employee_form", clear_on_submit=True):
        emp_id = st.text_input("Employee Card/ID Number")
        emp_name = st.text_input("Full Name")
        mobile = st.text_input("Mobile Number")
        emp_type = st.selectbox("Compensation Model", ["Piece Rate Basis", "Salary Basis", "Contractor"])
        address = st.text_input("Residential Address/Village Name")
        
        if st.form_submit_button("Register Employee Account"):
            if emp_name and emp_id:
                db.add_employee(emp_id, emp_name, mobile, emp_type, address)
                st.success(f"Registered {emp_name} successfully into the workforce ledger!")
                st.rerun()
