from fastapi import FastAPI
from routes import users

app = FastAPI(title="Oraaq Marketplace API", version="1.0.0")

# Register routes
app.include_router(users.router, prefix="/api", tags=["Users"])

@app.get("/")
def root():
    return {"message": "Oraaq Backend is Running!"}
