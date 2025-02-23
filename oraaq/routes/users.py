# Remove schemas.py import from your route file
# Remove the RegisterUserRequest model

from fastapi import APIRouter, HTTPException
import mysql.connector
import json
from database import get_db_connection
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/register_user/")
def register_user(request: dict):  # Accept raw dict instead of Pydantic model
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.callproc("register_user", [
            request["user_name"],
            request["password"],
            request["phone"],
            request["user_type_id"],
            request["email"]
        ])

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
                "data": json.loads(response["data"]) if "data" in response else {}
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

