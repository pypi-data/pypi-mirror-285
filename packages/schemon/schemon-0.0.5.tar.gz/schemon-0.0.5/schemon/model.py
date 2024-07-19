import os
from sqlalchemy import (
    create_engine,
    text,
    Column,
    String,
    Integer,
    Boolean,
    PrimaryKeyConstraint,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from schemon.config import config
from schemon.env import loadenv

loadenv()

Base = declarative_base()
engine = create_engine(
    config.database_uri,
    echo=config.show_sql,
    connect_args=config.connect_args,
)
Session = sessionmaker(bind=engine)


def has_pk_support(*args, **kwargs):
    """use ddl_if make a fake primary key constraint to support hive and pass the sqlalchemy orm check"""
    if os.getenv("DB_TYPE") == "mysql" or os.getenv("DB_TYPE") == "sqlite3":
        return True
    return False


class MyBase:
    def __repr__(self):
        """generic repr"""
        _d = {k: v for k, v in self.__dict__.items() if k != "_sa_instance_state"}
        return f"{self.__class__.__name__}({_d})"


class RegistrySchema(MyBase, Base):
    """
    Represents a registry schema.

    Attributes:
        schema_id (str): The ID of the schema.
        env (str): The environment of the schema.
        filename (str): The filename of the schema.
        stage (str): The stage of the schema.
        entity_name (str): The name of the entity.
        entity_description (str): The description of the entity.
        owner_name (str): The name of the owner.
        owner_email (str): The email of the owner.
        platform (str): The platform of the schema.
        format (str): The format of the schema.
        type (str): The type of the schema.
        content (str): The content of the schema.
        version (str): The version of the schema.
        latest (bool): Indicates if the schema is the latest version.
        created_at (int): The timestamp when the schema was created.
    """

    __tablename__ = "registry_schema"
    __table_args__ = (PrimaryKeyConstraint("schema_id").ddl_if(None, has_pk_support),)

    schema_id = Column(String(50))
    env = Column(String(10))
    filename = Column(String(500))
    stage = Column(String(50))
    entity_name = Column(String(50))
    entity_description = Column(String(500))
    owner_name = Column(String(100))
    owner_email = Column(String(100))
    platform = Column(String(100))
    format = Column(String(50))
    type = Column(String(50))
    content = Column(Text)
    version = Column(String(10))
    latest = Column(Boolean)
    created_at = Column(Integer)


class RegistryField(MyBase, Base):
    """
    Represents a field in the registry.

    Attributes:
        field_id (str): The ID of the field.
        schema_id (str): The ID of the schema that the field belongs to.
        name (str): The name of the field.
        type (str): The type of the field.
        required (bool): Indicates if the field is required.
        nullable (bool): Indicates if the field is nullable.
        unique (bool): Indicates if the field is unique.
        key (bool): Indicates if the field is a key.
        pd_default (str): The default value of the field in the Pandas DataFrame.
        default (str): The default value of the field.
        description (str): The description of the field.
        regex (str): The regular expression pattern for the field.
        example (str): An example value for the field.
        created_at (int): The timestamp of when the field was created.
    """

    __tablename__ = "registry_field"
    __table_args__ = (PrimaryKeyConstraint("field_id").ddl_if(None, has_pk_support),)

    field_id = Column(String(50))
    schema_id = Column(String(50))
    name = Column(String(50))
    type = Column(String(50))
    required = Column(Boolean)
    nullable = Column(Boolean)
    unique = Column(Boolean)
    key = Column(Boolean)
    pd_default = Column(String(50))
    default = Column(String(50))
    description = Column(String(500))
    regex = Column(String(500))
    example = Column(String(500))
    created_at = Column(Integer)

    def to_dict(self):
        return {
            "field_id": self.field_id,
            "schema_id": self.schema_id,
            "name": self.name,
            "type": self.type,
            "required": self.required,
            "nullable": self.nullable,
            "unique": self.unique,
            "key": self.key,
            "pd_default": self.pd_default,
            "default": self.default,
            "description": self.description,
            "regex": self.regex,
            "example": self.example,
            "created_at": self.created_at,
        }


def create_all():
    """
    Creates all the tables defined in the metadata using the provided engine.
    If the database URI starts with "hive", it sets the file format of the "registry_schema" and "registry_field" tables to "orc".
    """
    Base.metadata.create_all(engine)
    if config.database_uri.startswith("hive"):
        session = Session()
        for t in ["registry_schema", "registry_field"]:
            session.execute(text(f"alter table {t} set fileformat orc"))
        session.commit()
        session.close()


create_all()

if __name__ == "__main__":
    create_all()
