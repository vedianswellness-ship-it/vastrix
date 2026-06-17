import streamlit as st
import pymongo
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        """Initialize connection and structure Vastrix collections."""
        self.client = self._init_connection()
        # Vastrix Database Core Collections
        self.db = self.client["vastrix_erp"]
        self.employees = self.db["employees"]
        self.processes = self.db["processes"]
        self.daily_work = self.db["daily_work"]

    @st.cache_resource
    def _init_connection(_self):
        """Establishes a cached, secure connection to MongoDB."""
        if "mongo" not in st.secrets:
            st.error("❌ Configuration Error: Please paste your [mongo] string into Streamlit settings.")
            raise AttributeError("Missing database secret credentials.")
        try:
            return pymongo.MongoClient(st.secrets["mongo"]["connection_string"])
        except Exception as e:
            st.error(f"❌ Database connection timeout: {e}")
            raise

    # --- EMPLOYEE MASTER OPERATIONS ---
    def add_employee(self, emp_id, name, mobile, emp_type, address, base_salary=0.0):
        """Saves a new worker with their compensation profile and base salary if applicable."""
        try:
            payload = {
                "emp_id": emp_id,
                "name": name,
                "mobile": mobile,
                "emp_type": emp_type,  # Salary Basis, Piece Rate Basis, Contractor
                "address": address,
                "joining_date": datetime.now().strftime("%Y-%m-%d"),
                "base_salary": float(base_salary) if emp_type == "Salary Basis" else 0.0
            }
            return self.employees.insert_one(payload)
        except Exception as e:
            st.error(f"Error adding employee: {e}")
            return None

    def get_all_employees(self):
        """Fetches all workers registered in the factory system."""
        return list(self.employees.find({}, {"_id": 0}))

    # --- PROCESS MASTER OPERATIONS ---
    def add_process(self, item_type, process_name, machine, rate):
        """Inserts unique task definitions into the piece-rate process master."""
        try:
            payload = {
                "item_type": item_type,       # e.g., T-Shirt, Lower
                "process_name": process_name, # e.g., Overlock, Flatlock, Steam Press
                "machine": machine,
                "rate": float(rate)           # Per-piece rate in ₹
            }
            return self.processes.insert_one(payload)
        except Exception as e:
            st.error(f"Error updating process master: {e}")
            return None

    def get_all_processes(self):
        """Fetches all defined garment production rates."""
        return list(self.processes.find({}, {"_id": 0}))

    # --- TRANSACTION ENTRIES (PIECE-WORK OR ATTENDANCE/SALARY CALCS) ---
    def log_daily_entry(self, payload):
        """Logs daily worker transaction (Piece work or Salary Attendance)."""
        try:
            payload["timestamp"] = datetime.now()
            return self.daily_work.insert_one(payload)
        except Exception as e:
            st.error(f"Failed to submit entry: {e}")
            return None

    def get_daily_summary_stats(self):
        """Aggregates metrics for the manager dashboard screen."""
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            today_entries = list(self.daily_work.find({"date": today_str}))
            
            total_pieces = sum(item.get("qty", 0) for item in today_entries if "qty" in item)
            total_payout = sum(item.get("total_amount", 0) for item in today_entries)
            
            return {
                "pieces_produced": total_pieces,
                "payout_incurred": total_payout,
                "entries_count": len(today_entries)
            }
        except Exception as e:
            return {"pieces_produced": 0, "payout_incurred": 0, "entries_count": 0}
