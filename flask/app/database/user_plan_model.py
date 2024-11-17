from datetime import datetime, timedelta
import pytz
import moment
from firebase_admin import firestore
from ..database.db_connect import connection

client = connection()
userplans_collection = client.collection("userplans")

class UserPlan:
    def __init__(self, user_id, plan_id, fees, fee_status=False):
        self.userId = user_id
        self.subId = None
        self.planId = plan_id
        self.start_date = None
        self.end_date = None
        self.isavailable = []
        self.remaining_days = None
        self.fees = fees
        self.fee_status = fee_status
        self.created_at = datetime.now(pytz.timezone("Asia/Kolkata"))
        self.updated_at = datetime.now(pytz.timezone("Asia/Kolkata"))

    def save(self):
        try:
            # Check for existing data and calculate subId
            docs = userplans_collection.stream()
            data = [doc.to_dict() for doc in docs]
            self.subId = len(data) + 1  # Auto-increment based on current count

            # Define start_date and end_date
            today_date = moment.now().utcOffset("+05:30").add(1, 'days').startOf('day').toDate()
            self.start_date = today_date
            if self.planId == 501:
                end_date = today_date + timedelta(days=1)
            elif self.planId == 502:
                end_date = today_date + timedelta(days=7)
            elif self.planId == 503:
                end_date = today_date + timedelta(days=30)
            else:
                raise ValueError("Invalid planId")
            self.end_date = end_date

            # Calculate remaining days
            self.remaining_days = (self.end_date - self.start_date).days

            # Populate `isavailable` based on dates range
            dates_range = self.get_dates_in_range(self.start_date, self.end_date)
            for date in dates_range:
                available_object = {
                    "date": moment.date(date).utcOffset("+05:30").startOf("day").toDate(),
                    "breakfast": True,
                    "lunch": True,
                    "dinner": True
                }
                self.isavailable.append(available_object)

            # Prepare the data for Firestore
            user_plan_data = self.__dict__
            userplans_collection.add(user_plan_data)
            return user_plan_data

        except Exception as e:
            return {'error': str(e)}

    def get_dates_in_range(self, start, end):
        date_list = []
        current_date = start
        while current_date <= end:
            date_list.append(current_date)
            current_date += timedelta(days=1)
        return date_list

   