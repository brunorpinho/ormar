import datetime

import databases
import ormar
import pytest
import sqlalchemy

from tests.settings import DATABASE_URL

metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)


class TableBase(ormar.Model):
    ormar_config = ormar.OrmarConfig(
        abstract=True,
        metadata=metadata,
        database=database,
    )

    id: int = ormar.Integer(primary_key=True)
    created_by: str = ormar.String(max_length=20, default="test")
    created_at: datetime.datetime = ormar.DateTime(
        timezone=True, default=datetime.datetime.now
    )
    last_modified_by: str = ormar.String(max_length=20, nullable=True)
    last_modified_at: datetime.datetime = ormar.DateTime(timezone=True, nullable=True)


class NationBase(ormar.Model):
    ormar_config = ormar.OrmarConfig(abstract=True)

    name: str = ormar.String(max_length=50)
    alpha2_code: str = ormar.String(max_length=2)
    region: str = ormar.String(max_length=30)
    subregion: str = ormar.String(max_length=30)


class Nation(NationBase, TableBase):
    ormar_config = ormar.OrmarConfig()


@pytest.fixture(autouse=True, scope="module")
def create_test_database():
    engine = sqlalchemy.create_engine(DATABASE_URL)
    metadata.drop_all(engine)
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)


@pytest.mark.asyncio
async def test_model_is_not_abstract_by_default():
    async with database:
        sweden = await Nation(
            name="Sweden", alpha2_code="SE", region="Europe", subregion="Scandinavia"
        ).save()
        assert sweden.id is not None
