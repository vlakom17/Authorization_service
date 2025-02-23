from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.database.database import Base
from app.models.models import User, LoginHistory

fileConfig(context.config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = context.config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    config = context.config
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

