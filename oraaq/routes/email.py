import smtplib
import mysql.connector
from email.mime.text import MIMEText
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from database import get_db_connection  # Ensure this function returns a valid MySQL connection

router = APIRouter()

# SMTP Configuration
SMTP_HOST = "pro.turbo-smtp.com"
SMTP_PORT = 465
FROM_EMAIL = "no-reply@oraaq.com"
MAIL_PASS = "C7u4XU2XAna5QLA"  # Replace with actual password



# Email Sending Function
def send_email(to_mail, user_name, otp_code):
    try:
        subject = "🔒 Oraaq OTP Code"
        body = f"""\
Dear {user_name},

Your One-Time Password (OTP) for Oraaq is: {otp_code}.

This code is valid for 5 minutes. Please do not share it with anyone for security reasons.

If you did not request this code, please ignore this message.

Thank you,  
Oraaq Team
"""
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = to_mail

        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(FROM_EMAIL, MAIL_PASS)
            server.sendmail(FROM_EMAIL, to_mail, msg.as_string())

        return True
    except Exception as e:
        return str(e)


# Request Model
class ForgotPasswordRequest(BaseModel):
    email: str


# @router.post("/forget-password")
# def forget_password(request: ForgotPasswordRequest):
#     try:
#         conn = get_db_connection()   
#         cursor = conn.cursor(dictionary=True)  # <-- Use dictionary=True for column names

#         # Call the stored procedure (no OUT params)
#         cursor.callproc("forget_password3", [request.email])

#         # Fetch the result
#         otp_code = None
#         email = None
#         phone = None
#         username = None

#         for result in cursor.stored_results():
#             data = result.fetchone()
#             if data:
#                 otp_code = data.get("otp")
#                 email = data.get("email")
#                 phone = data.get("phone")
#                 username = data.get("username")

#         conn.commit()
#         cursor.close()
#         conn.close()

#         if not otp_code or not email:
#             raise HTTPException(status_code=404, detail="User not found or OTP not generated.")

#         # Send the OTP email
#         email_status = send_email(email, username, otp_code)
#         if email_status is not True:
#             raise HTTPException(status_code=500, detail=f"Email sending failed: {email_status}")

#         return {
#             "status": "success",
#             "message": "OTP sent successfully",
#             "data": {
#                 "OTP": otp_code,
#                 "Email": email,
#                 "Phone": phone
#             }
#         }

#     except mysql.connector.Error as err:
#         raise HTTPException(status_code=500, detail=f"Database error: {str(err)}")




from fastapi import BackgroundTasks

@router.post("/forget-password")
def forget_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    try:
        conn = get_db_connection()   
        cursor = conn.cursor(dictionary=True)  # <-- Use dictionary=True for column names

        # Call the stored procedure (no OUT params)
        cursor.callproc("forget_password3", [request.email])

        # Fetch the result
        otp_code = None
        email = None
        phone = None
        username = None

        for result in cursor.stored_results():
            data = result.fetchone()
            if data:
                otp_code = data.get("otp")
                email = data.get("email")
                phone = data.get("phone")
                username = data.get("username")

        conn.commit()
        cursor.close()
        conn.close()

        if not otp_code or not email:
            raise HTTPException(status_code=404, detail="User not found or OTP not generated.")

        # Send the OTP email
        # email_status = send_email(email, username, otp_code)
        # if email_status is not True:
        #     raise HTTPException(status_code=500, detail=f"Email sending failed: {email_status}")

        background_tasks.add_task(send_email, email, username, otp_code)
        
        return {
            "status": "success",
            "message": "OTP sent successfully",
            "data": {
                "OTP": otp_code,
                "Email": email,
                "Phone": phone
            }
        }

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {str(err)}")
