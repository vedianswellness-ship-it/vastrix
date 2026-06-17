import streamlit as st
st.write(st.secrets)  # This will print your active secret keys on the screen to debug
import streamlit as st
import pymongo

# Page layout
st.set_page_config(page_title="My MongoDB Web App", layout="centered")
st.title("🚀 Streamlit + MongoDB Atlas")

# Connect to MongoDB using the connection string from secrets.toml
@st.cache_resource
def init_connection():
    # Looks inside .streamlit/secrets.toml automatically
    return pymongo.MongoClient(st.secrets["mongo"]["connection_string"])

try:
    client = init_connection()
    db = client["my_database"]  # Feel free to change database name
    collection = db["my_collection"]  # Feel free to change collection name
    
    st.success("Successfully connected to MongoDB Atlas!")
    
    # Simple UI Form to insert data to test it
    st.subheader("Add a record to MongoDB")
    with st.form("test_form"):
        name = st.text_input("Item Name")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Save to Database")
        
        if submitted and name:
            collection.insert_one({"name": name, "notes": notes})
            st.balloons()
            st.success(f"Saved '{name}' to MongoDB!")

except Exception as e:
    st.error(f"Connection failed: {e}")
