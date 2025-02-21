from fastapi import APIRouter, HTTPException
from schemas import RegisterUserRequest
import mysql.connector
import json
from database import get_db_connection

router = APIRouter()

@router.post("/register_user/")
def register_user(request: RegisterUserRequest):
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
                "data": json.loads(response["data"]) if "data" in response else {}
            }
        else:
            raise HTTPException(status_code=500, detail="Unexpected error during registration.")

    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail={"status": "error", "message": str(err)})
