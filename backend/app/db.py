from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

is_sqlite = settings.database_url.startswith("sqlite")

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    pool_pre_ping=True
)

if is_sqlite:
    @event.listens_for(engine, "connect")
    def _enable_sqlite_fks(dbapi_conn, _):
        curr = dbapi_conn.cursor()
        curr.execute("PRAGMA foreign_keys=ON")
        curr.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: one session per request, always closed."""
    with SessionLocal() as db:
        yield db


