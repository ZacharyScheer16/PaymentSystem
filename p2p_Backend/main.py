from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PaymentProject API", version="1.0.0")

# Add this block before your routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # This specifically authorizes your React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "PaymentProject backend is running"}

# ... rest of your code