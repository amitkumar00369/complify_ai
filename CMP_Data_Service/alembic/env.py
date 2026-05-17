from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from core.config import settings
from core.database import Base

import app.models


# ===================================
# ALEMBIC CONFIG
# ===================================
config = context.config


# ===================================
# LOGGING
# ===================================
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ===================================
# DATABASE URL (SYNC)
# ===================================
DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST1}:"
    f"{settings.DB_PORT}/"
    f"{settings.DB_NAME}"
)

print("Alembic DB URL:", DATABASE_URL)

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL
)


# ===================================
# METADATA
# ===================================
target_metadata = Base.metadata


# ===================================
# OFFLINE MODE
# ===================================
def run_migrations_offline():

    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ===================================
# ONLINE MODE
# ===================================
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
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ===================================
# RUN
# ===================================
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()