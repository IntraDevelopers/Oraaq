from pydantic import BaseModel, EmailStr

class RegisterUserRequest(BaseModel):
    user_name: str  # No min_length validation
    password: str
    phone: str
    user_type_id: int
    email: EmailStr
