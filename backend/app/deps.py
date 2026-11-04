import uuid

from fastapi import Depends, Header
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.errors import ApiError
from app.models import Client


def get_client(x_client_id: str = Header(), db: Session = Depends(get_db)) -> Client:
    try:
        client_id = uuid.UUID(x_client_id)
    except ValueError:
        raise ApiError(400, "invalid_client_id", "X-Client-Id must be a valid UUID") from None

    client = db.get(Client, client_id)
    if client is None:
        client = Client(id=client_id)
        db.add(client)
        try:
            db.commit()
        except IntegrityError:
            # Two first-load requests raced to create the same client; the other one won.
            db.rollback()
            client = db.get(Client, client_id)
    return client