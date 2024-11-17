import firebase_admin
from firebase_admin import firestore
from datetime import datetime
import pytz

# Initialize Firebase app (only once)
if not firebase_admin._apps:
    firebase_admin.initialize_app()

# Firestore connection
db = firestore.client()

class Menu:
    def __init__(self, menu_day, menu_breakfast, menu_lunch, menu_dinner, special_menu=None):
        self.menu_id = None  # This will be set later
        self.menu_day = menu_day
        self.menu_breakfast = menu_breakfast
        self.menu_lunch = menu_lunch
        self.menu_dinner = menu_dinner
        self.special_menu = special_menu or []
        self.date_created = datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()

    def save(self):
        # Query Firestore to get the current count of menus for auto-incrementing menuId
        menu_ref = db.collection('menu')
        # Create the menu document
        menu_data = {
            'menu_day': self.menu_day,
            'menu_breakfast': self.menu_breakfast,
            'menu_lunch': self.menu_lunch,
            'menu_dinner': self.menu_dinner,
            'special_menu': self.special_menu,
            'date_created': self.date_created
        }

        # Save the document to Firestore and get the document reference
        doc_ref = menu_ref.add(menu_data)  # This generates a unique document ID

        # Now we have the auto-generated document ID, we can update the document to include the menuId
        # Update the document with the menuId
        doc_ref[1].update({'menuId': doc_ref[1].id})  # This will set menuId to the document ID

        # Return the full menu data with the custom menuId
        menu_data['menuId'] = doc_ref[1].id  # Set the custom ID to return

        return menu_data