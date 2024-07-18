from pathlib import Path

from alembic import command
from alembic.config import Config as AlembicConfig
from loguru import logger
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from plutous.config import config

url = URL.create(drivername="postgresql+psycopg2", **config.db.dict())
engine = create_engine(url)

Session = sessionmaker(bind=engine)


def _get_alembic_config(diretory: Path):
    """
    get the decube/alembic.ini config file
    """
    migration = diretory.joinpath("migrations")
    ab_config = AlembicConfig(str(diretory.joinpath("alembic.ini")))
    ab_config.set_main_option("script_location", str(migration))
    ab_config.set_main_option("sqlalchemy.url", url.render_as_string(False))

    return ab_config


def init(schema: str, metadata: MetaData, directory: Path):
    sql = f"""
        SELECT EXISTS(
            SELECT *
            FROM information_schema.tables
            WHERE table_schema = '{schema}'
            LIMIT 1
        )
    """
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        exists = conn.execute(text(sql)).one()[0]
        if exists:
            logger.warning(f"{schema} schema already contains table, Skipping...")
            return

        metadata.create_all(conn)
        conn.commit()

    ab_config = _get_alembic_config(directory)
    command.stamp(ab_config, "head")


def revision(directory: Path, msg: str, **kwargs):
    alembic_cfg = _get_alembic_config(directory)
    command.revision(alembic_cfg, message=msg, autogenerate=True, **kwargs)


def upgrade(directory: Path, revision: str = "head", **kwargs):
    alembic_cfg = _get_alembic_config(directory)
    command.upgrade(alembic_cfg, revision, **kwargs)


def downgrade(directory: Path, revision: str, **kwargs):
    alembic_cfg = _get_alembic_config(directory)
    command.downgrade(alembic_cfg, revision, **kwargs)


def reset(schema: str):
    logger.info(f'Resetting schema "{schema}"...')
    reply = input(
        f"Verify you are connected to the correct database ({engine.url.render_as_string()})![y/N]"
    )
    if reply.lower() != "y":
        logger.info("Aborting...")
        return

    sql = f"""
    DROP SCHEMA "{schema}" CASCADE;
    """

    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
