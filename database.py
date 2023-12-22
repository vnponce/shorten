import databases
import sqlalchemy
from config import config

# all database structure
metadata = sqlalchemy.MetaData()

url_table = sqlalchemy.Table(
    "urls",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("url", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("short_code", sqlalchemy.String, nullable=False)
)

# to connect to sqlalchemy
engine = sqlalchemy.create_engine(
    config.DATABASE_URL,
    # This is only for sqlite database
    connect_args={"check_same_thread": False}
)

# create the tables with the correct structure
metadata.create_all(engine)

# the instance to interact with the database
database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK
)
