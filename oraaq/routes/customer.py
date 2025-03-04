import json
import mysql.connector
from fastapi import APIRouter
from database import get_db_connection  # Ensure this function returns a valid MySQL connection
from pydantic import BaseModel

router = APIRouter()

class UpdateCustomerProfileRequest(BaseModel):
    customer_id: int
    customer_name: str
    email: str
    phone: str
    longitude: float
    latitude: float
    is_otp_verified: str

@router.put("/updateCustomer")
def update_customer_profile(data: UpdateCustomerProfileRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Call stored procedure
        cursor.callproc('UpdateCustomerProfile', [
            data.customer_id,
            data.customer_name,
            data.email,
            data.phone,
            data.longitude,
            data.latitude,
            data.is_otp_verified
        ])

        # Fetch the result
        result = None
        for res in cursor.stored_results():
            result = res.fetchone()  # Get the first row
            print("Stored Procedure Result:", result)  # Debugging

        cursor.close()
        conn.close()

        if not result:
            return {"status": "error", "message": "Error: No response from stored procedure"}

        # Convert MySQL response tuple to dictionary
        response = {
            "status": result[0],  # "success" or "error"
            "message": result[1],  # Message text
            "data": json.loads(result[2]) if result[2] else None  # JSON data
        }

        return response

    except mysql.connector.Error as err:
        error_msg = str(err)
        print("MySQL Error:", error_msg)  # Debugging log

        if '45000' in error_msg:
            try:
                json_part = error_msg[error_msg.find('{') : error_msg.rfind('}') + 1]
                parsed_error = json.loads(json_part)
                return parsed_error
            except Exception as e:
                print("JSON Parsing Error:", str(e))  # Debugging log
                return {"status": "error", "message": "An unexpected error occurred"}

        return {"status": "error", "message": "Database error: " + str(err)}
