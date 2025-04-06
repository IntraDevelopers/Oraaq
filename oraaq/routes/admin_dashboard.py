from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import mysql.connector
import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import mysql.connector
from database import get_db_connection  # Ensure you have this function implemented
from routes.auth import validate_token  # Import token validation function
import json
from pydantic import BaseModel


router = APIRouter()


@router.get("/get_admin_dashboard_cards")
def get_admin_dashboard(req: Request):
    
    if not validate_token(req):
        return JSONResponse(
            status_code=401,
            content={"status": "error", "message": "Invalid Access Token"}
        )
    
    try:
        # Validate Token (if required)
        # if not validate_token(req):
        #     return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid Access Token"})

        conn = get_db_connection()
        cursor = conn.cursor()

        # Call the stored procedure
        cursor.callproc("get_admin_dashboard_cards")

        # Fetch the result
        result = None
        for res in cursor.stored_results():
            result = res.fetchone()  # Fetch single row

        cursor.close()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="No data found.")

        # Convert MySQL JSON result to Python dictionary
        dashboard_data = json.loads(result[0])  # MySQL returns a JSON string

        return JSONResponse(status_code=200, content=dashboard_data)

    except mysql.connector.Error as err:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(err)})

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})




# @router.get("/get_admin_dashboard_charts")
# def get_admin_dashboard(req: Request):
    
#     # if not validate_token(req):
#     #     return JSONResponse(
#     #         status_code=401,
#     #         content={"status": "error", "message": "Invalid Access Token"}
#     #     )
    
#     try:
#         # Validate Token (if required)
#         # if not validate_token(req):
#         #     return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid Access Token"})

#         conn = get_db_connection()
#         cursor = conn.cursor()

#         # Call the stored procedure
#         cursor.callproc("get_admin_dashboard_charts")

#         # Fetch the result
#         result = None
#         for res in cursor.stored_results():
#             result = res.fetchone()  # Fetch single row

#         cursor.close()
#         conn.close()

#         if not result:
#             raise HTTPException(status_code=404, detail="No data found.")

#         # Convert MySQL JSON result to Python dictionary
#         dashboard_data = json.loads(result[0])  # MySQL returns a JSON string

#         return JSONResponse(status_code=200, content=dashboard_data)

#     except mysql.connector.Error as err:
#         return JSONResponse(status_code=500, content={"status": "error", "message": str(err)})

#     except Exception as e:
#         return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})



# Helper function to fetch data for monthly orders
def fetch_monthly_orders():
    query = """
    SELECT DATE_FORMAT(order_date, '%Y-%m') AS order_month, COUNT(*) AS order_count
    FROM ORDER_Master
    GROUP BY DATE_FORMAT(order_date, '%Y-%m')
    ORDER BY order_month;
    """
    connection = get_db_connection()
    with connection.cursor(dictionary=True) as cursor:  # <-- use dictionary=True
        cursor.execute(query)
        result = cursor.fetchall()
    connection.close()
    return result




# Helper function to fetch data for status-wise orders
def fetch_status_wise_orders():
    query = """
    SELECT COALESCE(os.short_title, 'Unknown') AS order_status, COUNT(ot.order_status_id) AS order_count
    FROM order_transaction ot
    LEFT JOIN order_status os ON ot.order_status_id = os.order_status_id
    GROUP BY os.short_title
    ORDER BY order_count DESC;
    """
    connection = get_db_connection()
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    connection.close()
    return result


# Helper function to fetch data for services sold
def fetch_services_sold():
    query = """
    SELECT service_id, service_title, service_count
    FROM (
      SELECT svc.service_id, COALESCE(s.short_title, 'Unknown Service') AS service_title, svc.service_count
      FROM (
        SELECT od.service_id, COUNT(*) AS service_count
        FROM order_detail od
        JOIN service s ON od.service_id = s.service_id
        WHERE NOT EXISTS (SELECT 1 FROM service sub_s WHERE sub_s.PARENT_SERVICE_ID = s.SERVICE_ID)
        GROUP BY od.service_id
      ) svc
      LEFT JOIN service s ON svc.service_id = s.service_id
      ORDER BY svc.service_count DESC
      LIMIT 25
    ) AS services_sold;
    """
    connection = get_db_connection()
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    connection.close()
    return result



# # API endpoint for the admin dashboard charts
# @router.get("/get_admin_dashboard_charts")
# async def get_admin_dashboard_charts():
#     try:
#         # Fetch data from the database
#         monthly_orders = fetch_monthly_orders()
#         status_wise_orders = fetch_status_wise_orders()
#         services_sold = fetch_services_sold()

#         # Ensure all the data is returned as dictionaries and structure the response
#         response = {
#             "monthly_orders": [
#                 {"order_month": item["order_month"], "order_count": item["order_count"]}
#                 for item in monthly_orders
#             ],
#             "status_wise_orders": [
#                 {"order_status": item["short_title"], "order_count": item["order_count"]}
#                 for item in status_wise_orders
#             ],
#             "services_sold": [
#                 {"service_id": item["service_id"], "service_title": item["service_title"], "service_count": item["service_count"]}
#                 for item in services_sold
#             ]
#         }

#         return response

#     except Exception as e:
#         # Handle any database or other exceptions
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")




# API endpoint for the admin dashboard charts
@router.get("/get_admin_dashboard_charts")
async def get_admin_dashboard_charts():
    try:
        # Fetch data from the database
        monthly_orders = fetch_monthly_orders()
        status_wise_orders = fetch_status_wise_orders()
        services_sold = fetch_services_sold()

        # Build the JSON response
        response = {
            "monthly_orders": monthly_orders,
            "status_wise_orders": status_wise_orders,
            "services_sold": services_sold
        }

        return response

    except Exception as e:
        # Handle any database or other exceptions
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

