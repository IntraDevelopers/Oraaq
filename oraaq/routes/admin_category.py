from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import mysql.connector
from database import get_db_connection  # Ensure you have this function implemented
from routes.auth import validate_token  # Import token validation function
import json
import base64

router = APIRouter()
@router.get("/admin_get_categories")
def get_service_categories(request: Request):
                # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    try:
        conn = get_db_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed.")

        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                category_id, short_title, description, 
                sequence_no, image_url, prompt_message, 
                file_mimetype AS mime_type, image_blob, active
            FROM SERVICE_CATEGORY
            ORDER BY SEQUENCE_NO
        """

        cursor.execute(query)
        result = cursor.fetchall()

        # Convert binary image data (BLOB) to Base64
        for row in result:
            if row["image_blob"]:
                row["image_blob"] = base64.b64encode(row["image_blob"]).decode("utf-8")

        cursor.close()
        conn.close()

        return JSONResponse(status_code=200, content={"status": "success", "items": result})

    except Exception as err:
        return JSONResponse(status_code=400, content={"status": "error", "message": str(err)})
