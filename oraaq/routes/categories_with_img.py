from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from database import get_db_connection
import base64
from routes.auth import validate_token  # Import token validation function

router = APIRouter()

@router.post("/admin_insert_category")
async def create_service_category(
    request: Request,  # Request is needed to read the Authorization header
    short_title: str = Form(...),
    description: str = Form(...),
    active: str = Form(...),
    sequence_no: int = Form(None),
    image_url: str = Form(None),
    prompt_message: str = Form(None),
    file_mimetype: str = Form(None),
    body: UploadFile = File(None)  # Handling file upload
):

                # Validate token
    # if not validate_token(request):
    #     return JSONResponse(
    #         status_code=401,
    #         content={"status": "error", "message": "Invalid Access Token"}
    #     )

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed.")

    cursor = conn.cursor()
    # Read image file as binary
    image_blob = await body.read() if body else None

    query = """
        INSERT INTO SERVICE_CATEGORY (
            SHORT_TITLE, 
            DESCRIPTION, 
            ACTIVE, 
            SEQUENCE_NO, 
            IMAGE_URL,
            PROMPT_MESSAGE, 
            FILE_MIMETYPE, 
            IMAGE_BLOB
         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        short_title,
        description,
        active,
        sequence_no,
        image_url,
        prompt_message,
        file_mimetype,
        image_blob
    )

    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

    return JSONResponse(
        status_code=201,
        content={"status": "success", "message": "Service category created successfully"}
    )


#  http://portal.intraerp.com:8080/ords/oraaq/api/Get_Categories


@router.get("/Get_Categories")
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
                file_mimetype AS mime_type, image_blob
            FROM SERVICE_CATEGORY
            WHERE ACTIVE != 'N'
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






@router.put("/admin_update_category")
async def update_service_category(
    request: Request,
    category_id: int = Form(...),
    short_title: str = Form(None),
    description: str = Form(None),
    active: str = Form(None),
    sequence_no: int = Form(None),
    image_url: str = Form(None),
    prompt_message: str = Form(None),
    file_mimetype: str = Form(None),
    body: UploadFile = File(None)  # Optional image update
):
    
    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed.")

    cursor = conn.cursor()

    # Read new image file if provided
    image_blob = await body.read() if body else None

    # Build dynamic SET clause
    update_fields = []
    values = []

    if short_title is not None:
        update_fields.append("SHORT_TITLE = %s")
        values.append(short_title)
    
    if description is not None:
        update_fields.append("DESCRIPTION = %s")
        values.append(description)

    if active is not None:
        update_fields.append("ACTIVE = %s")
        values.append(active)

    if sequence_no is not None:
        update_fields.append("SEQUENCE_NO = %s")
        values.append(sequence_no)

    if image_url is not None:
        update_fields.append("IMAGE_URL = %s")
        values.append(image_url)

    if prompt_message is not None:
        update_fields.append("PROMPT_MESSAGE = %s")
        values.append(prompt_message)

    if file_mimetype is not None:
        update_fields.append("FILE_MIMETYPE = %s")
        values.append(file_mimetype)

    if image_blob:
        update_fields.append("IMAGE_BLOB = %s")
        values.append(image_blob)

    # If no fields are provided, return an error
    if not update_fields:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "No update fields provided"}
        )

    # Final query
    query = f"UPDATE SERVICE_CATEGORY SET {', '.join(update_fields)} WHERE CATEGORY_ID = %s"
    values.append(category_id)

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    return JSONResponse(
        status_code=200,
        content={"status": "success", "message": "Service category updated successfully"}
    )


@router.delete("/admin_delete_category/{category_id}")
def delete_service_category(category_id: int, request: Request):

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed.")

    cursor = conn.cursor()

    # Delete query
    query = "DELETE FROM SERVICE_CATEGORY WHERE CATEGORY_ID = %s"
    cursor.execute(query, (category_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return JSONResponse(
        status_code=200,
        content={"status": "success", "message": "Service category deleted successfully"}
    )
