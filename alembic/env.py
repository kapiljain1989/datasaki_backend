from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Import the Base metadata from your models
from app.db.database import Base  # Ensure this imports your Base metadata
from app.models import user  # Import all models so Alembic detects them


# Alembic Config
config = context.config
fileConfig(config.config_file_name)

# Set Database URL from .env
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Provide Alembic with the metadata of your models
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()
    print("Tables found in metadata:", target_metadata.tables.keys())
run_migrations_online()
