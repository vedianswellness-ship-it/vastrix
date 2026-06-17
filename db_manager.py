import streamlit as st
import pymongo

class DatabaseManager:
    def __init__(self):
        """Initialize connection using Streamlit secrets."""
        self.client = self._init_connection()
        # Default database and collection names
        self.db = self.client["my_database"]
        self.collection = self.db["my_collection"]

    @st.cache_resource
    def _init_connection(_self):
        """Establishes and caches the MongoDB Connection."""
        try:
            connection_string = st.secrets["mongo"]["connection_string"]
            return pymongo.MongoClient(connection_string)
        except KeyError:
            st.error("Missing 'mongo' configuration in secrets.toml!")
            raise
        except Exception as e:
            st.error(f"Failed to connect to MongoDB: {e}")
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
