import json
from fastapi import APIRouter, HTTPException, Request
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
from datetime import datetime
from decimal import Decimal

router = APIRouter()

@router.get("/get_applied_merchant_work_order")
def get_applied_merchant_work_order(request: Request):
    try:
        merchant_id = request.query_params.get("merchant_id")  # Get merchant_id as a string

        if not merchant_id:  
            merchant_id = None  # Pass NULL to the stored procedure

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("get_applied_merchant_work_order", [merchant_id])

        # Fetch the results
        work_orders = []
        for result in cursor.stored_results():
            work_orders = result.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not work_orders:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "No applied work orders found.",
                    "data": []
                }
            )

        # Convert datetime and decimal values
        for order in work_orders:
            for key, value in order.items():
                if isinstance(value, datetime):
                    order[key] = value.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
                elif isinstance(value, Decimal):
                    order[key] = float(value)  # Convert Decimal to float
                elif key == "service_names" and value:
                    order[key] = json.loads(value)  # Convert JSON string to list

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Applied work orders fetched successfully",
                "data": work_orders
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
