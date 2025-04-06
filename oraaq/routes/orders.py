import json
from fastapi import APIRouter, HTTPException, Query, Request
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
from schemas import GenerateOrderRequest
from routes.auth import validate_token
from fastapi.responses import JSONResponse

router = APIRouter()

# @router.post("/generateOrder2")
# def generate_order(req: Request, request: GenerateOrderRequest):

#     # Validate token
#     if not validate_token(req):
#         return JSONResponse(
#             status_code=401,
#             content={"status": "error", "message": "Invalid Access Token"}
#         )
    

#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         # Convert order details list to JSON string
#         order_details_json = json.dumps([detail.dict() for detail in request.order_details])

#         # Call the stored procedure
#         cursor.callproc("generate_order_with_detail", [
#             request.customer_id,
#             request.order_required_date,
#             request.category_id,
#             request.customer_amount,
#             request.total_amount,
#             request.radius,
#             request.longitude,
#             request.latitude,
#             order_details_json
#         ])

#         # Fetch the order ID
#         response = None
#         for result in cursor.stored_results():
#             response = result.fetchone()

#         conn.commit()
#         cursor.close()
#         conn.close()

#         if response:
#             return JSONResponse(
#                 status_code=200,
#                 content={
#                     "status": "success",
#                     "message": "Order created successfully",
#                     "order_id": response["order_id"]
#                 }
#             )
#         else:
#             raise HTTPException(status_code=500, detail="Unexpected error during order creation.")

#     except mysql.connector.Error as err:
#         conn.rollback()  # Ensure rollback on failure

#         error_msg = str(err)
#         if ": " in error_msg:
#             error_msg = error_msg.split(": ", 1)[-1]  # Extract readable message

#         return JSONResponse(
#             status_code=400,
#             content={"status": "error", "message": error_msg},
#         )



@router.post("/generateOrder2")
def generate_order(req: Request, request: GenerateOrderRequest):

    # Validate token
    if not validate_token(req):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Extract data correctly
        order_master = request.order_master
        order_details_json = json.dumps([detail.dict() for detail in request.order_detail])

        # Call the stored procedure
        cursor.callproc("generate_order_with_detail", [
            order_master.customer_id,
            order_master.order_required_date,
            order_master.category_id,
            order_master.customer_amount,
            order_master.total_amount,
            order_master.radius,
            order_master.longitude,
            order_master.latitude,

            order_details_json
        ])

        # Fetch the order ID
        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if response:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "Order created successfully",
                    "order_id": response["order_id"]
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Unexpected error during order creation.")

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure

        error_msg = str(err)
        if ": " in error_msg:
            error_msg = error_msg.split(": ", 1)[-1]  # Extract readable message

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )



from fastapi import APIRouter, HTTPException
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
from schemas import CancelOrderRequest
from datetime import datetime

# router = APIRouter()

# @router.put("/cancelWorkOrder")
# def cancel_or_complete_order(req: Request, request: CancelOrderRequest):

#     # Validate token
#     if not validate_token(req):
#         return JSONResponse(
#             status_code=401,
#             content={"status": "error", "message": "Invalid Access Token"}
#         )

#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         # Call the stored procedure
#         cursor.callproc("cancel_or_complete_order_by_merchant", [
#             request.bidding_id,
#             request.merchant_id,
#             request.order_status_id
#         ])

#         # Fetch response from the procedure
#         result = []
#         for res in cursor.stored_results():
#             result = res.fetchall()

#         conn.commit()
#         cursor.close()
#         conn.close()

#         if not result:
#             return JSONResponse(
#                 status_code=400,
#                 content={"status": "error", "message": "Unexpected error occurred.", "data": {}}
#             )

#         # Convert response from a stringified JSON to an actual dictionary
#         response_data = result[0]
#         if "response" in response_data and isinstance(response_data["response"], str):
#             response_data = json.loads(response_data["response"])  # Convert string JSON to dict

#         # Ensure proper response order: status -> message -> data
#         formatted_response = {
#             "status": response_data.get("status", "success"),
#             "message": response_data.get("message", ""),
#             "data": response_data.get("data", {})
#         }

#         return JSONResponse(
#             status_code=200,
#             content=formatted_response
#         )

#     except mysql.connector.Error as err:
#         conn.rollback()  # Ensure rollback on failure

#         error_msg = str(err)
#         if ": " in error_msg:
#             error_msg = error_msg.split(": ", 1)[-1]  # Extract readable message

#         return JSONResponse(
#             status_code=400,
#             content={"status": "error", "message": error_msg, "data": {}},
#         )





from fastapi import Query

@router.put("/cancelWorkOrder")
def cancel_or_complete_order(
    req: Request,
    bidding_id: int = Query(..., description="Bidding ID"),
    merchant_id: int = Query(..., description="Merchant ID"),
    order_status_id: int = Query(..., description="Order Status ID (2 = Cancelled, 3 = Completed)")
):
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
        cursor.callproc("cancel_or_complete_order_by_merchant", [
            bidding_id,
            merchant_id,
            order_status_id
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
                content={"status": "error", "message": "Unexpected error occurred.", "data": {}}
            )

        # Convert response from a stringified JSON to an actual dictionary
        response_data = result[0]
        if "response" in response_data and isinstance(response_data["response"], str):
            response_data = json.loads(response_data["response"])

        formatted_response = {
            "status": response_data.get("status", "success"),
            "message": response_data.get("message", ""),
            "data": response_data.get("data", {})
        }

        return JSONResponse(
            status_code=200,
            content=formatted_response
        )

    except mysql.connector.Error as err:
        conn.rollback()

        error_msg = str(err)
        if ": " in error_msg:
            error_msg = error_msg.split(": ", 1)[-1]

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg, "data": {}},
        )




from pydantic import BaseModel

# Define request body model
class CancelRequestModel(BaseModel):
    request_id: int

@router.put("/cancel_request")
def cancel_request( request: Request, data: CancelRequestModel):

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    """
    Cancel a service request by updating its status in the database.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure with request_id from JSON body
        cursor.callproc("cancel_request", [data.request_id])

        # Fetch response from the procedure
        result = []
        for res in cursor.stored_results():
            result = res.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not result:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "No data found for the provided request ID."}
            )

        return JSONResponse(
            status_code=200,
            content=result[0]  # Returning the first row as response
        )

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(err)},
        )


# Request Body Model
class CancelOrderRequest(BaseModel):
    order_id: int
    customer_id: int

@router.put("/cancel_c_order_by_customer")
def cancel_customer_order(req: Request, request: CancelOrderRequest):

    # Validate token
    if not validate_token(req):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    """
    Cancels an order by a customer.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("cancel_c_order_by_customer", [
            request.order_id,
            request.customer_id
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
                status_code=404,
                content={"status": "error", "message": "Order cancellation failed."}
            )

        # Convert the JSON string in 'data' column to a dictionary
        response_data = result[0]
        if "data" in response_data and isinstance(response_data["data"], str):
            response_data["data"] = json.loads(response_data["data"])

        return JSONResponse(
            status_code=200,
            content=response_data
        )

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure

        # Extract only the actual error message after ": "
        error_msg = str(err)
        if ": " in error_msg:
            error_msg = error_msg.split(": ", 1)[-1]  # Get only the message part

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )


# Request Body Model
class UpdateOfferRequest(BaseModel):
    request_id: int
    new_offer_amount: float  # Ensures amount is a decimal

# FastAPI Route
@router.put("/update_offer_amount")
def update_offer_amount(req: Request, request: UpdateOfferRequest):

    # Validate token
    if not validate_token(req):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    """
    Update the offer amount for a given request_id.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the MySQL Stored Procedure
        cursor.callproc("update_offer_amount", [request.request_id, request.new_offer_amount])

        # Fetch the results
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

        # ✅ Convert MySQL JSON string response into a dictionary
        response_data = result[0]
        if "data" in response_data and isinstance(response_data["data"], str):
            response_data["data"] = json.loads(response_data["data"])

        return JSONResponse(
            status_code=200,
            content=response_data
        )

    except mysql.connector.Error as err:
        conn.rollback()  # Rollback in case of failure

        # Extract only the meaningful error message after ": "
        error_msg = str(err)
        if ": " in error_msg:
            error_msg = error_msg.split(": ", 1)[-1]  # Keep only the relevant part

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )

# Define the request model
class UpdateRadiusRequest(BaseModel):
    request_id: int
    new_radius: float

@router.put("/updateRadius")
def update_radius(req: Request, request: UpdateRadiusRequest):

    # Validate token
    if not validate_token(req):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    """
    Updates the radius for a given request ID.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("update_radius", [request.request_id, request.new_radius])

        # Fetch response from the procedure
        result = []
        for res in cursor.stored_results():
            result = res.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not result:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Request ID not found."}
            )

        # ✅ Fix: Convert JSON string to a proper dictionary
        response_data = result[0]
        if "data" in response_data and isinstance(response_data["data"], str):
            response_data["data"] = json.loads(response_data["data"])

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Radius updated successfully.",
                "data": response_data["data"]  # Ensure proper JSON formatting
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