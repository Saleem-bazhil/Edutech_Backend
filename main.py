from fastapi import FastAPI
from core.database import Base, engine
from api_routes.chat import router as chat_router 
from core.config import settings

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    
api_prefix = settings.API_V1_PREFIX

app.include_router(chat_router,prefix=api_prefix)

@app.get('/')
def Home():
    return {"message":"chat"}