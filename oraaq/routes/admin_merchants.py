from fastapi import APIRouter, HTTPException, Request, Query

from fastapi.responses import JSONResponse
import mysql.connector
from database import get_db_connection  # Ensure you have this function implemented
from routes.auth import validate_token  # Import token validation function
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# from fastapi.responses import JSONResponse
import pymysql
# import json
# from database import get_db_connection  # Ensure you have a DB connection function
from typing import Optional

router = APIRouter()

@router.get("/admin_get_merchants")
def get_app_users(request: Request):
    """
    Fetches all app users by calling the MySQL stored procedure 'admin_get_app_users'.
    Returns a JSON response.
    """
        
                # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    try:
        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Call stored procedure
        cursor.callproc("admin_get_merchants")

        # Fetch result
        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        # Close cursor and connection
        cursor.close()
        conn.close()

        # If response is empty, return an error
        if not response:
            raise HTTPException(status_code=404, detail="No users found.")

        # MySQL returns JSON as a string, so we parse it
        parsed_json = json.loads(response[0])

        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(err)}
        )






# ✅ Request Model for Merchant Registration
class MerchantCreateRequest(BaseModel):
    short_title: str | None = None  # Allow NULL (MySQL will validate)
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
    holiday_days: str | None = None  # Comma-separated (e.g., 'FRI,SAT')

# ✅ API Endpoint to Insert a New Merchant
@router.post("/admin_insert_merchant")
def insert_merchant(request: MerchantCreateRequest):
    print("This one is called")
    """
    Inserts a new merchant into the database by calling the MySQL stored procedure `admin_insert_merchant`.
    Returns a JSON response with success or error messages.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ Call the MySQL Stored Procedure
        cursor.callproc("admin_insert_merchant", [
            request.short_title, request.description, request.active, request.is_otp_verified,
            request.merchant_number, request.phone, request.email, request.pass_word,
            request.cnic, request.category_id, request.opening_time, request.closing_time,
            request.created_by, request.updated_by, request.country, request.postal_code,
            request.website, request.ntn, request.latitude, request.longitude,
            request.logo_url, request.business_name, request.area_id, request.holiday_days
        ])

        # ✅ Fetch response from stored procedure
        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()


        # If response is None, return an unexpected error
        if not response or response[0] is None:
            raise HTTPException(status_code=500, detail="Unexpected error occurred while inserting merchant.")

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
    
class AdminUpdateMerchantRequest(BaseModel):
    merchant_id: int
    short_title: str | None = None
    description: str | None = None
    active: str | None = None
    merchant_number: str | None = None
    phone: str | None = None
    email: str | None = None
    cnic: str | None = None
    category_id: int | None = None
    opening_time: str | None = None
    closing_time: str | None = None
    updated_by: str  | None = None
    country: str | None = None
    postal_code: str | None = None
    website: str | None = None
    ntn: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    logo_url: str | None = None
    business_name: str | None = None
    area_id: int | None = None
    holiday_days: str | None = None

@router.put("/admin_update_merchant")
def update_merchant(request: Request, merchant: AdminUpdateMerchantRequest):
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.callproc("admin_update_merchant", [
            merchant.merchant_id, merchant.short_title, merchant.description,
            merchant.active, merchant.merchant_number, merchant.phone,
            merchant.email, merchant.cnic, merchant.category_id,
            merchant.opening_time, merchant.closing_time, merchant.updated_by,
            merchant.country, merchant.postal_code, merchant.website,
            merchant.ntn, merchant.latitude, merchant.longitude,
            merchant.logo_url, merchant.business_name, merchant.area_id,
            merchant.holiday_days
        ])

        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if not response or response[0] is None:
            raise HTTPException(status_code=500, detail="Unexpected error occurred while updating merchant.")

        parsed_json = json.loads(response[0])
        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        conn.rollback()
        error_msg = str(err).split(": ", 1)[-1]
        return JSONResponse(status_code=400, content={"status": "error", "message": error_msg})
    

@router.delete("/admin_delete_merchant")
def delete_merchant(request: Request, merchant_id: int = Query(...)):
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.callproc("admin_delete_merchant", [merchant_id])

        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if not response or response[0] is None:
            raise HTTPException(status_code=500, detail="Unexpected error occurred while deleting merchant.")

        parsed_json = json.loads(response[0])
        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        conn.rollback()
        error_msg = str(err).split(": ", 1)[-1]
        return JSONResponse(status_code=400, content={"status": "error", "message": error_msg})