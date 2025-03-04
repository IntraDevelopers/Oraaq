import json
from fastapi import APIRouter, HTTPException, Query
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
from datetime import datetime
from decimal import Decimal

router = APIRouter()

@router.get("/fetchServiceRequests")
def fetch_service_requests_with_bids(customer_id: int = Query(..., description="Customer ID")):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("fetch_service_requests_with_bids", [customer_id])

        # Fetch the results
        service_requests = []
        for result in cursor.stored_results():
            service_requests = result.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not service_requests:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "No service requests found.",
                    "data": []
                }
            )

        # Convert datetime and decimal values
        for request in service_requests:
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
                "message": "Service requests fetched successfully",
                "data": service_requests
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















@router.get("/fetch_combined_requests")
def fetch_all_service_requests(customer_id: int = Query(..., description="Customer ID")):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("fetch_all_service_requests", [customer_id])

        # Fetch the results
        service_requests = []
        for result in cursor.stored_results():
            service_requests = result.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not service_requests:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "No service requests found.",
                    "data": []
                }
            )

        # Convert datetime, decimal values, and JSON arrays
        for request in service_requests:
            for key, value in request.items():
                if isinstance(value, datetime):
                    request[key] = value.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
                elif isinstance(value, Decimal):
                    request[key] = float(value)  # Convert Decimal to float
                elif key == "services" and value:
                    try:
                        request[key] = json.loads(value)  # Convert JSON string to list
                    except json.JSONDecodeError:
                        request[key] = []

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Service requests fetched successfully",
                "data": service_requests
            }
        )

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure
        error_msg = str(err).split(": ", 1)[-1] if ": " in str(err) else str(err)
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )
