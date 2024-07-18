from __future__ import annotations
from functools import wraps

import time
import os
import json
from sqlalchemy import desc, and_, Table, MetaData, insert
from schemon.common import parse_yaml
from schemon.model import Base, Session, RegistrySchema, RegistryField


from schemon.env import loadenv

loadenv()


def chunk_data(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]


class TransactionEvent:
    """
    Represents a transaction event.

    Attributes:
        AFTER_COMMIT (int): Constant representing the after commit event. Transaction event constants for hooking
    """

    AFTER_COMMIT = 1


def get_latest_registry_schema(session: Session, filters: dict = None) -> RegistrySchema:  # type: ignore
    """
    Retrieve the latest registry schema based on the provided filters.

    Args:
        session (Session): The database session.
        filters (dict, optional): Filters to apply to the query. Defaults to None.

    Returns:
        RegistrySchema: The latest registry schema record that matches the filters.
    """
    query = session.query(RegistrySchema)
    if filters:
        conditions = [
            getattr(RegistrySchema, key) == value for key, value in filters.items()
        ]
        query = query.filter(and_(*conditions))
    record = query.order_by(desc(RegistrySchema.version)).first()
    return record


def get_model_data(my_model: Base, session: Session, filters: dict = None) -> list[Base]:  # type: ignore
    """
    Retrieve model data from the database based on the provided filters.

    Args:
        my_model (Base): The model class to query.
        session (Session): The SQLAlchemy session object.
        filters (dict, optional): A dictionary of filters to apply to the query. Each key-value pair represents a filter condition. Defaults to None.

    Returns:
        list[Base]: A list of model instances that match the provided filters.
    """
    query = session.query(my_model)
    if filters:
        conditions = [getattr(my_model, key) == value for key, value in filters.items()]
        query = query.filter(and_(*conditions))
    records = query.all()
    return records


def get_registry_fields_by_entity(session: Session, entity_name: str, stage: str, env: str) -> list[RegistryField]:  # type: ignore
    """
    Retrieve the registry fields for a given entity, stage, and environment.

    Args:
        session (Session): The database session.
        entity_name (str): The name of the entity.
        stage (str): The stage of the entity.
        env (str): The environment of the entity.

    Returns:
        list[RegistryField]: A list of registry fields.

    """
    rs = get_latest_registry_schema(
        session, {"entity_name": entity_name, "stage": stage, "env": env}
    )
    rfs = []
    if rs:
        rfs = get_model_data(RegistryField, session, {"schema_id": rs.schema_id})
    return rfs


def get_registry_schema_by_entity(session: Session, entity_name: str, stage: str, env: str) -> list[RegistryField]:  # type: ignore
    """
    Retrieves the registry schema for a given entity, stage, and environment.

    Args:
        session (Session): The database session.
        entity_name (str): The name of the entity.
        stage (str): The stage of the schema.
        env (str): The environment of the schema.

    Returns:
        list[RegistryField]: The list of registry fields.

    """
    rs = get_latest_registry_schema(
        session, {"entity_name": entity_name, "stage": stage, "env": env}
    )
    rms = []
    if rs:
        rms = rs
    return rms


import time


def get_new_id() -> str:
    """
    Generate a new ID based on the current timestamp.

    Returns:
        str: The generated ID.
    """
    time.sleep(1e-6)
    return str(int(time.time() * 1e6))


def transactional(func):
    """
    Decorator that provides transactional behavior to a function.

    This decorator wraps the given function in a transactional context. It creates a new session,
    executes the function within that session, commits the changes if successful, and rolls back
    the changes if an exception occurs. It also provides an option to execute additional functions
    after the commit.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.

    Raises:
        Exception: If an exception occurs during the execution of the function.

    Example:
        @transactional
        def save_data(data, session):
            # Perform database operations using the provided session
            ...

        # Usage
        save_data(data)
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()
        try:
            kwargs["session"] = session
            result = func(*args, **kwargs)
            session.commit()
            if isinstance(result, dict):
                for event in (TransactionEvent.AFTER_COMMIT,):
                    if result.get(event):
                        result.get(event)()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    return wrapper


@transactional
def add_registry_schema(filepath: str, new_version: str, session: Session):  # type: ignore
    """
    Adds a new registry schema to the database.

    Args:
        filepath (str): The path to the YAML file containing the schema definition.
        new_version (str): The version of the schema to be added.
        session (Session): The database session object.

    Returns:
        dict: A dictionary containing a callback function to be executed after the transaction is committed.
    """
    parsed = parse_yaml(filepath)
    entity_name = parsed["entity"]["name"]

    schema_to_update = (
        session.query(RegistrySchema)
        .filter(
            RegistrySchema.entity_name == entity_name and RegistrySchema.latest == 1
        )
        .all()
    )
    if schema_to_update is not None:
        for schema in schema_to_update:
            schema.latest = 0
    session.flush()

    content = parsed["_full_content"]
    schema_id = get_new_id()
    registry_schema = RegistrySchema(
        schema_id=schema_id,
        env=os.getenv("ENV"),
        filename=os.path.basename(filepath),
        entity_name=entity_name,
        entity_description=parsed["entity"]["description"],
        stage=parsed["stage"],
        owner_name=parsed["owner"]["name"],
        owner_email=parsed["owner"]["email"],
        platform=parsed["platform"],
        format=parsed["format"],
        type=parsed["type"],
        content=content,
        version=new_version,
        latest=True,
        created_at=int(time.time()),
    )
    session.add(registry_schema)
    session.flush()

    source_fields: dict = parsed["fields"]
    print(entity_name)
    if (
        "transformation_config" in parsed["config"]
        and parsed["config"]["transformation_config"] is not None
        and "append_config" in parsed["config"]["transformation_config"]
    ):
        source_fields.update(parsed["config"]["transformation_config"]["append_config"])

    registry_field_rows = []
    for field_name, item in source_fields.items():
        registry_field_row = RegistryField(
            field_id=get_new_id(),
            schema_id=schema_id,
            name=field_name,
            type=item.get("type"),
            required=item.get("required"),
            nullable=item.get("nullable"),
            unique=item.get("unique"),
            key=item.get("key"),
            pd_default=item.get("pd_default"),
            default=item.get("default"),
            description=item.get("description"),
            regex=json.dumps(item.get("regex")),
            example=json.dumps(item.get("example")),
            created_at=int(time.time()),
        )
        registry_field_rows.append(registry_field_row.to_dict())
        # session.add(registry_field)
        # session.flush()
    metadata = MetaData()
    registry_field_table = Table("registry_field", metadata, autoload_with=session.bind)
    chunk_size = int(os.getenv("BULK_INSERT_CHUNK_SIZE"))
    for chunk in chunk_data(registry_field_rows, chunk_size):
        session.execute(insert(registry_field_table).values(chunk))

    session.flush()
    return {
        TransactionEvent.AFTER_COMMIT: lambda: print(
            f"{filepath} schema and field saved successfully with version {new_version}"
        )
    }
