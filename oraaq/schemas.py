from pydantic import BaseModel, EmailStr, conint, condecimal
from typing import List, Optional
from datetime import datetime


class RegisterUserRequest(BaseModel):
    user_name: str
    password: str
    phone: str
    user_type_id: int
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    user_type_id: int





class OrderDetail(BaseModel):
    service_id: int
    quantity: int
    unit_price: int

class GenerateOrderRequest(BaseModel):
    customer_id: int
    order_required_date: str  
    category_id: int
    order_amount: int
    total_amount: int
    radius: int
    order_details: List[OrderDetail]


class PostBidRequest(BaseModel):
    order_id: int
    merchant_id: int
    bid_amount: int
    bid_remarks: str
    bid_expiration: str



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
    phone: str
    provider: str
    role: int  # 2 for Merchant, 3 for Customer


class ChangePasswordRequest(BaseModel):
    user_id: int
    current_password: str
    new_password: str