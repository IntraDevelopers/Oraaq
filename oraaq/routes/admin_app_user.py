from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse
import mysql.connector
from database import get_db_connection  # Ensure you have this function implemented
from routes.auth import validate_token  # Import token validation function
import json
from pydantic import BaseModel

router = APIRouter()

@router.get("/admin_get_app_users")
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
        cursor.callproc("admin_get_app_users")

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



from fastapi import Request, HTTPException
from pydantic import BaseModel

# ✅ Request Model for User Registration
class UserCreateRequest(BaseModel):
    user_name: str = None
    pass_word: str = None
    email: str = None
    phone: str = None
    user_type_id: int = None
    created_by: str = None
    updated_by: str = None
    active: str = None
    sequence_no: int = None
    is_super_user: str = None
    is_otp_allowed: str = None
    current_otp: int = None
    last_login_datetime: str = None
    user_source_id: int = None
    is_otp_verified: str = None
    is_social: str = None




# ✅ API Endpoint to Insert a New User
@router.post("/admin_insert_app_user")
def insert_user(req: Request, user_create_request: UserCreateRequest):
    """
    Inserts a new user into the database by calling the MySQL stored procedure `admin_insert_app_user`.
    Returns a JSON response with success or error messages.
    """

    # Validate token using the correct 'req' (Request) object
    if not validate_token(req):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Call the MySQL Stored Procedure
        cursor.callproc("admin_insert_app_user", [
            user_create_request.user_name, user_create_request.pass_word, user_create_request.active, user_create_request.sequence_no,
            user_create_request.created_by, user_create_request.updated_by, user_create_request.user_type_id, user_create_request.is_super_user,
            user_create_request.is_otp_allowed, user_create_request.current_otp, user_create_request.last_login_datetime,
            user_create_request.user_source_id, user_create_request.email, user_create_request.phone, user_create_request.is_otp_verified, user_create_request.is_social
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
            raise HTTPException(status_code=500, detail="Unexpected error occurred while inserting user.")

        # Parse the JSON response from MySQL
        parsed_json = json.loads(response[0])

        return JSONResponse(parsed_json)

    except mysql.connector.Error as err:
        conn.rollback()  # Rollback changes on failure
        error_msg = str(err).split(": ", 1)[-1]  # Extract readable error message

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )
    



from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import mysql.connector
import json

# router = APIRouter()

class AppUserUpdateRequest(BaseModel):
    app_user_id: int
    user_name: str | None = None
    pass_word: str | None = None
    active: str | None = None
    sequence_no: int | None = None
    updated_by: str | None = None
    user_type_id: int | None = None
    is_super_user: str | None = None
    is_otp_allowed: str | None = None
    current_otp: int | None = None
    last_login_datetime: str | None = None
    user_source_id: int | None = None
    email: str | None = None
    phone: str | None = None
    is_otp_verified: str | None = None
    is_social: str | None = None

@router.put("/admin_update_app_user")
def update_app_user(request: Request, user: AppUserUpdateRequest):
    # Validate token using the correct 'req' (Request) object
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.callproc("admin_update_app_user", [
            user.app_user_id, user.user_name, user.pass_word, user.active,
            user.sequence_no, user.updated_by, user.user_type_id, user.is_super_user,
            user.is_otp_allowed, user.current_otp, user.last_login_datetime,
            user.user_source_id, user.email, user.phone, user.is_otp_verified,
            user.is_social
        ])

        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if not response or response[0] is None:
            raise HTTPException(status_code=500, detail="Unexpected error occurred while updating app user.")

        parsed_json = json.loads(response[0])
        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        conn.rollback()
        error_msg = str(err).split(": ", 1)[-1]
        return JSONResponse(status_code=400, content={"status": "error", "message": error_msg})




@router.delete("/admin_delete_app_user")
def delete_app_user(request: Request, app_user_id: int = Query(...)):
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.callproc("admin_delete_app_user", [app_user_id])

        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if not response or response[0] is None:
            raise HTTPException(status_code=500, detail="Unexpected error occurred while deleting app user.")

        parsed_json = json.loads(response[0])
        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        conn.rollback()
        error_msg = str(err).split(": ", 1)[-1]
        return JSONResponse(status_code=400, content={"status": "error", "message": error_msg})