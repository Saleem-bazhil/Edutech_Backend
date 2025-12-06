from fastapi import FastAPI
from core.database import Base, engine
from api_routes.chat import router as chat_router 
from core.config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # React dev URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    
api_prefix = settings.API_V1_PREFIX

app.include_router(chat_router,prefix=api_prefix)

@app.get('/')
def Home():
    return {"message":"chat"}