from sqlmodel import create_engine, SQLModel, Session


DATABASE_URL = "sqlite:///calitech.db"
engine = create_engine(DATABASE_URL)

def get_db():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()

def init_database():
    SQLModel.metadata.create_all(bind=engine)