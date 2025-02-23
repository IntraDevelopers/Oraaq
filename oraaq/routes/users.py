from fastapi import APIRouter, HTTPException
from schemas import RegisterUserRequest
import mysql.connector
import json
from database import get_db_connection
import jwt
import datetime
#pip install PyJWT
import jwt  # Correct import
from jwt import encode  # Ensures the function exists


# Secret key for JWT encoding and decoding
SECRET_KEY = "123"


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
        error_msg = str(err)
        print("MySQL Error:", error_msg)  # Debugging log

        if '45000' in error_msg:
            try:
                # Extracting the actual error message from MySQL error response
                error_message = error_msg.split(': ')[1].strip()  # Get text after "45000: "
                return {"status": "error", "message": error_message}
            except Exception as e:
                print("Parsing Error:", str(e))  # Debugging log
                return {"status": "error", "message": "An unexpected error occurred"}

        return {"status": "error", "message": "Database error: " + str(err)}

        


def generate_token(user_id: int, role: int):
    """Generate JWT token."""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Token expires in 2 hours
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

@router.post("/login")
def login(data: dict):
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Call the stored procedure
        cursor.callproc('LoginUser', [email, password, role])

        # Fetch the result
        for result in cursor.stored_results():
            data = result.fetchall()

        cursor.close()
        conn.close()

        if not data:
            return {"status": "error", "message": "Invalid email or password"}

        # Extract user details
        user_id = data[0][2]
        user_role = data[0][3]

        # Generate JWT token
        token = generate_token(user_id, user_role)

        return {
            "status": "success",
            "message": "Login successful",
            "user_id": user_id,
            "role": user_role,
            "token": token
        }

    except mysql.connector.Error as err:
        error_msg = str(err)
        print("MySQL Error:", error_msg)  # Debugging log

        if '45000' in error_msg:
            try:
                # Extract JSON part from the error message
                json_part = error_msg[error_msg.find('{') : error_msg.rfind('}') + 1]
                
                # Parse the extracted JSON error message
                parsed_error = json.loads(json_part)

                return parsed_error
            except Exception as e:
                print("JSON Parsing Error:", str(e))  # Debugging log
                return {"status": "error", "message": "An unexpected error occurred"}

        return {"status": "error", "message": "Database error: " + str(err)}
