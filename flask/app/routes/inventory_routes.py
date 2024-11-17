from flask import Blueprint, request, jsonify
from ..database.db_connect import connection
from ..database.inventory_model import Inventory

client = connection()
inventory= client.collection("inventory") 

# Create a blueprint for user routes
inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/store/<string:storeType>', methods=['GET'])
def get_store(storeType):
    if not storeType:
        return jsonify({'message': 'Store Type Required'}), 400

    # Query Firestore for the inventory by store type
    store_query = inventory.where('storeType', '==', storeType).stream()

    # Convert Firestore documents to a list of dictionaries
    store = [doc.to_dict() for doc in store_query]

    # If no stores found
    if not store:
        return jsonify({'message': 'No stores found'}), 400

    return jsonify(store), 200

@inventory_bp.route('/<string:inventoryId>', methods=['GET'])
def get_inventory(inventoryId):
    if not inventoryId:
        return jsonify({'message': 'Inventory ID Required'}), 400

    # Query Firestore for the inventory item by inventory ID
    inventory_query = inventory.where('inventoryId', '==', inventoryId).limit(1).stream()

    # Get the first result
    inventory_item = next(inventory_query, None)

    if not inventory_item:
        return jsonify({'message': 'No inventory found'}), 400

    # Convert Firestore document to a dictionary
    inventory_data = inventory_item.to_dict()

    return jsonify(inventory_data), 200


@inventory_bp.route('/add', methods=['POST'])
def add_inventory():
    data = request.json
    try:
        new_inventory = Inventory(
            name=data.get('name'),
            store_type=data.get('storeType'),
            qty=data.get('qty'),
            single_price=data.get('single_price')
        )
        inventory_data = new_inventory.save()
        return jsonify({'message': 'New inventory added successfully', 'data': inventory_data}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

@inventory_bp.route('/update/<string:inventory_id>', methods=['PUT'])
def update_inventory(inventory_id):
    data = request.json
    name = data.get('name')
    store_type = data.get('storeType')
    qty = data.get('qty')
    used_qty = data.get('usedqty', 0)  # Defaults to 0 if not provided
    single_price = data.get('single_price')

    # Reference to the inventory collection

    # Query for the inventory by inventoryId
    inventory_query = inventory.where('inventoryId', '==', inventory_id).limit(1).stream()
    inventory_doc = next(inventory_query, None)

    if not inventory_doc:
        return jsonify({'message': 'No inventory found'}), 404

    # Get the existing inventory data
    existing_inventory = inventory_doc.to_dict()
    
    # Calculate the new values
    used_qty = existing_inventory.get('usedQty', 0) + used_qty
    remain_qty = qty - used_qty
    sub_total = qty * single_price

    # Create an updated inventory object
    inventory_object = {
        'name': name,
        'storeType': store_type,
        'qty': qty,
        'usedQty': used_qty,
        'remainQty': remain_qty,
        'singlePrice': single_price,
        'subTotal': sub_total
    }

    # Update the inventory in Firestore
    inventory.document(inventory_doc.id).update(inventory_object)

    return jsonify({'message': 'Inventory updated successfully'}), 200


@inventory_bp.route('/delete/<string:inventory_id>', methods=['DELETE'])
def delete_inventory(inventory_id):

    # Query for the inventory by inventoryId
    inventory_query = inventory.where('inventoryId', '==', inventory_id).limit(1).stream()
    inventory_doc = next(inventory_query, None)

    if not inventory_doc:
        return jsonify({'message': 'No inventory found'}), 404

    # Delete the inventory document
    inventory.document(inventory_doc.id).delete()

    return jsonify({'message': 'Inventory deleted successfully'}), 200


@inventory_bp.route('/', methods=["GET"])
def greet():
    return jsonify({"message": "Welcome to the Inventory API"}), 200