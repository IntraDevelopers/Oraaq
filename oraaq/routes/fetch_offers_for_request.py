import json
from fastapi import APIRouter, HTTPException, Request
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
from datetime import datetime
from decimal import Decimal

router = APIRouter()

@router.get("/fetch_offers_for_request")
def fetch_offers_for_request(request: Request):
    try:
        request_id = request.query_params.get("request_id")  # Get request_id as a string

        if not request_id:
            request_id = None  # Pass NULL to the stored procedure

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("fetch_offers_for_request", [request_id])

        # Fetch the results
        offers = []
        for result in cursor.stored_results():
            offers = result.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not offers:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "No offers found for the request.",
                    "data": []
                }
            )

        # Convert datetime and decimal values
        for offer in offers:
            for key, value in offer.items():
                if isinstance(value, datetime):
                    offer[key] = value.strftime("%Y-%m-%d %H:%M:%S")  # Convert datetime to string
                elif isinstance(value, Decimal):
                    offer[key] = float(value)  # Convert Decimal to float

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Offers fetched successfully",
                "data": offers
            }
        )

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure
        print(f"Error: {err}")
        error_msg = str(err)
        if ": " in error_msg:
            error_msg = error_msg.split(": ", 1)[-1]  # Extract readable message

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )
