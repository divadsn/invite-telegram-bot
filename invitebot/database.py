from invitebot import DB_URI

from sqlalchemy import Column, Integer, Text, DateTime, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure a Session class.
Session = sessionmaker()

# Create an engine which the Session will use for connections.
engine = create_engine(DB_URI)

# Create a configured Session class.
Session.configure(bind=engine)

# Create a Session
session = Session()

# Create a base for the models to build upon.
Base = declarative_base()


class Invite(Base):

    __tablename__ = "invites"

    invite_id = Column(Integer, primary_key=True, nullable=False)
    chat_id = Column(Integer, nullable=False)
    link = Column(Text, unique=True, nullable=False)
    from_id = Column(Integer, nullable=False)
    from_name = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    valid_until = Column(DateTime, nullable=False)
    invitee_id = Column(Integer)
    invitee_name = Column(Text)
    joined_at = Column(DateTime)
