import json
from fastapi import APIRouter, HTTPException, Request
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
import json
from fastapi import APIRouter, Query
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
import json
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
import json
from decimal import Decimal  # Import Decimal module
from routes.auth import validate_token
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/GetInProgressWorkOrdersForMerchant")
def get_in_progress_work_orders(request: Request):

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    try:
        merchant_id = request.query_params.get("merchant_id")  # Get merchant_id from query params

        if not merchant_id:
            merchant_id = None  # Pass NULL to the stored procedure

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("GetInProgressWorkOrdersForMerchant", [merchant_id])

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
                    "message": "No in-progress work orders found for the merchant.",
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
                "message": "In-progress work orders fetched successfully",
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





# router = APIRouter()


# router = APIRouter()

def convert_decimal_to_float(data):
    """
    Recursively converts all Decimal values in a dictionary or list to float.
    """
    if isinstance(data, list):
        return [convert_decimal_to_float(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_decimal_to_float(value) for key, value in data.items()}
    elif isinstance(data, Decimal):
        return float(data)  # Convert Decimal to float
    return data

@router.get("/merchantWorkorders")
def get_work_orders(request: Request, 
                    merchant_id: int = Query(..., description="Merchant ID"),
                    order_status_id: int = Query(..., description="Order Status ID")):
    
    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    """
    Fetch work orders for a merchant based on the order status.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("get_work_orders", [merchant_id, order_status_id])

        # Fetch response from the procedure
        result = []
        for res in cursor.stored_results():
            result = res.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not result:
            return JSONResponse(
                status_code=200,
                content={"status": "success", "message": "No work orders found.", "data": []}
            )

        # Convert Decimal values to float
        result = convert_decimal_to_float(result)

        # Convert service_names from string to actual JSON array
        for item in result:
            if "service_names" in item and isinstance(item["service_names"], str):
                try:
                    item["service_names"] = json.loads(item["service_names"])
                except json.JSONDecodeError:
                    item["service_names"] = []

        # Format response
        formatted_response = {
            "status": "success",
            "message": "Work orders retrieved successfully.",
            "data": result
        }

        return JSONResponse(
            status_code=200,
            content=formatted_response
        )

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure

        error_msg = str(err)
        if ": " in error_msg:
            error_msg = error_msg.split(": ", 1)[-1]  # Extract readable message

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg, "data": []},
        )




# router = APIRouter()

def convert_decimal_to_float(data):
    """ Recursively converts all Decimal values to float. """
    if isinstance(data, list):
        return [convert_decimal_to_float(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_decimal_to_float(value) for key, value in data.items()}
    elif isinstance(data, Decimal):
        return float(data)
    return data

@router.get("/customerWorkOrders")
def get_work_orders_customer(request: Request,
                             customer_id: int = Query(..., description="Customer ID"),
                             order_status_id: int = Query(..., description="Order Status ID")):
    

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    """
    Fetch work orders for a customer based on the order status.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("get_work_orders2", [customer_id, order_status_id])

        # Fetch response from the procedure
        result = []
        for res in cursor.stored_results():
            result = res.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        # Handle empty response
        if not result:
            return JSONResponse(
                status_code=200,
                content={"status": "success", "message": "No work orders found.", "data": []}
            )

        # Convert Decimal values to float
        result = convert_decimal_to_float(result)

        # Convert service_names from string to actual JSON array
        for item in result:
            if "service_names" in item and isinstance(item["service_names"], str):
                try:
                    item["service_names"] = json.loads(item["service_names"])
                except json.JSONDecodeError:
                    item["service_names"] = []

        # Format response
        formatted_response = {
            "status": "success",
            "message": "Work orders retrieved successfully.",
            "data": result
        }

        return JSONResponse(
            status_code=200,
            content=formatted_response
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
