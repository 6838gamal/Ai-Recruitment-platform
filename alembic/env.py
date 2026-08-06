"""Alembic environment configuration."""
from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config, pool

from alembic import context

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all models so Alembic can detect them
from app.database import Base  # noqa: E402
from app.modules.accounts import models as accounts_models  # noqa: F401, E402
from app.modules.companies import models as companies_models  # noqa: F401, E402
from app.modules.users import models as users_models  # noqa: F401, E402
from app.modules.jobs import models as jobs_models  # noqa: F401, E402
from app.modules.candidates import models as candidates_models  # noqa: F401, E402
from app.modules.ats import models as ats_models  # noqa: F401, E402
from app.modules.interviews import models as interviews_models  # noqa: F401, E402
from app.modules.notifications import models as notifications_models  # noqa: F401, E402
from app.modules.ai_matching import models as ai_models  # noqa: F401, E402
from app.modules.files import models as files_models  # noqa: F401, E402
from app.modules.audit import models as audit_models  # noqa: F401, E402
from app.modules.crm import models as crm_models  # noqa: F401, E402
from app.modules.billing import models as billing_models  # noqa: F401, E402
from app.modules.settings import models as settings_models  # noqa: F401, E402

target_metadata = Base.metadata


def get_url() -> str:
    """Get database URL from environment."""
    from app.config import settings
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
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


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
