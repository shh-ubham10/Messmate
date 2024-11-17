from flask import Blueprint, jsonify
from datetime import datetime, timedelta
import pytz
from ..database.db_connect import connection

client = connection()
inventory_collection = client.collection("inventory")
user_plans_collection = client.collection("user_plans")

# Create a blueprint for stats routes
stats_bp = Blueprint('stats', __name__)

def get_date_range(start_of, end_of):
    timezone = pytz.timezone("Asia/Kolkata")
    start_date = timezone.localize(datetime.now()).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = timezone.localize(datetime.now()).replace(hour=23, minute=59, second=59, microsecond=999999)
    if start_of == "month":
        start_date = start_date.replace(day=1)
    elif start_of == "week":
        start_date -= timedelta(days=start_date.weekday())
    if end_of == "month":
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    elif end_of == "week":
        end_date += timedelta(days=6 - end_date.weekday())
    return start_date, end_date

@stats_bp.route('/getMonthlyExpenses', methods=['GET'])
def get_monthly_expenses():
    start_date, end_date = get_date_range("month", "month")
    expense_summary = {}

    # Query inventory data for the specified date range
    start_date_str = start_date.isoformat()
    end_date_str = end_date.isoformat()

    # Query inventory data for the specified date range
    inventory_docs = inventory_collection.where("date", ">=", start_date_str).where("date", "<=", end_date_str).stream()

    for doc in inventory_docs:
        item = doc.to_dict()  # Convert each Firestore document to a dictionary
        store_type = item.get("storeType", "Unknown")
        if store_type not in expense_summary:
            expense_summary[store_type] = {"expense": 0, "qty": 0, "remainqty": 0}
        
        expense_summary[store_type]["expense"] += item.get("sub_total", 0)
        expense_summary[store_type]["qty"] += item.get("qty", 0)
        expense_summary[store_type]["remainqty"] += item.get("remainqty", 0)

    grouped_expenses = [
        {"storeType": store_type, "expense": summary["expense"], "qty": summary["qty"], "remainqty": summary["remainqty"]}
        for store_type, summary in expense_summary.items()
    ]

    return jsonify(grouped_expenses)


@stats_bp.route('/get_week_profit', methods=['GET'])
def get_week_profit():
    # Set IST offset
    start_date, end_date = get_date_range("week", "week")


    # Query inventory data for the specified date range
    start_date = start_date.isoformat()
    end_date = end_date.isoformat()


    # Query Firestore for documents within date range
    user_docs = user_plans_collection \
                  .where("date", ">=", start_date) \
                  .where("date", "<=", end_date) \
                  .stream()
    # Aggregate and group data by start_date
    user_data = {}
    for doc in user_docs:
        data = doc.to_dict()
        start_date = data["start_date"].strftime('%Y-%m-%d')
        
        # Initialize total if date not in user_data
        if start_date not in user_data:
            user_data[start_date] = 0
        user_data[start_date] += data.get("fees", 0)

    # Convert aggregated data to desired format
    grouped_people = [{"date": date, "amount": amount} for date, amount in user_data.items()]
    
    return jsonify(grouped_people)



@stats_bp.route('/get_plan_count', methods=['GET'])
def get_plan_count():
    # Define start and end dates
    start_date, end_date = get_date_range("month", "month")


    # Query inventory data for the specified date range
    start_date = start_date.isoformat()
    end_date = end_date.isoformat()
    

    # Query Firestore for documents within date range
    user_docs = user_plans_collection \
                  .where("start_date", ">=", start_date) \
                  .where("start_date", "<=", end_date) \
                  .stream()

    # Aggregate and count occurrences of each planId
    plan_counts = {}
    for doc in user_docs:
        data = doc.to_dict()
        plan_id = data.get("planId")
        
        if plan_id:
            # Initialize count for each unique planId
            if plan_id not in plan_counts:
                plan_counts[plan_id] = 0
            plan_counts[plan_id] += 1

    # Format result to match the desired output
    result = [{"planId": plan_id, "count": count} for plan_id, count in sorted(plan_counts.items())]

    # Return result or message if no users found
    if not result:
        return jsonify({"message": "No user found for today"}), 404

    return jsonify(result)



    # Define IST timezone
    ist = pytz.timezone('Asia/Kolkata')

    # Get current date-time in IST
    now_ist = datetime.now(ist)

    # Calculate start of the month in IST
    start_of_month_ist = now_ist.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Calculate start of the week containing the start of the month
    start_of_week_ist = start_of_month_ist - timedelta(days=start_of_month_ist.weekday())

    # Calculate end of the month in IST
    if now_ist.month == 12:
        next_month = now_ist.replace(year=now_ist.year + 1, month=1, day=1)
    else:
        next_month = now_ist.replace(month=now_ist.month + 1, day=1)
    end_of_month_ist = next_month - timedelta(seconds=1)

    # Calculate end of the week containing the end of the month
    end_of_week_ist = end_of_month_ist + timedelta(days=(6 - end_of_month_ist.weekday()))
    end_of_week_ist = end_of_week_ist.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Convert IST datetime to UTC for Firestore queries
    start_date_utc = start_of_week_ist.astimezone(pytz.UTC)
    end_date_utc = end_of_week_ist.astimezone(pytz.UTC)

    # Debugging: Uncomment to verify date ranges
    # print("Start Date (UTC):", start_date_utc)
    # print("End Date (UTC):", end_date_utc)

    try:
        # Query Firestore for DailyEntry documents with attendance within the date range
        docs = db.collection('DailyEntry').where('attendance', 'array_contains_any', [
            {'date': {'$gte': start_date_utc, '$lte': end_date_utc}}
        ]).stream()

        # Process each document and aggregate attendance by date
        attendance_by_date = {}
        for doc in docs:
            data = doc.to_dict()
            attendance_list = data.get('attendance', [])

            # Filter attendance entries within the date range
            for entry in attendance_list:
                date = entry.get('date')
                if start_date_utc <= date <= end_date_utc:
                    date_str = date.astimezone(ist).strftime('%Y-%m-%d')
                    attendance_by_date[date_str] = attendance_by_date.get(date_str, 0) + 1

        # Group attendance count by date
        grouped_attendance = [{"date": date, "value": count} for date, count in attendance_by_date.items()]

        if not grouped_attendance:
            return jsonify({"message": "No attendance found for the specified period"}), 404

        return jsonify(grouped_attendance), 200

    except Exception as e:
        # Handle any errors during the process
        return jsonify({"error": str(e)}), 500