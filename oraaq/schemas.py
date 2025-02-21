from pydantic import BaseModel, EmailStr, constr, Field

# Define a Pydantic model for request validation
class RegisterUserRequest(BaseModel):
    user_name: str = Field(..., min_length=1, description="Username is required")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    phone: str = Field(..., min_length=11, max_length=11, description="Phone number must be 11 digits")
    user_type_id: int = Field(..., description="User type ID is required")
    email: EmailStr = Field(..., description="Valid email is required")