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
    SELECT service_id, short_title, description, price, is_service_group, parent_service_id, prompt_message as prompt , active, is_radio
    FROM service 
    WHERE category_id = %s
    """
    cursor.execute(query, (category_id,))
    
    services = cursor.fetchall()
    conn.close()
    
    return services

def build_tree(services, parent_id=None):
    """Recursively build service tree and mark last leaf"""
    tree = []
    for service in services:
        if service["parent_service_id"] == parent_id:
            # Recursively get children services
            children = build_tree(services, service["service_id"])
            if children:
                service["services"] = children
                service["is_last_leaf"] = 'N'  # Not a leaf if it has children
            else:
                service["is_last_leaf"] = 'Y'  # It's a leaf node if no children
            tree.append(service)
    return tree

@router.get("/admin_get_service_tree")
def get_services(request: Request, category_id: int = Query(..., description="Category ID to filter services")):

    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    

    """API endpoint to return filtered service tree with is_last_leaf flag"""
    services = fetch_services(request, category_id)
    if not services:
        # return {"message": "No services found for the given category ID", "service_group": []}
        return JSONResponse(
            status_code = 404,
            content = {"status": "error","message": "No services found for the given category ID"}
        )
    
    # Build the service tree
    service_tree = build_tree(services, parent_id=None)
    
    return {"service_group": service_tree}















# def fetch_service_by_id_or_parent(request: Request, service_id: int):
#     """Fetch service by service_id or services whose parent_service_id matches the service_id"""
    
#     # Validate token
#     if not validate_token(request):
#         return JSONResponse(
#             status_code=401,
#             content={"status": "error", "message": "Invalid Access Token"}
#         )

#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)

#     query = """
#     SELECT service_id, short_title, description, price, is_service_group, parent_service_id, prompt_message, active
#     FROM service 
#     WHERE service_id = %s OR parent_service_id = %s
#     """
#     cursor.execute(query, (service_id, service_id))
    
#     services = cursor.fetchall()
#     conn.close()
#     print(services)

#     return services

# def build_tree2(services, parent_id=None):
#     """Recursively build service tree and mark last leaf"""
#     tree = []
#     for service in services:
#         if service["parent_service_id"] == parent_id:
#             # Recursively get children services
#             children = build_tree2(services, service["service_id"])
#             if children:
#                 service["services"] = children
#                 service["is_last_leaf"] = 'N'  # Not a leaf if it has children
#             else:
#                 service["is_last_leaf"] = 'Y'  # It's a leaf node if no children
#             tree.append(service)
#     return tree

# @router.get("/admin_get_service_subtree")
# def get_service_tree_by_service_id(request: Request, service_id: int = Query(..., description="Service ID to fetch service or its children")):
#     """API endpoint to return the service tree by service_id or its children"""
    
#     # Validate token
#     if not validate_token(request):
#         return JSONResponse(
#             status_code=401,
#             content={"status": "error", "message": "Invalid Access Token"}
#         )
    
#     services = fetch_service_by_id_or_parent(request, service_id)
    
#     if not services:
#         return JSONResponse(
#             status_code=404,
#             content={"status": "error", "message": "No services found for the given service ID"}
#         )

#     # Build the service tree
#     service_tree = build_tree2(services, parent_id=None)
    
#     return {"service_group": service_tree}



def find_root_service(services, service_id):
    for service in services:
        if service["service_id"] == service_id:
            return service
    return None


def fetch_service_by_id_or_parent(request: Request, service_id: int):
    """Fetch service by service_id or services whose parent_service_id matches the service_id"""
    
    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT service_id, short_title, description, active, price, is_radio, prompt_message as prompt, is_service_group, parent_service_id
    FROM service 
    WHERE service_id = %s OR parent_service_id = %s
    """
    cursor.execute(query, (service_id, service_id))
    
    services = cursor.fetchall()
    conn.close()
    
    # Log services fetched
    # logging.info(f"Fetched services: {services}")
    print(services)
    
    return services



# def build_tree2(services, parent_id=None):
#     """Recursively build service tree and mark last leaf"""
#     tree = []
    
#     print(f"Building tree for parent_id: {parent_id}, available services: {len(services)}")  # Debugging
    
#     for service in services:
#         print(f"Checking service {service['service_id']} with parent_service_id {service['parent_service_id']}")  # Debugging
        
#         # Check if this service is a child of the given parent_id
#         if service["parent_service_id"] == parent_id:
#             print(f"Service {service['service_id']} matches parent_id {parent_id}")  # Debugging

#             # Recursively get children services
#             children = build_tree2(services, service["service_id"])
            
#             if children:
#                 service["services"] = children
#                 service["is_last_leaf"] = 'N'  # Not a leaf if it has children
#             else:
#                 service["is_last_leaf"] = 'Y'  # It's a leaf node if no children
                
#             # Append the service to the tree
#             tree.append(service)
#             return tree

#     # If no services were added to the tree (i.e., no matching parent_id), return the parent service itself as a leaf
#     if not tree and parent_id is not None:
#         print(f"Returning leaf service for parent_id {parent_id}: {service}")
#         # When there's no matching child, return the service as a leaf
#         return [{
#             "service_id": service["service_id"],  # Accessing the individual service from the list
#             "short_title": service["short_title"],
#             "description": service["description"],
#             "price": service["price"],
#             "is_service_group": service["is_service_group"],
#             "prompt": service["prompt"],
#             "active": service["active"],
#             "is_last_leaf": "Y"
#         } for service in services]  # This is the correct way to iterate through services


    
def build_tree2(services, parent_id=None):
    tree = []

    for service in services:
        # ❗ Prevent self-reference
        if service["parent_service_id"] == parent_id and service["service_id"] != parent_id:
            children = build_tree2(services, service["service_id"])

            if children:
                service["services"] = children
                service["is_last_leaf"] = "N"
            else:
                service["is_last_leaf"] = "Y"

            tree.append(service)

    # If no children, return this service itself (as leaf)
    # if not tree and parent_id is not None:
    #     for service in services:
    #         if service["service_id"] == parent_id:
    #             return [{
    #                 "service_id": service["service_id"],
    #                 "short_title": service["short_title"],
    #                 "description": service["description"],
    #                 "price": service["price"],
    #                 "is_service_group": service["is_service_group"],
    #                 "prompt": service["prompt"],
    #                 "active": service["active"],
    #                 "is_last_leaf": "Y",
    #                 "services": []
    #             }]
    return tree



@router.get("/admin_get_service_subtree")
def get_service_tree_by_service_id(request: Request, service_id: int = Query(..., description="Service ID to fetch service or its children")):
    """API endpoint to return the service tree by service_id or its children"""
    
    # Validate token
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    # Fetch services based on service_id or parent_service_id
    services = fetch_service_by_id_or_parent(request, service_id)
    
    if not services:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "No services found for the given service ID"}
        )

    root_service = find_root_service(services, service_id)
    if not root_service:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "Service ID not found"}
        )

    tree = build_tree2(services, parent_id=service_id)
    # Mark root node
    if tree:
        root_service["services"] = tree
        root_service["is_last_leaf"] = "N"
    else:
        root_service["is_last_leaf"] = "Y"

    return {"service_group": [root_service]}



from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import mysql.connector
from database import get_db_connection  # Ensure you have this function implemented
from routes.auth import validate_token  # Import token validation function
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# from fastapi.responses import JSONResponse
import pymysql
# import json
# from database import get_db_connection  # Ensure you have a DB connection function
from typing import Optional

class ServiceCreateRequest(BaseModel):
    short_title: str | None = None
    description: str
    active: str | None = None
    sequence_no: int | None = None
    image_urls: str | None = None
    parent_service_id: int | None = None
    is_service_group: str | None = None
    category_id: int | None = None
    prompt_message: str | None = None
    price: int | None = None
    is_radio: str | None = None


@router.post("/admin_insert_service")
def insert_service(req: Request, request: ServiceCreateRequest):
    if not validate_token(req):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.callproc("admin_insert_service", [
            request.short_title,
            request.description,
            request.active,
            request.sequence_no,
            request.image_urls,
            request.parent_service_id,
            request.is_service_group,
            request.category_id,
            request.prompt_message,
            request.price,
            request.is_radio
        ])

        # Fetch and parse stored procedure result
        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if not response or "json_response" not in response:
            raise HTTPException(status_code=500, detail="Unexpected error occurred while inserting service.")

        return json.loads(response["json_response"])

    except mysql.connector.Error as err:
        conn.rollback()
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(err)}
        )






class AdminUpdateServiceRequest(BaseModel):
    service_id: int | None = None
    short_title: str | None = None
    description: str | None = None
    active: str | None = None
    sequence_no: int | None = None
    image_urls: str | None = None
    service_group_id: int | None = None
    parent_service_id: int | None = None
    is_service_group: str | None = None
    category_id: int | None = None
    prompt_message: str | None = None
    price: float | None = None
    is_radio: str | None = None

@router.put("/admin_update_service")
def update_service(request: Request, service: AdminUpdateServiceRequest):
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.callproc("admin_update_service", [
            service.service_id, service.short_title, service.description,
            service.active, service.sequence_no, service.image_urls,
            service.service_group_id, service.parent_service_id,
            service.is_service_group, service.category_id,
            service.prompt_message, service.price, service.is_radio
        ])

        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if not response or response[0] is None:
            raise HTTPException(status_code=500, detail="Unexpected error occurred while updating service.")

        parsed_json = json.loads(response[0])
        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        conn.rollback()
        error_msg = str(err).split(": ", 1)[-1]
        return JSONResponse(status_code=400, content={"status": "error", "message": error_msg})
    





@router.delete("/admin_delete_service")
def delete_service(request: Request, service_id: int = Query(...)):
    if not validate_token(request):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.callproc("admin_delete_service", [service_id])

        response = None
        for result in cursor.stored_results():
            response = result.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        if not response or response[0] is None:
            raise HTTPException(status_code=500, detail="Unexpected error occurred while deleting service.")

        parsed_json = json.loads(response[0])
        return JSONResponse(content=parsed_json)

    except mysql.connector.Error as err:
        conn.rollback()
        error_msg = str(err).split(": ", 1)[-1]
        return JSONResponse(status_code=400, content={"status": "error", "message": error_msg})