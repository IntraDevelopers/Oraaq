from fastapi import APIRouter, HTTPException
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
from schemas import AddOrderRatingRequest
import json

router = APIRouter()

@router.post("/addRating")
def add_order_rating(request: AddOrderRatingRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("add_order_rating", [
            request.order_id,
            request.rating_for_user_type,
            request.merchant_id,
            request.customer_id,
            request.rating_by,
            request.rating,
            request.review
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
        if "data" in response_data and isinstance(response_data["data"], str):
            response_data["data"] = json.loads(response_data["data"])  # Convert string JSON to dict

        # Ensure proper response order: status -> message -> data
        formatted_response = {
            "status": response_data.get("status", "success"),
            "message": response_data.get("message", ""),
            "data": response_data.get("data", {})
        }

        return JSONResponse(
            status_code=200,
            content=formatted_response
        )

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
            content={"status": "error", "message": error_msg, "data": {}},
        )
