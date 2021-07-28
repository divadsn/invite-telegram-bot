from sqlalchemy import Column, Integer, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Invite(Base):

    __tablename__ = "invites"

    id = Column(Integer, primary_key=True, nullable=False)
    chat_id = Column(Integer, nullable=False)
    invite_link = Column(Text, unique=True, nullable=False)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    invitee = Column(Integer)
    joined_at = Column(DateTime)
