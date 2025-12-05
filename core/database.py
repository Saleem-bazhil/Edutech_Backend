from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

print("Loaded DB URL:", settings.DATABASE_URL)   

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# IMPORTANT: No @contextmanager for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
