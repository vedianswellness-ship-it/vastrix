import streamlit as st
import pymongo

class DatabaseManager:
    def __init__(self):
        """Initialize connection using Streamlit secrets."""
        self.client = self._init_connection()
        # Default database and collection names
        self.db = self.client["my_database"]
        self.collection = self.db["my_collection"]
        # Inside db_manager.py
@st.cache_resource
def _init_connection(_self):
    try:
        # Hardcode temporarily just to test the connection locally
        connection_string = "mongodb+srv://shona_db_user:YOUR_NEW_SECRET_PASSWORD@cluster0.eotergv.mongodb.net/?retryWrites=true&w=majority"
        return pymongo.MongoClient(connection_string)
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        raise

   @st.cache_resource
    def _init_connection(_self):
        """Establishes and caches the MongoDB Connection."""
        # 1. First, check if the "mongo" key actually exists in secrets
        if "mongo" not in st.secrets:
            st.error("❌ Streamlit Secrets Error: The '[mongo]' section was not found in your settings!")
            st.info("If you are on Streamlit Cloud, please open 'Manage app' -> 'Settings' -> 'Secrets' and paste your [mongo] credentials there.")
            raise AttributeError("Missing [mongo] configuration block in secrets.")
            
        try:
            # 2. Get the connection string safely
            connection_string = st.secrets["mongo"]["connection_string"]
            return pymongo.MongoClient(connection_string)
        except Exception as e:
            st.error(f"❌ MongoDB Connection failed: {e}")
            raise

    def insert_record(self, data: dict):
        """Inserts a single document into the collection."""
        try:
            return self.collection.insert_one(data)
        except Exception as e:
            st.error(f"Error inserting record: {e}")
            return None

    def fetch_all_records(self):
        """Fetches all documents from the collection."""
        try:
            return list(self.collection.find())
        except Exception as e:
            st.error(f"Error fetching records: {e}")
            return []
