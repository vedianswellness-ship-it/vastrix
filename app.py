import streamlit as st
# Import the DatabaseManager class we just made
from db_manager import DatabaseManager

st.set_page_config(page_title="My Managed Web App", layout="centered")
st.title("🚀 Streamlit + MongoDB App Layout")

# Instantiate our database manager
db_manager = DatabaseManager()

# Form UI to insert data
st.subheader("Add a Record")
with st.form("add_item_form"):
    name = st.text_input("Item Name")
    notes = st.text_area("Notes")
    submitted = st.form_submit_button("Save to Database")
    
    if submitted and name:
        payload = {"name": name, "notes": notes}
        result = db_manager.insert_record(payload)
        if result:
            st.success(f"Saved '{name}' successfully!")
            st.balloons()

st.write("---")

# UI to view data
st.subheader("Current Database Records")
records = db_manager.fetch_all_records()

if not records:
    st.info("No records found in the database yet.")
else:
    for record in records:
        st.write(f"**Name:** {record.get('name')} | **Notes:** {record.get('notes')}")
