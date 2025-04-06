import json
from fastapi import APIRouter, HTTPException, Query, Request
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
from datetime import datetime
from decimal import Decimal
from routes.auth import validate_token

# import json
# from fastapi import APIRouter, HTTPException, Request
# import mysql.connector
# from database import get_db_connection
# from fastapi.responses import JSONResponse
# from datetime import datetime
# from decimal import Decimal


router = APIRouter()

@router.get("/getAllNewRequests")
def get_all_new_requests(request: Request, merchant_id: int = Query(..., description="Merchant ID")):
    
    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("get_all_new_requests", [merchant_id])

        # Fetch the results
        new_requests = []
        for result in cursor.stored_results():
            new_requests = result.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not new_requests:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "No new service requests found.",
                    "data": []
                }
            )

        # Convert datetime and decimal values
        for request in new_requests:
            for key, value in request.items():
                if isinstance(value, datetime):
                    request[key] = value.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
                elif isinstance(value, Decimal):
                    request[key] = float(value)  # Convert Decimal to float
                elif key == "service_names" and value:
                    request[key] = json.loads(value)  # Convert JSON string to list

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "New service requests fetched successfully",
                "data": new_requests
            }
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






# router = APIRouter()

@router.get("/fetchAcceptedRequest")
def get_accepted_requests(request: Request):

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    try:
        customer_id = request.query_params.get("customer_id")  # Get customer_id from query params

        if not customer_id:
            customer_id = None  # Pass NULL to the stored procedure

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("get_accepted_request", [customer_id])

        # Fetch the results
        accepted_requests = []
        for result in cursor.stored_results():
            accepted_requests = result.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not accepted_requests:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "No accepted requests found for the customer.",
                    "data": []
                }
            )

        # Convert datetime and decimal values
        for request in accepted_requests:
            for key, value in request.items():
                if isinstance(value, datetime):
                    request[key] = value.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
                elif isinstance(value, Decimal):
                    request[key] = float(value)  # Convert Decimal to float
                elif key == "services" and value:
                    request[key] = json.loads(value)  # Convert JSON string to list

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Accepted requests fetched successfully",
                "data": accepted_requests
            }
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
