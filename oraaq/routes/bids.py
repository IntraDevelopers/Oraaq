from fastapi import APIRouter, HTTPException
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
from schemas import PostBidRequest
from pydantic import BaseModel

router = APIRouter()

@router.post("/submitBid")
def post_bid(request: PostBidRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("post_bid", [
            request.order_id,
            request.merchant_id,
            request.bid_amount,
            request.bid_remarks,
            request.bid_expiration  # Convert to MySQL DATETIME format
        ])

        # Fetch the inserted bidding ID
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
                    "message": "Bid submitted successfully",
                    "bidding_id": response["bidding_id"]
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Unexpected error during bid submission.")

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure

        error_msg = str(err)
        if ": " in error_msg:
            error_msg = error_msg.split(": ", 1)[-1]  # Extract readable message

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )



from fastapi import APIRouter, HTTPException, Query
from decimal import Decimal


@router.get("/getAllBids")
def get_all_bids(order_id: int = Query(..., description="Order ID")):
    """
    Fetch all active bids for a given order.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("get_all_bids", [order_id])

        # Fetch the results
        result = []
        for res in cursor.stored_results():
            result = res.fetchall()

        conn.commit()
        cursor.close()
        conn.close()

        if not result:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "No bids found for the provided order.",
                    "data": []
                }
            )

        # Convert Decimal to float
        for bid in result:
            for key, value in bid.items():
                if isinstance(value, Decimal):
                    bid[key] = float(value)  # Convert Decimal to float

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "All bids.",
                "data": result
            }
        )

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure
        error_msg = str(err).split(": ", 1)[-1]  # Extract readable message

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg},
        )




# Request Body Schema
class CancelBidRequest(BaseModel):
    bid_id: int
    merchant_id: int

@router.put("/cancel_bid_for_merchant")
def cancel_bid(request: CancelBidRequest):
    """
    Cancels a bid for the merchant.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("cancel_bid_for_merchant", [request.bid_id, request.merchant_id])

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
                content={"status": "error", "message": "Unexpected error occurred."}
            )

        return JSONResponse(
            status_code=200,
            content=result[0]  # The stored procedure returns a JSON object
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