from typing import Iterable

from sqlalchemy.orm import Session as _Session

from plutous.database import Session


def get_session() -> Iterable[_Session]:
    session = Session()
    try:
        yield session
    finally:
        session.close()
