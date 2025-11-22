"""
Database configuration and session management.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
if "sqlite" in settings.DATABASE_URL:
    # Disable foreign key constraints for SQLite to avoid issues with missing tables
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# For SQLite, disable foreign key enforcement at connection level
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Disable foreign key constraints for SQLite."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.close()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Database session dependency for FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    """
    try:
        # Import all models here so they are registered
        from app.models import customer, order, menu  # noqa
        
        Base.metadata.create_all(bind=engine)
        
        # Create bon_teller table if it doesn't exist (not in models, but needed)
        from sqlalchemy import text, inspect
        with engine.connect() as conn:
            # Create bon_teller table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS bon_teller (
                    jaar INTEGER NOT NULL,
                    dag INTEGER NOT NULL,
                    laatste_nummer INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (jaar, dag)
                )
            """))
            
            # Check if bestellingen table exists and add missing columns
            inspector = inspect(engine)
            if 'bestellingen' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('bestellingen')]
                
                # Add status column if it doesn't exist
                if 'status' not in columns:
                    try:
                        conn.execute(text("""
                            ALTER TABLE bestellingen ADD COLUMN status TEXT DEFAULT 'Nieuw'
                        """))
                        # Update existing rows to have default status
                        conn.execute(text("""
                            UPDATE bestellingen SET status = 'Nieuw' WHERE status IS NULL
                        """))
                        logger.info("Added status column to bestellingen table")
                    except Exception as e:
                        logger.warning(f"Could not add status column: {e}")
                
                # Add betaalmethode column if it doesn't exist
                if 'betaalmethode' not in columns:
                    try:
                        conn.execute(text("""
                            ALTER TABLE bestellingen ADD COLUMN betaalmethode TEXT DEFAULT 'cash'
                        """))
                        logger.info("Added betaalmethode column to bestellingen table")
                    except Exception as e:
                        logger.warning(f"Could not add betaalmethode column: {e}")
                
                # Add afstand_km column if it doesn't exist
                if 'afstand_km' not in columns:
                    try:
                        conn.execute(text("""
                            ALTER TABLE bestellingen ADD COLUMN afstand_km REAL
                        """))
                        logger.info("Added afstand_km column to bestellingen table")
                    except Exception as e:
                        logger.warning(f"Could not add afstand_km column: {e}")
                
                # Add online_bestelling column if it doesn't exist
                if 'online_bestelling' not in columns:
                    try:
                        conn.execute(text("""
                            ALTER TABLE bestellingen ADD COLUMN online_bestelling INTEGER DEFAULT 0
                        """))
                        logger.info("Added online_bestelling column to bestellingen table")
                    except Exception as e:
                        logger.warning(f"Could not add online_bestelling column: {e}")
                
                # Add email and password_hash columns to klanten table if they don't exist
                if 'klanten' in inspector.get_table_names():
                    klanten_columns = [col['name'] for col in inspector.get_columns('klanten')]
                    
                    if 'email' not in klanten_columns:
                        try:
                            conn.execute(text("""
                                ALTER TABLE klanten ADD COLUMN email TEXT
                            """))
                            logger.info("Added email column to klanten table")
                        except Exception as e:
                            logger.warning(f"Could not add email column: {e}")
                    
                    if 'password_hash' not in klanten_columns:
                        try:
                            conn.execute(text("""
                                ALTER TABLE klanten ADD COLUMN password_hash TEXT
                            """))
                            logger.info("Added password_hash column to klanten table")
                        except Exception as e:
                            logger.warning(f"Could not add password_hash column: {e}")
                    
                    if 'email_verified' not in klanten_columns:
                        try:
                            conn.execute(text("""
                                ALTER TABLE klanten ADD COLUMN email_verified INTEGER DEFAULT 0 NOT NULL
                            """))
                            logger.info("Added email_verified column to klanten table")
                        except Exception as e:
                            logger.warning(f"Could not add email_verified column: {e}")
                    
                    if 'verification_token' not in klanten_columns:
                        try:
                            conn.execute(text("""
                                ALTER TABLE klanten ADD COLUMN verification_token TEXT
                            """))
                            logger.info("Added verification_token column to klanten table")
                        except Exception as e:
                            logger.warning(f"Could not add verification_token column: {e}")
                    
                    if 'verification_token_expires' not in klanten_columns:
                        try:
                            conn.execute(text("""
                                ALTER TABLE klanten ADD COLUMN verification_token_expires TEXT
                            """))
                            logger.info("Added verification_token_expires column to klanten table")
                        except Exception as e:
                            logger.warning(f"Could not add verification_token_expires column: {e}")
                
                # Add status_updated_at column if it doesn't exist
                if 'status_updated_at' not in columns:
                    try:
                        conn.execute(text("""
                            ALTER TABLE bestellingen ADD COLUMN status_updated_at DATETIME
                        """))
                        logger.info("Added status_updated_at column to bestellingen table")
                    except Exception as e:
                        logger.warning(f"Could not add status_updated_at column: {e}")
                
                # Check if koerier_id has foreign key constraint and remove it if needed
                # SQLite doesn't support DROP CONSTRAINT, so we need to recreate the table
                try:
                    fk_list = conn.execute(text("PRAGMA foreign_key_list(bestellingen)")).fetchall()
                    has_koerier_fk = any(fk[2] == 'koeriers' for fk in fk_list)
                    
                    if has_koerier_fk:
                        logger.warning("Foreign key constraint on koerier_id exists but koeriers table may not exist. "
                                     "This may cause issues. Consider recreating the table without the constraint.")
                except Exception as e:
                    logger.warning(f"Could not check foreign keys: {e}")
            
            # Check if bestelregels table exists and add missing columns
            if 'bestelregels' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('bestelregels')]
                
                # Add extras column if it doesn't exist
                if 'extras' not in columns:
                    try:
                        conn.execute(text("""
                            ALTER TABLE bestelregels ADD COLUMN extras TEXT
                        """))
                        logger.info("Added extras column to bestelregels table")
                    except Exception as e:
                        logger.warning(f"Could not add extras column: {e}")
            
            conn.commit()
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

