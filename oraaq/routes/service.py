from fastapi import APIRouter, Query, Request
import mysql.connector
from database import get_db_connection
from fastapi.responses import JSONResponse
import json
from routes.auth import validate_token


router = APIRouter()


def fetch_services(request: Request, category_id: int):

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    """Fetch service data from MySQL filtered by category_id and active != 1"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT service_id, short_title, description, price, is_service_group, parent_service_id, prompt_message as prompt, is_radio
    FROM service
    WHERE category_id = %s and active != 'N'
    """
    cursor.execute(query, (category_id,))
    
    services = cursor.fetchall()    
    conn.close()
    # Convert service_id and parent_service_id to integers to avoid lookup issues
    for service in services:
        service["service_id"] = int(service["service_id"])  # Convert to int
        service["parent_service_id"] = int(service["parent_service_id"]) if service["parent_service_id"] else None

    # print("Services Retrieved:", services)
    return services


def build_tree(services):
    """
    Builds a service tree from a flat list based on parent_service_id.
    Services with a NULL parent_service_id are treated as root nodes.
    """
    service_map = {service["service_id"]: service for service in services}  # Map services by service_id
    
    # Initialize children list and set defaults
    for service in services:
        service["services"] = []  # Initialize empty list for child services
        service["is_last_leaf"] = "Y"  # Default to 'Y', will change later if it gets children

    # Assign children to their respective parents
    for service in services:
        parent_id = service.get("parent_service_id")
        if parent_id is not None and parent_id in service_map:
            parent = service_map[parent_id]
            parent["services"].append(service)
            parent["is_last_leaf"] = "N"  # Parent cannot be a leaf

    # Extract only root services (those with parent_service_id as None)
    tree = [service for service in services if service["parent_service_id"] is None]

    return tree # Wrapping in expected output format

@router.get("/GetService")
def get_services(request: Request, category_id: int = Query(..., description="Category ID to filter services")):

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    """API endpoint to return filtered service tree with is_last_leaf flag"""
    services = fetch_services(request, category_id)  # Pass both request and category_id here
    if not services:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "No services found for the given category ID"}
        )
    
    # Build the service tree
    service_tree = build_tree(services)
    
    return {"service_group": service_tree}

