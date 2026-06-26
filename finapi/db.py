"""Connexion a la base SQLite via SQLAlchemy."""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Le fichier .db sera cree dans data/finapi.db
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "finapi.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite + Flask
    echo=False,  # passez a True pour voir les requetes SQL
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db() -> None:
    """Cree les tables si elles n'existent pas encore."""
    from finapi import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
