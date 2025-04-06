# # import json
# # import mysql.connector
# # from fastapi import APIRouter
# # from database import get_db_connection  # Ensure this function returns a valid MySQL connection
# from pydantic import BaseModel



# # from fastapi import APIRouter, HTTPException
# # import mysql.connector
# # from database import get_db_connection
# # from fastapi.responses import JSONResponse
# # from schemas import AcceptRejectOfferRequest
# import json
# from fastapi import APIRouter, HTTPException, Request
# import mysql.connector[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]
# from database import get_db_connection
# from fastapi.responses import JSONResponse[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]
# from datetime import datetime
# from decimal import Decimal


# # router = APIRouter()

# router = APIRouter()

# # Request body model
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
    


from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, constr
from database import get_db_connection
from fastapi.responses import JSONResponse
import mysql.connector
import json 
from routes.auth import validate_token
from fastapi.responses import JSONResponse

router = APIRouter()

# ✅ Pydantic Model for Request Body
class MerchantProfileUpdate(BaseModel):
    merchant_id: int | None = None
    short_name: str | None = None
    merchant_user_id: int | None = None
    merchant_name: str | None = None
    business_name: str | None = None
    merchant_number: str | None = None
    cnic: str | None = None
    email: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    opening_time: str | None = None
    closing_time: str | None = None
    service_type: int | None = None
    holidays: str | None = None

# ✅ PUT API to Update Merchant Profile
@router.put("/UpdateMerchantProfile")
def update_merchant_profile(req: Request, request: MerchantProfileUpdate):

    # Validate token
    if not validate_token(req):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )


    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the MySQL Stored Procedure
        cursor.callproc("update_merchant_profile", [
            request.merchant_id, request.short_name, request.merchant_user_id,
            request.merchant_name, request.business_name, request.merchant_number,
            request.cnic, request.email, request.latitude, request.longitude,
            request.opening_time, request.closing_time, request.service_type, request.holidays
        ])

        # Fetch response
        result = []
        for res in cursor.stored_results():
            result = res.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not result:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Profile update failed."}
            )

        # Ensure data is properly parsed
        response_data = result[0]
        if isinstance(response_data.get("data"), str):
            response_data["data"] = json.loads(response_data["data"])

        return JSONResponse(
            status_code=200,
            content=response_data
        )
    
    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure
        error_msg = str(err).split(": ", 1)[-1]  # Extract readable message
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )
    








# ✅ Pydantic Model for Request Body with Optional Fields
class MerchantCreateRequest(BaseModel):
    short_title: str | None = None
    description: str | None = None
    active: str | None = None
    is_otp_verified: str | None = None
    merchant_number: str | None = None
    phone: str | None = None
    email: str | None = None
    pass_word: str | None = None
    cnic: str | None = None
    category_id: int | None = None
    opening_time: str | None = None
    closing_time: str | None = None
    created_by: str | None = None
    updated_by: str | None = None
    country: str | None = None
    postal_code: str | None = None
    website: str | None = None
    ntn: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    logo_url: str | None = None
    business_name: str | None = None
    area_id: int | None = None
    holiday_days: str | None = None

# ✅ API to Insert Merchant
@router.post("/admin_insert_merchant2")
def insert_merchant(req: Request, request: MerchantCreateRequest):

    # Validate token
    if not validate_token(req):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the MySQL Stored Procedure
        cursor.callproc("admin_insert_merchant", [
            request.short_title, request.description, request.active,
            request.is_otp_verified, request.merchant_number, request.phone,
            request.email, request.pass_word, request.cnic, request.category_id,
            request.opening_time, request.closing_time, request.created_by,
            request.updated_by, request.country, request.postal_code, request.website,
            request.ntn, request.latitude, request.longitude, request.logo_url,
            request.business_name, request.area_id, request.holiday_days
        ])

        # Fetch response
        response = None
        for res in cursor.stored_results():
            response = res.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        # If response is None, return an unexpected error
        if not response or response[0] is None:
            raise HTTPException(status_code=500, detail="Unexpected error occurred while inserting customer.")

        parsed_json = json.loads(response[0])

        # Parse the JSON response from MySQL
        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        conn.rollback()  # Rollback changes on failure
        error_msg = str(err).split(": ", 1)[-1]  # Extract readable error message

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )