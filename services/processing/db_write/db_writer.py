"""
db_writer.py

Handles insertion of PDF text chunks into a Postgres database using SQLAlchemy.
Includes automatic table creation for idempotent setup.

Author: ResearchAI Team
"""

import os
from sqlalchemy import create_engine, Column, Integer, Text, String, TIMESTAMP
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class Chunk(Base):
    """
    ORM model for the 'chunks' table in the Postgres database.

    :param id: Primary key
    :param source_file: Name of the source PDF file
    :param chunk_index: Index of the chunk within the document
    :param chunk_text: Text content of the chunk
    :param created_at: Timestamp of chunk insertion
    """
    __tablename__ = 'chunks'

    id = Column(Integer, primary_key=True)
    source_file = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

def get_engine():
    """
    Creates and returns a SQLAlchemy engine using environment variables.

    :returns: SQLAlchemy engine instance
    :rtype: sqlalchemy.Engine
    """
    user = os.getenv("POSTGRES_USER", "researchai")
    password = os.getenv("POSTGRES_PASSWORD", "researchai")
    db = os.getenv("APP_DB", "researchai_app")
    host = os.getenv("POSTGRES_HOST", "postgres")  # important: 'postgres' = container name
    port = os.getenv("POSTGRES_PORT", "5432")

    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

def write_chunks_to_db(chunks):
    """
    Writes a list of chunk dictionaries into the Postgres database.

    Automatically creates the `chunks` table if it does not exist.

    :param chunks: List of chunk dictionaries with keys: 'source_file', 'chunk_index', 'chunk_text'
    :type chunks: list[dict]
    """
    engine = get_engine()
    Base.metadata.create_all(engine)  # 👈 Automatically create table if not exists

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for chunk in chunks:
            db_row = Chunk(
                source_file=chunk["source_file"],
                chunk_index=chunk["chunk_index"],
                chunk_text=chunk["chunk_text"]
            )
            session.add(db_row)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()