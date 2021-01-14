from sqlalchemy import Column, Integer, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Link(Base):
    __tablename__ = 'link'

    id = Column(Integer, primary_key = True)
    wows_user_id = Column(BigInteger, nullable = False, unique = True)
    discord_user_id = Column(BigInteger, nullable = False, unique = True)
