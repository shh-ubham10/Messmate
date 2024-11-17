import firebase_admin
from firebase_admin import firestore
from datetime import datetime
import pytz
from firebase_admin import initialize_app

# Initialize Firebase app (only once)
if not firebase_admin._apps:
    initialize_app()

# Firestore connection
db = firestore.client()

class Inventory:
    def __init__(self, name, store_type, qty, single_price):
        self.name = name
        self.store_type = store_type
        self.qty = qty
        self.single_price = single_price
        self.date = None
        self.used_qty = 0
        self.remain_qty = None
        self.sub_total = None
        self.inventory_id = None

    def save(self):
        # Set the current date with time zone
        self.date = datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()

        # Calculate sub_total and remaining quantity
        self.sub_total = self.qty * self.single_price
        self.remain_qty = self.qty - self.used_qty

        # Create an inventory document without the ID first
        inventory_data = {
            'name': self.name,
            'storeType': self.store_type,
            'qty': self.qty,
            'usedQty': self.used_qty,
            'remainQty': self.remain_qty,
            'singlePrice': self.single_price,
            'subTotal': self.sub_total,
            'date': self.date
        }

        # Save the document to Firestore and get the document reference
        doc_ref = db.collection('inventory').add(inventory_data)  # This generates a unique document ID

        # Now we have the auto-generated document ID, we can update the document to include the inventoryId
        # Update the document with the inventoryId
        doc_ref[1].update({'inventoryId': doc_ref[1].id})  # This will set inventoryId to the document ID

        # Return the full inventory data with the custom inventoryId
        inventory_data['inventoryId'] = doc_ref[1].id  # Set the custom ID to return

        return inventory_data