from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import items, claims, auth
from app.database import create_db_and_tables

app = FastAPI(title="TrackMate API", version="1.0")

# CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Mount static folder for serving uploaded images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routes
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(claims.router)
