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
        self.daily_work = self.db["daily_work"]
        self.lots = self.db["lots"]  
        self.products = self.db["products"]  # New Collection for Product Operations Blueprint

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
                "emp_type": emp_type,
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

    # --- PRODUCT PROCESS BLUEPRINT MASTER ---
    def add_product_template(self, product_name, steps_list):
        """Saves a product profile alongside its complete engineering operation sequence & rates."""
        try:
            payload = {
                "product_name": product_name,
                "operations": steps_list,  # List of dicts: [{"operation": "Overlock", "rate": 3.0}, ...]
                "updated_at": datetime.now().strftime("%Y-%m-%d")
            }
            # Update if exists, insert if new
            return self.products.update_one({"product_name": product_name}, {"$set": payload}, upsert=True)
        except Exception as e:
            st.error(f"Error updating product process profile: {e}")
            return None

    def get_all_products(self):
        """Fetches all product routing templates."""
        return list(self.products.find({}, {"_id": 0}))

    # --- CUTTING DEPARTMENT (LOT & BUNDLE CREATION) ---
    def create_cutting_lot(self, lot_no, product_name, total_pcs, bundle_qty):
        """Creates a cutting lot linked to a product's operations template."""
        try:
            total_pcs = int(total_pcs)
            bundle_qty = int(bundle_qty)
            
            # Fetch product template rules to verify operation workflow exists
            prod_template = self.products.find_one({"product_name": product_name})
            operations = prod_template.get("operations", []) if prod_template else []

            # Auto-calculate sequential bundle cards layout
            bundles = []
            remaining_pcs = total_pcs
            bundle_index = 1
            
            while remaining_pcs > 0:
                current_bundle_size = min(bundle_qty, remaining_pcs)
                bundles.append({
                    "bundle_no": f"{lot_no}-B{bundle_index}",
                    "qty": current_bundle_size,
                    "status": "Available",
                    "assigned_to": None
                })
                remaining_pcs -= current_bundle_size
                bundle_index += 1

            payload = {
                "lot_no": lot_no,
                "product_name": product_name,
                "total_pcs": total_pcs,
                "operations_blueprint": operations,  # Embedded copy snapshot of operational costs
                "bundles": bundles,
                "created_at": datetime.now().strftime("%Y-%m-%d")
            }
            return self.lots.insert_one(payload)
        except Exception as e:
            st.error(f"Failed to save cutting lot: {e}")
            return None

    def get_active_lots(self):
        """Fetches all cutting lots."""
        return list(self.lots.find({}, {"_id": 0}))

    def update_bundle_status(self, lot_no, bundle_no, worker_name):
        """Marks a bundle as completed/assigned by a worker."""
        try:
            self.lots.update_one(
                {"lot_no": lot_no, "bundles.bundle_no": bundle_no},
                {"$set": {
                    "bundles.$.status": "Completed",
                    "bundles.$.assigned_to": worker_name
                }}
            )
        except Exception as e:
            st.error(f"Failed to lock bundle tracking: {e}")

    # --- TRANSACTION ENTRIES ---
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
