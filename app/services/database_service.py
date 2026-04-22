import logfire
from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from google.cloud.sql.connector import Connector, IPTypes
from app.config import DB_USER, DB_PASS, DB_NAME, DB_CONNECTION_NAME

# Initialize Cloud SQL Connector
connector = Connector()

def getconn():
    conn = connector.connect(
        DB_CONNECTION_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME,
        ip_type=IPTypes.PUBLIC # Change to PRIVATE if using VPC
    )
    return conn

# SQLAlchemy Setup
Base = declarative_base()

class QueryLog(Base):
    __tablename__ = "query_logs"
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    query = Column(Text)
    reasoning = Column(Text)
    answer = Column(Text)
    sources = Column(JSON)
    latency = Column(Float)

# Create Engine
# Note: In a production Cloud Run environment, you would use the connector
try:
    engine = create_engine("postgresql+pg8000://", creator=getconn)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # Create tables
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"⚠️ Database Connection Failed: {e}")
    SessionLocal = None

def log_query_to_db(query_id, query_text, reasoning, answer, sources, latency):
    """Logs the full agent interaction to Postgres."""
    if not SessionLocal:
        return
    
    try:
        db = SessionLocal()
        new_log = QueryLog(
            id=query_id,
            query=query_text,
            reasoning=reasoning,
            answer=answer,
            sources=sources,
            latency=latency
        )
        db.add(new_log)
        db.commit()
        db.close()
        print(f"✅ Logged query {query_id} to Postgres")
    except Exception as e:
        print(f"Database Log Error: {e}")
