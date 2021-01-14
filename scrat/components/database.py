from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Database:

    def __init__(self, url: str):
        self._url = url

    @contextmanager
    def session_scope(self, autocommit = True):
        """Provide a transactional scope around a series of operations."""
        session = sessionmaker(bind = create_engine(self._url))()
        try:
            yield session
            if autocommit:
                session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
