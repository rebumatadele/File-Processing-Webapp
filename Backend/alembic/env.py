# alembic/env.py

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import all your models here
from app.config.database import Base
from app.settings import settings
from app.models.user import User
from app.models.file import UploadedFile, ProcessedFile
from app.models.prompt import Prompt
from app.models.cache import CachedResult
from app.models.claude_batch import Batch, BatchRequestItem
from app.models.config import ConfigRequest
from app.models.error import ErrorLog
from app.models.processing_status import ProcessingFileStatus
from app.models.processing import ProcessingJob
from app.models.rate_limiter import RateLimiterModel
from app.models.result import ProcessingResult
from app.models.user_config import UserConfig

# Existing Alembic configuration
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Retrieve the DATABASE_URL from environment variables
database_url = settings.database_url


if not database_url:
    raise Exception("DATABASE_URL environment variable not set.")

# Override the sqlalchemy.url from the .ini file at runtime
config.set_main_option("sqlalchemy.url", database_url)

# # Define the include_object function to exclude 'cached_results' table
# def include_object(object, name, type_, reflected, compare_to):
#     if type_ == "table" and name == "cached_results":
#         return False
#     return True


# Update the context.configure calls to remove the include_object parameter
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # include_object=include_object,  # Remove this line
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # include_object=include_object,  # Remove this line
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
