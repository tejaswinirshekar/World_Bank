from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///./countries.db"  # or use DuckDB
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session