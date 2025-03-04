from fastapi import APIRouter, HTTPException
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
import json

router = APIRouter()

@router.get("/getCategories")
def generate_categories_json():
    """
    Fetch active service categories in JSON format.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Call the stored procedure
        cursor.callproc("generate_categories_json")

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
                content={"status": "error", "message": "No categories found.", "data": []}
            )

        # The stored procedure returns a JSON string inside "json_response"
        response_data = result[0]  # First row of the response

        if "json_response" in response_data and isinstance(response_data["json_response"], str):
            try:
                # Convert string JSON to dictionary
                parsed_json = json.loads(response_data["json_response"])
                return JSONResponse(status_code=200, content=parsed_json)

            except json.JSONDecodeError:
                return JSONResponse(
                    status_code=500,
                    content={"status": "error", "message": "Invalid JSON format from stored procedure."}
                )

        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Invalid response format from database."}
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
