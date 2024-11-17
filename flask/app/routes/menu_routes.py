from flask import Blueprint, request, jsonify
from ..database.db_connect import connection
from ..database.menu_model import Menu

client = connection()
menu_collection = client.collection("menu") 

# Create a blueprint for menu routes
menu_bp = Blueprint('menu', __name__)
VALID_DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

@menu_bp.route('/add', methods=['POST'])
def add_menu():
    data = request.json
    try:
        # Validate data
        menu_day = data.get('menu_day')
        menu_breakfast = data.get('menu_breakfast')
        menu_lunch = data.get('menu_lunch')
        menu_dinner = data.get('menu_dinner')
        
        if not (menu_day and menu_breakfast and menu_lunch and menu_dinner):
            return jsonify({'error': 'Please provide all required fields.'}), 400

        # Validate the menu_day
        if menu_day not in VALID_DAYS:
            return jsonify({'error': f'menu_day must be one of the following: {", ".join(VALID_DAYS)}.'}), 400

        # Check if menu for the specified day already exists
        existing_menu_query = menu_collection.where('menu_day', '==', menu_day).limit(1).get()
        
        if existing_menu_query:
            # Update existing document
            existing_doc = existing_menu_query[0].reference
            existing_doc.update({
                'menu_breakfast': menu_breakfast,
                'menu_lunch': menu_lunch,
                'menu_dinner': menu_dinner,
                'special_menu': data.get('special_menu', [])
            })
            return jsonify({'message': 'Menu updated successfully for ' + menu_day}), 200
        else:
            # Create a new menu
            new_menu = Menu(menu_day, menu_breakfast, menu_lunch, menu_dinner, data.get('special_menu'))
            saved_menu_data = new_menu.save()  # Save and get the dictionary data
            return jsonify({'data': saved_menu_data}), 201  # Return the saved menu data
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/<menu_day>', methods=['GET'])
def get_menu(menu_day):
    # Confirm data
    if not menu_day:
        return jsonify({'message': 'Menu Day Required'}), 400

    try:
        # Query Firestore for menu by day
        menu_query = menu_collection.where('menu_day', '==', menu_day).stream()
        menu = [doc.to_dict() for doc in menu_query]

        # Check if menu exists
        if not menu:
            return jsonify({'message': 'No menu found'}), 404

        return jsonify({'menu': menu, 'message': "Your menu on screen"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@menu_bp.route('/delete', methods=['DELETE'])
def delete_menu():
    data = request.json
    menu_day = data.get('menu_day')

    # Confirm data
    if not menu_day:
        return jsonify({'message': 'Menu Day Required'}), 400

    try:
        # Find the menu for the specified day
        menu_query = menu_collection.where('menu_day', '==', menu_day).limit(1).get()
        
        if not menu_query:
            return jsonify({'message': 'Menu not found'}), 404

        # Delete the document
        menu_doc_ref = menu_query[0].reference
        menu_doc_ref.delete()

        return jsonify({'message': f'Menu of {menu_day} deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500  

@menu_bp.route('/', methods=['GET'])
def get():
    return jsonify({"message": "Welcome to the Menu API"}), 200
