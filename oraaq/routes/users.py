from fastapi import APIRouter, HTTPException, Request, Query
from schemas import RegisterUserRequest
import mysql.connector
import json
from database import get_db_connection
from fastapi.responses import JSONResponse
from decimal import Decimal
# from fastapi import APIRouter, HTTPException, Query
# import mysql.connector
# from database import get_db_connection
# from fastapi.responses import JSONResponse
from routes.auth import validate_token
# from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/register")
def register_user(req: Request, request: RegisterUserRequest):

    # Validate token
    if not validate_token(req):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    """Registers a new user directly inside the route file."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.callproc("register_user", [
            request.user_name,
            request.password,
            request.phone,
            request.user_type_id,
            request.email
        ])

        # Fetch stored procedure results
        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if response:
            return {
                "status": "success",
                "message": "Registration successful.",
                "data": {"user": json.loads(response["json_response"]) if "json_response" in response else {}}
            }
        else:
            raise HTTPException(status_code=500, detail="Unexpected error during registration.")

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure
    
        # Extract error message without MySQL error codes
        error_msg = str(err)
        if ": " in error_msg:
            error_msg = error_msg.split(": ", 1)[-1]  # Keep only the message part

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )






@router.get("/GenerateOtp")
def generate_otp(request: Request, user_id: int = Query(..., description="User ID for OTP generation")):

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    """
    Generate an OTP for a given user ID.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("generate_otp", [user_id])

        # Fetch response from the procedure
        result = []
        for res in cursor.stored_results():
            result = res.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not result:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Unexpected error occurred."}
            )

        # Extract response data
        response_data = result[0]
        otp_value = None

        if "data" in response_data and isinstance(response_data["data"], str):
            parsed_data = json.loads(response_data["data"])
            otp_value = parsed_data.get("otp")

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "OTP Generated successfully",
                "OTP": otp_value
            }
        )

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure
        error_msg = str(err).split(": ", 1)[-1]  # Extract readable message

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )




@router.get("/getMerchantWithinRadius2")
def get_merchants_within_radius(
    request: Request,
    latitude: float = Query(..., description="Latitude of the location"),
    longitude: float = Query(..., description="Longitude of the location"),
    radius: float = Query(..., description="Search radius in kilometers"),
    category_id: int = Query(..., description="Category ID of the service")
):

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    """
    Fetch merchants within the given radius for a specified category.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("get_merchants_within_radius_2", [latitude, longitude, radius, category_id])

        # Fetch the results
        merchants = []
        for result in cursor.stored_results():
            merchants = result.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not merchants:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "No merchants found within the given radius.", "data": []}
            )

        # ✅ Convert all Decimal values to float to ensure JSON serialization
        for merchant in merchants:
            for key, value in merchant.items():
                if isinstance(value, Decimal):
                    merchant[key] = float(value)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Merchants retrieved successfully.",
                "data": merchants
            }
        )

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure
        error_msg = str(err).split(": ", 1)[-1] if ": " in str(err) else str(err)

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg, "data": []}
        )