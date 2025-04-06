import json
from fastapi import APIRouter, HTTPException, Request
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
from datetime import datetime
from decimal import Decimal
from routes.auth import validate_token


router = APIRouter()

@router.get("/GetAllNewRequestForMerchant")
def get_all_new_requests_for_merchant(request: Request):

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    try:
        merchant_id = request.query_params.get("merchant_id")  # Get merchant_id as a string

        if not merchant_id:
            merchant_id = None  # Pass NULL to the stored procedure

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("GetAllNewRequestForMerchant", [merchant_id])

        # Fetch the results
        merchant_requests = []
        for result in cursor.stored_results():
            merchant_requests = result.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not merchant_requests:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "No new requests found for the merchant.",
                    "data": []
                }
            )

        # Convert datetime and decimal values
        for request in merchant_requests:
            for key, value in request.items():
                if isinstance(value, datetime):
                    request[key] = value.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
                elif isinstance(value, Decimal):
                    request[key] = int(value) if value == int(value) else float(value)
                elif key == "service_names" and value:
                    request[key] = json.loads(value)  # Convert JSON string to list

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Requests fetched successfully",
                "data": merchant_requests
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
