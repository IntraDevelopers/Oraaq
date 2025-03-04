from fastapi import APIRouter, Query
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
import json

router = APIRouter()

@router.get("/GetService")
def get_services(category_id: int = Query(None, description="Category ID to filter services")):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure with category_id
        cursor.callproc("GetServiceTree", [category_id])

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
                content={"status": "error", "message": "No services found for the given category.", "data": {}}
            )

        # Convert response from a stringified JSON to a dictionary
        response_data = result[0]
        if "data" in response_data and isinstance(response_data["data"], str):
            try:
                response_data["data"] = json.loads(response_data["data"])  # Convert string JSON to dict
            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=400,
                    content={"status": "error", "message": "Invalid JSON format", "raw_data": response_data["data"]}
                )

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

    except mysql.connector.Error as err:
        conn.rollback()  # Ensure rollback on failure

        error_msg = str(err)
        if ": " in error_msg:
            error_msg = error_msg.split(": ", 1)[-1]  # Extract readable message

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": error_msg, "data": {}},
        )
