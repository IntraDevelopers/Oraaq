from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse
import mysql.connector
from database import get_db_connection  # Ensure you have this function implemented
from routes.auth import validate_token  # Import token validation function
import json

router = APIRouter()

# @router.get("/admin_get_orders")
# def get_app_users(request: Request):
#     """
#     Fetches all app users by calling the MySQL stored procedure 'admin_get_app_users'.
#     Returns a JSON response.
#     """
        
#                 # Validate token
#     if not validate_token(request):
#         return JSONResponse(
#             status_code=401,
#             content={"status": "error", "message": "Invalid Access Token"}
#         )
#     try:
#         # Establish database connection
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         # Call stored procedure
#         cursor.callproc("admin_get_orders")

#         # Fetch result
#         response = None
#         for result in cursor.stored_results():
#             response = result.fetchone()

#         # Close cursor and connection
#         cursor.close()
#         conn.close()

#         # If response is empty, return an error
#         if not response:
#             raise HTTPException(status_code=404, detail="No users found.")

#         # MySQL returns JSON as a string, so we parse it
#         parsed_json = json.loads(response[0])

#         return JSONResponse(content=parsed_json)

#     except mysql.connector.Error as err:
#         return JSONResponse(
#             status_code=500,
#             content={"status": "error", "message": str(err)}
#         )


@router.get("/admin_get_orders")
def get_orders(request: Request):
    """
    Fetches all orders by calling the MySQL stored procedure 'admin_get_orders'.
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
        cursor.callproc("admin_get_orders")

        # Fetch result
        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        # Close cursor and connection
        cursor.close()
        conn.close()

        # If response is empty, return an error
        if not response:
            raise HTTPException(status_code=404, detail="No orders found.")

        # MySQL returns JSON as a string, so we parse it
        parsed_json = json.loads(response[0])

        # Fix: Check if `selected_services` and `selected_service_ids` are strings that look like JSON arrays
        for order in parsed_json['data']['orders']:
            # Parse `selected_services` if it's a stringified JSON array
            if isinstance(order['selected_services'], str):
                try:
                    order['selected_services'] = json.loads(order['selected_services'])
                except json.JSONDecodeError:
                    order['selected_services'] = []  # In case of error, set it to an empty list

            # Parse `selected_service_ids` if it's a stringified JSON array
            if isinstance(order['selected_service_ids'], str):
                try:
                    order['selected_service_ids'] = json.loads(order['selected_service_ids'])
                except json.JSONDecodeError:
                    order['selected_service_ids'] = []  # In case of error, set it to an empty list

        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(err)}
        )
    



from pydantic import BaseModel

class AdminUpdateOrderRequest(BaseModel):
    order_id: int
    order_status_id: int | None = None
    total_amount: float | None = None
    order_amount: float | None = None
    category_id: int | None = None
    order_required_date: str | None = None  # Must be in "YYYY-MM-DD HH:MM:SS"
    radius: float | None = None
    updated_by: str  | None = None
    selected_services: str | None = None  # Comma-separated service IDs
    active: str | None = None

@router.put("/admin_update_order")
def update_order(request: Request, order: AdminUpdateOrderRequest):
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.callproc("admin_update_order", [
            order.order_id, order.order_status_id, order.total_amount,
            order.order_amount, order.category_id, order.order_required_date,
            order.radius, order.updated_by, order.selected_services, order.active
        ])

        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if not response or response[0] is None:
            raise HTTPException(status_code=500, detail="Unexpected error occurred while updating order.")

        parsed_json = json.loads(response[0])
        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        conn.rollback()
        error_msg = str(err).split(": ", 1)[-1]
        return JSONResponse(status_code=400, content={"status": "error", "message": error_msg})
    
@router.delete("/admin_delete_order")
def delete_order(request: Request, order_id: int = Query(...)):
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.callproc("admin_delete_order", [order_id])

        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if not response or response[0] is None:
            raise HTTPException(status_code=500, detail="Unexpected error occurred while deleting order.")

        parsed_json = json.loads(response[0])
        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        conn.rollback()
        error_msg = str(err).split(": ", 1)[-1]
        return JSONResponse(status_code=400, content={"status": "error", "message": error_msg})