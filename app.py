import streamlit as st
from db_manager import DatabaseManager

# Optimize configuration for mobile viewports
st.set_page_config(
    page_title="App Hub", 
    page_icon="📱", 
    layout="centered",          # Keeps layout tight and readable on mobile
    initial_sidebar_state="collapsed"  # Hides sidebar by default to save screen space
)

# Custom minimal CSS styling for mobile-friendly spacing
st.markdown("""
    <style>
    /* Reduce excessive vertical padding on small screens */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    /* Style form buttons to be prominent and touch-friendly */
    div.stButton > button:first-child {
        width: 100%;
        height: 3rem;
        font-weight: bold;
        border-radius: 8px;
    }
    /* Style database records like clean mobile info-cards */
    .mobile-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.title("📱 Task Manager")

# Initialize DB Manager
db_manager = DatabaseManager()

# Section 1: Mobile-Optimized Input Form using an expander to save space
with st.expander("➕ Add New Record", expanded=True):
    with st.form("add_item_form", clear_on_submit=True):
        name = st.text_input("Item Name", placeholder="e.g., Inventory Audit")
        notes = st.text_area("Notes / Remarks", placeholder="Enter specific details...")
        
        submitted = st.form_submit_button("Save Entry")
        
        if submitted:
            if name.strip() == "":
                st.error("Item Name cannot be blank.")
            else:
                payload = {"name": name, "notes": notes}
                result = db_manager.insert_record(payload)
                if result:
                    st.success("Saved successfully!")
                    st.rerun()  # Instantly refreshes mobile UI to show new data

st.write("---")

# Section 2: View Records in Clean Mobile-friendly Cards
st.subheader("Stored Records")
records = db_manager.fetch_all_records()

if not records:
    st.info("No records found in the database yet
