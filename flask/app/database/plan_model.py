from firebase_admin import firestore
from datetime import datetime
import pytz

db = firestore.client()

class Plan:
    PLAN_TYPES = ["Daily", "Weekly", "Monthly"]

    def __init__(self, plan_type, plan_desc, plan_price):
        self.planId = self.set_plan_id(plan_type)
        self.plan_type = plan_type
        self.plan_desc = plan_desc
        self.plan_price = plan_price
        self.created_at = datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        self.updated_at = self.created_at

        # Validate plan fields
        self.validate()

    def validate(self):
        if self.plan_type not in self.PLAN_TYPES:
            raise ValueError("Invalid plan type. Must be 'Daily', 'Weekly', or 'Monthly'.")
        if not isinstance(self.plan_desc, str) or not self.plan_desc:
            raise ValueError("Please enter a valid subscription description.")
        if not isinstance(self.plan_price, (int, float)) or not (0 <= self.plan_price <= 2790):
            raise ValueError("Please enter a price between 0 and 2790.")

    def set_plan_id(self, plan_type):
        # Sets planId based on plan_type
        if plan_type == "Daily":
            return 501
        elif plan_type == "Weekly":
            return 502
        elif plan_type == "Monthly":
            return 503
        return 500

    def save(self):
        plan_data = {
            'planId': self.planId,
            'plan_type': self.plan_type,
            'plan_desc': self.plan_desc,
            'plan_price': self.plan_price,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

        # Save to Firestore
        plan_ref = db.collection('plans').document()  # Creates a unique ID
        plan_ref.set(plan_data)
        return plan_data
