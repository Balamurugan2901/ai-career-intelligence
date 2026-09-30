from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings
from backend.utils.logger import logger

# SQLite engine configuration
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    """FastAPI dependency for yielding database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initializes SQLite database tables automatically."""
    try:
        # Import models so Base metadata is populated
        import backend.models.candidate  # noqa: F401
        import backend.models.career     # noqa: F401
        import backend.models.skill      # noqa: F401
        import backend.models.roadmap    # noqa: F401
        import backend.models.interview  # noqa: F401

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise e
