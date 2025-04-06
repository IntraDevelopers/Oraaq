from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse
import mysql.connector
from database import get_db_connection  # Ensure you have this function implemented
from routes.auth import validate_token  # Import token validation function
import json
from pydantic import BaseModel

router = APIRouter()

@router.get("/admin_get_customers")
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
        cursor.callproc("admin_get_customers")

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

# ✅ Request Model for Customer Registration
class CustomerCreateRequest(BaseModel):
    profile_image_url: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    pass_word: str | None = None
    phone: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    created_by: str | None = None
    updated_by: str | None = None
    active: str | None = None
    is_otp_verified: str | None = None


# ✅ API Endpoint to Insert a New Customer
@router.post("/admin_insert_customer")
def insert_customer(request: CustomerCreateRequest):
    """
    Inserts a new customer into the database by calling the MySQL stored procedure `admin_insert_customer`.
    Returns a JSON response with success or error messages.
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Call the MySQL Stored Procedure
        cursor.callproc("admin_insert_customer", [
            request.profile_image_url, request.first_name, request.last_name, request.email,
            request.pass_word, request.phone, request.latitude, request.longitude,
            request.created_by, request.updated_by, request.active, request.is_otp_verified
        ])

        # Fetch response from stored procedure
        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

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
    


class AdminUpdateCustomerRequest(BaseModel):
    customer_id: int
    profile_image_url: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email:  str | None = None
    phone:  str | None = None
    latitude: str | None = None
    longitude: str | None = None
    updated_by: str  | None = None
    active:  str | None = None

@router.put("/admin_update_customer")
def update_customer(request: Request, customer: AdminUpdateCustomerRequest):
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.callproc("admin_update_customer", [
            customer.customer_id, customer.profile_image_url, customer.first_name,
            customer.last_name, customer.email, customer.phone, customer.latitude,
            customer.longitude, customer.updated_by, customer.active
        ])

        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if not response or response[0] is None:
            raise HTTPException(status_code=500, detail="Unexpected error occurred while updating customer.")

        parsed_json = json.loads(response[0])
        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        conn.rollback()
        error_msg = str(err).split(": ", 1)[-1]
        return JSONResponse(status_code=400, content={"status": "error", "message": error_msg})
    

@router.delete("/admin_delete_customer")
def delete_customer(request: Request, customer_id: int = Query(...)):
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.callproc("admin_delete_customer", [customer_id])

        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if not response or response[0] is None:
            raise HTTPException(status_code=500, detail="Unexpected error occurred while deleting customer.")

        parsed_json = json.loads(response[0])
        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        conn.rollback()
        error_msg = str(err).split(": ", 1)[-1]
        return JSONResponse(status_code=400, content={"status": "error", "message": error_msg})