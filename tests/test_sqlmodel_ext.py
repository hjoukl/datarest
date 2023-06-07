# Adapted from SQLModel PR:
# https://github.com/tiangolo/sqlmodel/pull/43/files#diff-d47aa94b4399636b3bf61c282806410ca16c47e6edb13a2d3ba675f9460e7389
# Tests: https://github.com/watkinsm/sqlmodel/blob/0b2a7962092a1593d22787b58b2bf2501b0c1b93/tests/test_create_model.py#L6
#
# (Copyright Michael Watkins (https://github.com/watkinsm),
#  License: MIT (https://github.com/tiangolo/sqlmodel/blob/main/LICENSE))

import pytest
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine

from datarest._sqlmodel_ext import create_model, ConfigError, Type
from sqlmodel.main import default_registry


@pytest.fixture()
def clear_sqlmodel():
    # Clear the tables in the metadata for the default base model
    SQLModel.metadata.clear()
    # Clear the Models associated with the registry, to avoid warnings
    default_registry.dispose()
    yield
    SQLModel.metadata.clear()
    default_registry.dispose()


def test_create_model(clear_sqlmodel):
    """
    Test dynamic model creation, query, and deletion
    """
    field_definitions = {
        "id": (Optional[int], Field(default=None, primary_key=True)),
        "name": str,
        "secret_name": (str,),  # test 1-tuple
        "age": (Optional[int], None),
    }

    hero = create_model(
        "Hero", 
        **field_definitions, table=True
    )

    hero_1 = hero(**{"name": "Deadpond", "secret_name": "Dive Wilson"}), breakpoint()

    engine = create_engine("sqlite://")

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(hero_1)
        session.commit()
        session.refresh(hero_1)

    with Session(engine) as session:
        query_hero = session.query(hero).first()
        assert query_hero
        assert query_hero.id == hero_1.id
        assert query_hero.name == hero_1.name
        assert query_hero.secret_name == hero_1.secret_name
        assert query_hero.age == hero_1.age

    with Session(engine) as session:
        session.delete(hero_1)
        session.commit()

    with Session(engine) as session:
        query_hero = session.query(hero).first()
        assert not query_hero

@pytest.mark.skip
def test_create_model_1():
    field_definitions_2 = {
        "name": str,
        "age": (int, 0),
        "email": (str, Field(nullable=False)),
    }

    model = create_model("TestModel", **field_definitions_2, table=True), breakpoint()
    #assert isinstance(model, Type[SQLModel])
    assert "name" in model.__annotations__
    assert "age" in model.__annotations__
    assert "email" in model.__annotations__
    assert "name" in model.__dict__
    assert "age" in model.__dict__
    assert "email" in model.__dict__
    assert isinstance(model.__dict__["name"], Field)
    assert isinstance(model.__dict__["age"], Field)
    assert isinstance(model.__dict__["email"], Field)


    with pytest.raises(ConfigError):
        create_model("InvalidModel", **{"_invalid_field": str})

# Testoutput: FAILED test_sqlmodel_ext.py::test_create_model - TypeError: create_model() takes 1 positional argument but 2 were given
