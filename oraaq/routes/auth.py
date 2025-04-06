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
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi.requests import Request


# Secret key for encoding JWT
SECRET_KEY = "Oraaq_DB"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to create a JWT token
def create_access_token():
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Route to generate a token
@router.post("/token")
def get_token():
    token = create_access_token()
    return {"access": token}



# # Function to validate token
# def validate_token(request: Request):
#     auth_header = request.headers.get("Authorization")
#     if not auth_header or not auth_header.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Invalid Access Token")

#     token = auth_header.split("Bearer ")[1]
#     try:
#         jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Invalid Access Token")
#     except jwt.PyJWTError:

#         raise HTTPException(status_code=401, detail="Invalid Access Token")
    

def validate_token(request: Request) -> bool:
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return False  # Invalid token

    token = auth_header.split("Bearer ")[1]
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True  # Valid token
    except (jwt.ExpiredSignatureError, jwt.PyJWTError):
        return False  # Invalid token


@router.post("/splogin")
def login(req: Request, request: LoginRequest):

    # Validate token
    if not validate_token(req):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("validate_login", [request.email, request.password, request.role])

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

            token = create_access_token()
            parsed_data["token"] = token 

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
    request: Request,
    email: str = Query(..., description="User's registered email"),
    otp_value: int = Query(..., description="OTP code to verify")
):
    
    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
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
def change_password(request: Request,
                    data: ChangePasswordRequest):

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

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

        # Assuming result[0] contains the JSON string from the stored procedure
        try:
            response = json.loads(result[0])  # Parse the JSON response
        except json.JSONDecodeError:
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Invalid response format from stored procedure"}
            )

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
def set_new_password(request: Request, data: SetNewPasswordRequest):

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
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
    



class LoginRequest(BaseModel):
    username: str | None = None
    password: str | None = None

@router.post("/admin_login_user")
def login_user(request: Request, credentials: LoginRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.callproc("admin_login_user", [credentials.username, credentials.password])

        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        cursor.close()
        conn.close()

        if not response or response[0] is None:
            raise HTTPException(status_code=500, detail="Unexpected error occurred during login.")

        parsed_json = json.loads(response[0])
        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        error_msg = str(err).split(": ", 1)[-1]
        return JSONResponse(status_code=400, content={"status": "error", "message": error_msg})