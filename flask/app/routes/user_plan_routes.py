from flask import Blueprint, request, jsonify,current_app
from ..database.db_connect import connection
from datetime import datetime, timedelta, timezone
import pytz
from ..database.user_plan_model import UserPlan
import json

client = connection()
users= client.collection("users")  # Database
plans = client.collection("plans")
user_plans = client.collection("userplans")

# Create a blueprint for user routes
user_plan_bp = Blueprint('userplan', __name__)

IST = timezone(timedelta(hours=5, minutes=30))

def get_tomorrow_ist_start(day_offset=1):
    today = datetime.now(IST)
    tomorrow = today + timedelta(days=day_offset)
    return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)

@user_plan_bp.route("/getUserPlan/<int:userId>", methods=["GET"])
def get_user_current_plan(userId):
    tomorrow_start = get_tomorrow_ist_start()

    try:
        # Query Firestore for the user's current plan
        current_plan_stream = user_plans.where("userId", "==", userId).where("start_date", "<=", tomorrow_start).where("end_date", ">=", tomorrow_start).stream()
        current_plan = []
        for plan in current_plan_stream:
            current_plan.append(plan.to_dict())  # Get the plan data
   
        # Check if a plan was found
        if not current_plan:
            return jsonify({"message": "No current plan found"}), 400

        return jsonify(current_plan), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@user_plan_bp.route("/get_current_plan", methods=["GET"])
def get_current_plan():
    try:
        # Fetch all documents in the userplans collection
        userplans = user_plans.stream()

        # Process data to group by _id and select required fields
        user_list = []
        for user in userplans:
            user_data = user.to_dict()
            user_list.append({
                "_id": user.id,
                "userId": user_data.get("userId"),
                "planId": user_data.get("planId"),
                "start_date": user_data.get("start_date"),
                "end_date": user_data.get("end_date"),
                "fees": user_data.get("fees"),
                "fee_status": user_data.get("fee_status"),
            })

        # Sort users by userId (similar to MongoDB's $sort)
        user_list = sorted(user_list, key=lambda x: x["userId"])

        if not user_list:
            return jsonify({"message": "No users found"}), 400

        return jsonify(user_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_plan_bp.route("/add", methods=["POST"])
def add_user_plan():
    # Read data from request body
    data = request.get_json()
    userId = data.get("regNo")
    planId = data.get("planId")
    fees = data.get("fees")
    fees_status = data.get("fee_status")

    # Validate required fields
    if not userId or not planId or fees is None:
        return jsonify({"message": "Invalid user data received"}), 400
    
    plan_stream = plans.where("planId", "==", planId).limit(1).stream()
    current_plan = None
    for plan in plan_stream:
        current_plan = plan.to_dict() 

    # Check if current_plan is None
    if not current_plan:
        return jsonify({"message": "Invalid planId"}), 400
    
    # Now we can access the plan_type
    if current_plan.get("plan_type") == "Weekly":
        end_date = datetime.now(IST) + timedelta(days=7)
    elif current_plan.get("plan_type") == "Monthly":
        end_date = datetime.now(IST) + timedelta(days=30)  # Changed from months to days
    elif current_plan.get("plan_type") == "Daily":
        end_date = datetime.now(IST) + timedelta(days=1)
    else:
        return jsonify({"message": "Invalid plan type"}), 400

    # Create user plan object
    user_plan_object = {
        "userId": userId,
        "planId": planId,
        "fees": fees,
        "start_date": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
        "end_date": end_date,
        "fee_status": fees_status,
    }

    # Save the new user plan to Firestore
    user_plans.add(user_plan_object)

    # Send a response indicating success
    return jsonify({
        "message": f"New user plan for user {userId} created with plan {planId}"
    }), 201

@user_plan_bp.route("/update_user_plan", methods=["POST"])
def update_user_plan():
    data = request.get_json()
    userId = data.get("userId")
    planId = data.get("planId")

    if not userId or not planId:
        return jsonify({"message": "userId and planId are required"}), 400

    try:
        # Query to find the document with matching userId and planId
        user_plan_query = user_plans.where("userId", "==", userId).where("planId", "==", planId).limit(1)
        user_plan_docs = user_plan_query.stream()
        
        user_plan = None
        for doc in user_plan_docs:
            user_plan = doc
            break

        # If no matching document was found, return an error
        if not user_plan:
            return jsonify({"message": "User Plan not found"}), 400

        # Update the fee_status to true
        user_plans.document(user_plan.id).update({"fee_status": True})
        return jsonify({"message": f"Fee status for userId {userId} and planId {planId} updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_plan_bp.route("/update_consent", methods=["POST"])
def update_consent():
    data = request.get_json()
    userId = data.get("regNo")
    planId = data.get("planId")
    date_str = data.get("date")
    breakfast = data.get("breakfast")
    lunch = data.get("lunch")
    dinner = data.get("dinner")

    if not userId or not planId or not date_str:
        return jsonify({"message": "userId, planId, and date are required"}), 400

    # Convert the date to the required format
    try:
        # Parse date and set it to the start of the day
        date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=pytz.timezone("Asia/Kolkata")).date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD."}), 400

    updated_object = {
        "date": date.isoformat(),
        "breakfast": breakfast,
        "lunch": lunch,
        "dinner": dinner
    }

    try:
        # Find the user plan document with matching userId and planId
        user_plan_query = user_plans.where("userId", "==", userId).where("planId", "==", planId).limit(1)
        user_plan_docs = user_plan_query.stream()

        user_plan = None
        for doc in user_plan_docs:
            user_plan = doc
            break

        if not user_plan:
            return jsonify({"message": "User Plan not found"}), 400

        # Get the current data of isavailable and update the target date entry
        user_plan_data = user_plan.to_dict()
        isavailable = user_plan_data.get("isavailable", [])

        # Update the entry for the given date, or add a new entry if not found
        updated = False
        for item in isavailable:
            if item["date"] == date.isoformat():
                item.update(updated_object)
                updated = True
                break
        if not updated:
            isavailable.append(updated_object)

        # Update the document in Firestore
        user_plans.document(user_plan.id).update({"isavailable": isavailable})

        return jsonify({"message": f"Consent status for userId {userId} updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_plan_bp.route("/get_consent", methods=["GET"])
def get_consent():
    data = request.get_json()
    userId = data.get("regNo")
    planId = data.get("planId")
    date_str = data.get("date")

    if not userId or not planId or not date_str:
        return jsonify({"message": "userId, planId, and date are required"}), 400

    try:
        # Convert date to required format
        date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=pytz.timezone("Asia/Kolkata")).date()
        date_iso = date.isoformat()

        # Find the user plan document with matching userId and planId
        user_plan_query = user_plans.where("userId", "==", userId).where("planId", "==", planId).limit(1)
        user_plan_docs = user_plan_query.stream()

        user_plan = None
        for doc in user_plan_docs:
            user_plan = doc
            break

        if not user_plan:
            return jsonify({"message": "User Plan not found"}), 400

        # Filter the isavailable array for the specified date
        user_plan_data = user_plan.to_dict()
        isavailable = user_plan_data.get("isavailable", [])
        consent_data = next((item for item in isavailable if item["date"] == date_iso), None)

        if consent_data:
            return jsonify(consent_data), 200
        else:
            return jsonify({"message": "Consent data for the specified date not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_plan_bp.route("/get_user_today_plan/<userId>", methods=["GET"])
def get_user_today_plan(userId):
    # Get today's date at the start of the day in the target timezone
    today_date = get_tomorrow_ist_start(day_offset=1)


    try:

      
        # Find the user plan document by userId and date range
        user_plan_query = user_plans.where("userId", "==", int(userId)).where("start_date", "<=", today_date).where("end_date", ">=", today_date)
        

        user_plan_docs = user_plan_query.stream()

        user_plan = None
        for doc in user_plan_docs:
            user_plan = doc
            break

        if not user_plan:
            return jsonify({"message": "No users found"}), 400

        # Filter isavailable for today's date
        user_plan_data = user_plan.to_dict()
        isavailable = user_plan_data.get("isavailable", [])
        for item in isavailable:
            print(item["date"], today_date)
            if item["date"] == today_date:
                today_plan = item
                print("true one piece is real")
        today_plan = next((item for item in isavailable if item["date"] == today_date), None)

        if not today_plan:
            return jsonify({"message": "No available plan for today"}), 404

        # Prepare the response with required fields
        response_data = {
            "userId": user_plan_data.get("userId"),
            "planId": user_plan_data.get("planId"),
            "fees": user_plan_data.get("fees"),
            "fee_status": user_plan_data.get("fee_status"),
            "isavailable": today_plan
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_plan_bp.route("/get_today_students/<string:type>", methods=["GET"])
def get_today_students(type):
    # Get the current date and time in IST
    IST = timezone(timedelta(hours=5, minutes=30))

# Get the current date and time in IST
    today = datetime.now(IST)
    today_date = today.isoformat()

    meal_key = type.lower()  # Convert type to lowercase to match Firestore field names

    if meal_key not in ["breakfast", "lunch", "dinner"]:
        return jsonify({"message": "Invalid meal type"}), 400

    try:
        # Query user plans active for today
        user_plans_stream = user_plans.where("start_date", "<=", today_date).where("end_date", ">=", today_date).stream()

        # Filter results based on availability for the specified meal type
        students_list = []
        for plan in user_plans_stream:
            plan_data = plan.to_dict()
            isavailable = plan_data.get("isavailable", [])

            # Check if today's date is available for the specified meal type
            for availability in isavailable:
                # Parse the 'date' field and convert it to a datetime object
                availability_date = datetime.fromisoformat(availability.get("date")).replace(hour=0, minute=0, second=0, microsecond=0)

                # Compare dates to ensure they match
                if availability_date == today_date and availability.get(meal_key):
                    students_list.append({
                        "userId": plan_data["userId"],
                        "planId": plan_data["planId"],
                        "fee_status": plan_data["fee_status"]
                    })
                    break

        # Sort the result by userId
        students_list = sorted(students_list, key=lambda x: x["userId"])

        if not students_list:
            return jsonify({"message": "No users found"}), 400
        
        return jsonify(students_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@user_plan_bp.route('/', methods=['GET'])
def get_user_plans():
    return jsonify({'message': 'User Plans'}), 200

