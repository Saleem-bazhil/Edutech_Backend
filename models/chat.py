from core.database import Base
from sqlalchemy import Column,Integer,String,Text,ForeignKey,DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class ChatMessage(Base):
    __tablename__ = "chat messages"
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    role = Column(String,default="user")
    content = Column(Text)
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    user = relationship("User")
    