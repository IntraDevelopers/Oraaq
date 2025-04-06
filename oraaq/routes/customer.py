import json
import mysql.connector
from fastapi import APIRouter, Request
from database import get_db_connection  # Ensure this function returns a valid MySQL connection
from pydantic import BaseModel
from routes.auth import validate_token  # Import token validation function
from fastapi.responses import JSONResponse


router = APIRouter()

class UpdateCustomerProfileRequest(BaseModel):
    customer_id: int
    customer_name: str
    email: str
    phone: str
    longitude: float
    latitude: float

@router.put("/updateCustomer")
def update_customer_profile(request: Request, data: UpdateCustomerProfileRequest):

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
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
            data.latitude
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

    # except mysql.connector.Error as err:
    #     error_msg = str(err)
    #     print("MySQL Error:", error_msg)  # Debugging log

    #     if '45000' in error_msg:
    #         try:
    #             json_part = error_msg[error_msg.find('{') : error_msg.rfind('}') + 1]
    #             parsed_error = json.loads(json_part)
    #             return parsed_error
    #         except Exception as e:
    #             print("JSON Parsing Error:", str(e))  # Debugging log
    #             return {"status": "error", "message": "An unexpected error occurred"}

    #     return {"status": "error", "message": "Database error: " + str(err)}
    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure
        error_msg = str(err).split(": ", 1)[-1]  # Extract readable message
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )


# Request body model
# class UpdateMerchantProfileRequest(BaseModel):
#     merchant_id: int
#     merchant_name: str
#     merchant_number: str
#     cnic: str
#     email: str
#     business_name: str
#     latitude: float
#     longitude: float
#     opening_time: str
#     closing_time: str
#     service_type: int
#     holidays: str


# @router.put("/UpdateMerchantProfile")
# def update_merchant_profile(data: UpdateMerchantProfileRequest):
#     try:
#         print("Merchant API")
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         # Call stored procedure
#         cursor.callproc('UpdateMerchantProfile', [
#             data.merchant_id,
#             data.merchant_name,
#             data.merchant_number,
#             data.cnic,
#             data.email,
#             data.business_name,
#             data.latitude,
#             data.longitude,
#             data.opening_time,
#             data.closing_time,
#             data.service_type,
#             data.holidays
#         ])

#         # Fetch the result
#         result = None
#         for res in cursor.stored_results():
#             result = res.fetchone()  # Get the first row
        
#         cursor.close()
#         conn.close()

#         if not result:
#             return {"status": "error", "message": "Error: No response from stored procedure"}

#         # Convert MySQL response tuple to dictionary
#         response = {
#             "status": result[0],  # "success" or "error"
#             "message": result[1],  # Message text
#             "data": json.loads(result[2])  # JSON data containing updated profile
#         }

#         return response

#     except mysql.connector.Error as err:
#         error_msg = str(err)
#         print("MySQL Error:", error_msg)  # Debugging log

#         if '45000' in error_msg:
#             try:
#                 # Extract JSON part from the error message
#                 json_part = error_msg[error_msg.find('{') : error_msg.rfind('}') + 1]

#                 # Parse the extracted JSON error message
#                 parsed_error = json.loads(json_part)

#                 return parsed_error
#             except Exception as e:
#                 print("JSON Parsing Error:", str(e))  # Debugging log
#                 return {"status": "error", "message": "An unexpected error occurred"}

#         return {"status": "error", "message": "Database error: " + str(err)}
    