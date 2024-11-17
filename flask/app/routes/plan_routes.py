from flask import Blueprint, request, jsonify,current_app
from ..database.db_connect import connection
from datetime import datetime
import pytz
from ..database.plan_model import Plan

client = connection()
users= client.collection("users")  # Database
plans = client.collection("plans")

# Create a blueprint for user routes
plan_bp = Blueprint('plan', __name__)

@plan_bp.route('/add', methods=['POST'])
def add_plan():
    data = request.json
    plan_type = data.get('plan_type')
    plan_desc = data.get('plan_desc')
    plan_price = data.get('plan_price')

    # Confirm data
    if not all([plan_type, plan_desc, plan_price]):
        return jsonify({'message': 'All fields (plan_type, plan_desc, plan_price) are required'}), 400

    try:
        # Check for duplicate entry
        duplicate_query = plans.where('plan_type', '==', plan_type).limit(1).get()
        
        if duplicate_query:
            # Update the existing plan if duplicate found
            plan_doc_ref = duplicate_query[0].reference
            plan_doc_ref.update({
                'plan_desc': plan_desc,
                'plan_price': plan_price,
                'updated_at': datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
            })
            return jsonify({'message': f'{plan_type} plan updated'}), 200

        # Create new plan if no duplicate
        new_plan = Plan(plan_type, plan_desc, plan_price)
        saved_plan = new_plan.save()
        
        return jsonify({'message': f'Your {plan_type} added', 'data': saved_plan}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@plan_bp.route('/getPlan/<string:plan_type>', methods=['GET'])
def get_plan(plan_type):
    # Confirm data
    if not plan_type:
        return jsonify({'message': 'Plan Type Required'}), 400

    try:
        # Query for the specific plan by plan_type
        plan_query = plans.where('plan_type', '==', plan_type).limit(1).get()
        
        if not plan_query:
            return jsonify({'message': 'No plan found'}), 404

        # Convert the document to a dictionary
        plan = plan_query[0].to_dict()
        return jsonify({'plan': plan, 'message': 'Plan is on screen'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@plan_bp.route('/plans', methods=['GET'])
def get_all_plans():
    try:
        # Query for all plans in the collection
        plans_query = plans.stream()
        plans_data = [plan.to_dict() for plan in plans_query]

        if not plans_data:
            return jsonify({'message': 'No plan set yet'}), 404

        return jsonify(plans_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@plan_bp.route('/', methods=['GET'])
def greet():
    return jsonify({'message': 'Welcome to the Plan API'}), 200