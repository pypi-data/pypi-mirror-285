from datetime import datetime
from sqlalchemy import and_, create_engine, exc, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()


def get_engine(database: str, echo: bool = False):
    """
    Create DB Engine
    """
    engine = create_engine(database, echo=echo)

    return engine


def get_session(engine):
    """
    Create DB Session
    """
    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )

    return session


def create_tables(engine):
    """
    Create Tables
    """
    Base.metadata.create_all(bind=engine)


def upsert(session, model, unique=False, **kwargs) -> int:
    """
    Insert data if it does not exist, update existing data if any.

    Parameters:
    session (Session): SQLAlchemy session object.
    model: SQLAlchemy model class.
    kwargs: Column values for the model.
    unique (bool): If True, only unique combinations of columns (excluding id, created_at, updated_at) are registered.

    Returns:
    int: ID of the upserted instance.
    """
    table = model.__table__
    primary_key = list(table.primary_key.columns.keys())[0]

    if unique:
        # Exclude id, created_at, updated_at from unique check
        unique_columns = [
            col
            for col in kwargs.keys()
            if col not in ["id", "created_at", "updated_at"]
        ]
        filters = [getattr(model, col) == kwargs[col] for col in unique_columns]
        instance = session.query(model).filter(and_(*filters)).first()
    else:
        instance = (
            session.query(model).filter_by(**{primary_key: kwargs[primary_key]}).first()
        )

    if instance:
        # Update updated_at when changes are made
        updated = False
        changes = []
        for key, value in kwargs.items():
            old_value = getattr(instance, key)

            # Ensure both old_value and value are naive datetime objects (without timezone)
            if isinstance(old_value, datetime) and old_value.tzinfo is not None:
                old_value = old_value.replace(tzinfo=None)
            if isinstance(value, datetime) and value.tzinfo is not None:
                value = value.replace(tzinfo=None)

            if old_value != value:
                setattr(instance, key, value)
                changes.append((key, old_value, value))
                updated = True
        if updated:
            instance.updated_at = datetime.now()
            session.add(instance)
    else:
        # Insert new instance
        instance = model(**kwargs)
        session.add(instance)

    try:
        session.commit()
        return instance.id
    except exc.SQLAlchemyError as e:
        session.rollback()
        print(f"Error occurred: {e}")
        print(model)
        print(instance)
        # Handle the error gracefully, optionally log it
        # You can choose to raise an exception or handle it as per your application's needs
    finally:
        session.close()


def get_random_records(session, model, limit: int):
    """
    Fetches a specified number of random records from the database.

    Parameters:
        session (Session): SQLAlchemy session object.
        model: SQLAlchemy model class.
        limit (int): The number of random records to fetch.

    Returns:
        list: A list of random records from the database.

    """
    # Fetch random records
    random_records = session.query(model).order_by(func.random()).limit(limit).all()

    # Close the session
    session.close()

    return random_records
