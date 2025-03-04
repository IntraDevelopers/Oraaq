from fastapi import FastAPI
from routes import users, auth, orders, requests, bids, service_requests, get_applied_merchant_work_order, GetAllNewRequestForMerchant, offers, work_orders, ratings, customer, categories, service

app = FastAPI(title="Oraaq Marketplace API", version="1.0.0")

# Register routes
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(orders.router, prefix="/api", tags=["Orders"])
app.include_router(requests.router, prefix="/api", tags=["Requests"])
app.include_router(bids.router, prefix="/api", tags=["Bids"])
app.include_router(service_requests.router, prefix="/api", tags=["Service Requests"])
app.include_router(get_applied_merchant_work_order.router, prefix="/api", tags=["WorkOrders"])
app.include_router(GetAllNewRequestForMerchant.router, prefix="/api", tags=["Merchant Requests"])
app.include_router(offers.router, prefix="/api", tags=["Offers"])
app.include_router(work_orders.router, prefix="/api", tags=["Work Orders"])
app.include_router(ratings.router, prefix="/api", tags=["Ratings"])
# app.include_router(fetch_offers_for_request.router, prefix="/api", tags=["fetch_offers_for_request"])
app.include_router(customer.router, prefix="/api", tags=["Customer"])
app.include_router(categories.router, prefix="/api", tags=["Categories"])
app.include_router(service.router, prefix="/api", tags=["Service Tree"])
@app.get("/")
def root():
    return {"message": "Oraaq Backend is Running!"}
