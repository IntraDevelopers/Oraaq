import json
from fastapi import APIRouter, HTTPException, Query
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
from schemas import LoginRequest, SocialLoginRequest, ChangePasswordRequest
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
import json


router = APIRouter()

@router.post("/login")
def login(request: LoginRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("validate_login", [request.email, request.password, request.user_type_id])

        # Fetch the results
        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if response:
            # Parse the JSON string inside "data" before returning the response
            parsed_data = json.loads(response["data"]) if "data" in response and response["data"] else {}

            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Login successful",
                    "data": parsed_data
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Unexpected error during login.")

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure

        error_msg = str(err)
        if ": " in error_msg:
            error_msg = error_msg.split(": ", 1)[-1]  # Extract readable message

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )








# router = APIRouter()

# Pydantic Model for Request Body


@router.post("/SocialRegisterLogin")
def social_register_or_login(request: SocialLoginRequest):
    """
    Social Login/Register API for Oraaq Marketplace.
    - If the user doesn't exist, it registers them.
    - If the user exists, it logs them in.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("social_register_or_login", [
            request.user_name,
            request.email,
            request.social_id,
            request.phone,
            request.provider,
            request.role
        ])

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

        # Convert response from MySQL JSON string to dictionary
        response_data = result[0]
        if "data" in response_data and isinstance(response_data["data"], str):
            response_data["data"] = json.loads(response_data["data"])  # Convert string JSON to dict

        return JSONResponse(
            status_code=200,
            content=response_data
        )

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure

        error_msg = str(err)
        if ": " in error_msg:
            error_msg = error_msg.split(": ", 1)[-1]  # Extract readable message

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )




@router.get("/verifyOTP")
def verify_otp(
    email: str = Query(..., description="User's registered email"),
    otp_value: int = Query(..., description="OTP code to verify")
):
    """
    Verify an OTP for the given email.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("verify_otp", [email, otp_value])

        # Fetch response
        result = []
        for res in cursor.stored_results():
            result = res.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        # If no result, return error
        if not result:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Invalid OTP or email!"}
            )

        # Return success response
        return JSONResponse(
            status_code=200,
            content=result[0]
        )

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure
        error_msg = str(err)
        if ": " in error_msg:
            error_msg = error_msg.split(": ", 1)[-1]  # Extract readable message

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )







from fastapi import HTTPException
from fastapi.responses import JSONResponse

class ChangePasswordRequest(BaseModel):
    user_id: int
    current_password: str
    new_password: str

@router.put("/changePassword")
def change_password(data: ChangePasswordRequest):
    user_id = data.user_id
    current_password = data.current_password
    new_password = data.new_password

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Call stored procedure
        cursor.callproc('ChangePassword', [user_id, current_password, new_password])

        # Fetch the result
        result = None
        for res in cursor.stored_results():
            result = res.fetchone()  # Get the first row
        
        cursor.close()
        conn.close()

        if not result:
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Error: No response from stored procedure"}
            )

        # Convert MySQL response tuple to dictionary
        response = {
            "status": result[0],  # "success" or "error"
            "message": result[1]  # Message text
        }

        # Set HTTP status code based on response status
        status_code = 200 if response["status"] == "success" else 400

        return JSONResponse(
            status_code=status_code,
            content=response
        )

    except mysql.connector.Error as err:
        error_msg = str(err)
        print("MySQL Error:", error_msg)  # Debugging log

        if '45000' in error_msg:
            try:
                # Extract JSON part from the error message
                json_part = error_msg[error_msg.find('{') : error_msg.rfind('}') + 1]

                # Parse the extracted JSON error message
                parsed_error = json.loads(json_part)

                return JSONResponse(
                    status_code=400,
                    content=parsed_error
                )
            except Exception as e:
                print("JSON Parsing Error:", str(e))  # Debugging log
                return JSONResponse(
                    status_code=400,
                    content={"status": "error", "message": "An unexpected error occurred"}
                )

        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Database error: " + str(err)}
        )








class SetNewPasswordRequest(BaseModel):
    email: str
    new_password: str

@router.put("/setNewPassword")
def set_new_password(data: SetNewPasswordRequest):
    """
    Update the user's password securely.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("set_new_password", [data.email, data.new_password])

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

        return JSONResponse(
            status_code=200,
            content=result[0]  # Return the success response from the stored procedure
        )

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure
        error_msg = str(err)

        if ": " in error_msg:
            error_msg = error_msg.split(": ", 1)[-1]  # Extract readable message

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )