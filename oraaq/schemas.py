from pydantic import BaseModel, EmailStr, conint, condecimal
from typing import List, Optional
from datetime import datetime


class RegisterUserRequest(BaseModel):
    user_name: str
    password: str
    phone: str
    user_type_id: int
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: Optional[str] = None
    password: str
    role: int


class OrderDetail(BaseModel):
    service_id: int
    quantity: int
    unit_price: int

# class GenerateOrderRequest(BaseModel):
#     customer_id: int
#     order_required_date: str  
#     category_id: int
#     customer_amount: int
#     total_amount: int
#     radius: int
#     latitude: float
#     longitude: float
#     order_detail: List[OrderDetail]



class OrderMaster(BaseModel):
    customer_id: int
    order_required_date: str  
    category_id: int
    customer_amount: float
    total_amount: float
    radius: float
    latitude: float
    longitude: float  

class OrderDetail(BaseModel):
    service_id: int
    unit_price: float

class GenerateOrderRequest(BaseModel):
    order_master: OrderMaster
    order_detail: List[OrderDetail]




class PostBidRequest(BaseModel):
    order_id: int
    merchant_id: int
    bid_amount: int
    bid_remarks: Optional[str] = None 
    bid_expiration: Optional[str] = None 



class AcceptRejectOfferRequest(BaseModel):
    offer_id: int
    bid_status: int  # Only allows 2 (Accept) or 3 (Reject)


from pydantic import BaseModel, conint

class CancelOrderRequest(BaseModel):
    bidding_id: int
    merchant_id: int
    order_status_id: int # Only allows 2 (Cancelled) or 3 (Completed)



class AddOrderRatingRequest(BaseModel):
    order_id: int
    rating_for_user_type: int # 2 for Merchant, 3 for Customer
    merchant_id: Optional[int] = None  # Only required if rating a merchant
    customer_id: Optional[int] = None  # Only required if rating a customer
    rating_by: int  # User who is rating
    rating: float  # Rating value (1-5)
    review: Optional[str] = None  # Optional review, max 500 chars


class SocialLoginRequest(BaseModel):
    user_name: str
    email: str
    social_id: str
    phone: Optional[str] = None 
    provider: str
    role: int  # 2 for Merchant, 3 for Customer


class ChangePasswordRequest(BaseModel):
    user_id: int
    current_password: str
    new_password: str


# Request body model
# class UpdateMerchantProfileRequest(BaseModel):
#     merchant_id: int
#     merchant_name: str
#     merchant_number: str
#     cnic: str
#     email: str
#     business_name: str
#     latitude: float
#     longitude: float
#     opening_time: str
#     closing_time: str
#     service_type: int
#     holidays: str