from fastapi import FastAPI
from core.database import Base, engine
from api_routes.chat import router as chat_router
from core.config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://your-frontend-domain.com",
    "https://edutech-frontend-inky.vercel.app",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    
api_prefix = settings.API_V1_PREFIX

app.include_router(chat_router, prefix=api_prefix)

@app.get("/")
def home():
    return {"message": "chat"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=6001, reload=True)

