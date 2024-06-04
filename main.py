from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from user_authentication import auth_router, get_current_user

# Initialize FastAPI app
app = FastAPI()

# Add middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router, prefix="/auth")

@app.get("/")
async def read_root(current_user: str = Depends(get_current_user)):
    return {"message": f"Welcome, {current_user.username}!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
