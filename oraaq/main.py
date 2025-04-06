from fastapi import FastAPI
from routes import email, admin_dashboard, admin_service, admin_orders, admin_merchants, admin_customer, admin_category, admin_app_user, categories_with_img,users, auth, chatai, orders, requests, bids, service_requests, get_applied_merchant_work_order, GetAllNewRequestForMerchant, offers, work_orders, ratings, customer, merchant, categories, service
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="Oraaq Marketplace API", version="1.0.0")

# Allow all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],   # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],   # Allow all headers
)

# Register routes

app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(chatai.router, prefix="/api", tags=["ChatAI"])
app.include_router(orders.router, prefix="/api", tags=["Orders"])
app.include_router(requests.router, prefix="/api", tags=["Requests"])
app.include_router(bids.router, prefix="/api", tags=["Bids"])
app.include_router(service_requests.router, prefix="/api", tags=["Service Requests"])
app.include_router(get_applied_merchant_work_order.router, prefix="/api", tags=["WorkOrders"])
app.include_router(GetAllNewRequestForMerchant.router, prefix="/api", tags=["Merchant Requests"])
app.include_router(offers.router, prefix="/api", tags=["Offers"])
app.include_router(work_orders.router, prefix="/api", tags=["Work Orders"])
app.include_router(ratings.router, prefix="/api", tags=["Ratings"])
app.include_router(customer.router, prefix="/api", tags=["Customer"])
app.include_router(merchant.router, prefix="/api", tags=["Merchant"])
app.include_router(categories.router, prefix="/api", tags=["Categories"])
app.include_router(service.router, prefix="/api", tags=["Service Tree"])
app.include_router(categories_with_img.router, prefix="/api", tags=["Categories With Images"])
app.include_router(admin_app_user.router, prefix="/api", tags=["Admin App User"])
app.include_router(admin_category.router, prefix="/api", tags=["Admin Category"])
app.include_router(admin_customer.router, prefix="/api", tags=["Admin Customer"])
app.include_router(admin_merchants.router, prefix="/api", tags=["Admin Merchant"])
app.include_router(admin_orders.router, prefix="/api", tags=["Admin Order"])
app.include_router(admin_service.router, prefix="/api", tags=["Admin Service"])
app.include_router(admin_dashboard.router, prefix="/api", tags=["Admin Dashboard"])
app.include_router(email.router, prefix="/api", tags=["Send Email"])



@app.get("/")
def root():
    return {"message": "Oraaq Backend is Running!"}

# UpdateMerchantProfile