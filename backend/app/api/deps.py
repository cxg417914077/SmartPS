from typing import Annotated, Generator, Optional
from sqlmodel import Session
from fastapi import Depends
from backend.app.core.db import engine


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
