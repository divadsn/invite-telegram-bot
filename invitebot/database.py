from datetime import datetime
from invitebot import DB_URI

from sqlalchemy import Column, Integer, Text, DateTime, func, create_engine, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, sessionmaker

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
    create_date = Column(DateTime, nullable=False, server_default=func.now())
    expire_date = Column(DateTime, nullable=False)
    invitee_id = Column(Integer)
    invitee_name = Column(Text)
    joined_at = Column(DateTime)

    def __init__(self, chat_id: int, link: str, from_id: int, from_name: str, create_date: datetime, expire_date: datetime):
        self.chat_id = chat_id
        self.link = link
        self.from_id = from_id
        self.from_name = from_name
        self.create_date = create_date
        self.expire_date = expire_date

    def __repr__(self) -> str:
        return f"<Invite (invite_id='{self.invite_id}', chat_id='{self.chat_id}', link='{self.link}')>"


def query_invites_for_user(chat_id: int, user_id: int) -> Query:
    return session.query(Invite).filter(
        and_(
            Invite.chat_id == chat_id,
            Invite.from_id == user_id,
            Invite.expire_date > func.now(),
            Invite.invitee_id.is_(None)
        )
    ).order_by(Invite.invite_id)


def create_tables() -> None:
    Base.metadata.create_all(engine)
