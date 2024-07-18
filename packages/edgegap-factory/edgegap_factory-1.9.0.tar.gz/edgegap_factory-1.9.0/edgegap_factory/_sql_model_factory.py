import datetime
import enum
import typing

from sqlalchemy import TypeDecorator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect
from sqlmodel import Session

from . import _generator as generator
from ._base_factory import BaseFactory, AsyncBaseFactory

T = typing.TypeVar("T")


class SqlModelFactory(typing.Generic[T], BaseFactory[T]):
    __BASE_GENERATORS: typing.Dict[
        typing.Union[type, None], generator.AbstractValueGenerator
    ] = {
        str: generator.StringGenerator(),
        int: generator.IntegerGenerator(),
        float: generator.FloatGenerator(),
        datetime.datetime: generator.DatetimeGenerator(),
        bool: generator.BooleanGenerator(),
        None: generator.NoneGenerator(),
        dict: generator.DictGenerator(),
    }

    def __init__(self, session: Session | None, *, auto_commit: bool):
        self.__session = session
        self.__auto_commit = auto_commit

    def create(self, model: T):
        return self.__create(model, self.__auto_commit)

    def __create(self, model: T, commit: bool) -> T:
        inspected_model = inspect(model.__class__)
        relations = inspected_model.relationships.items()
        columns = list(inspected_model.columns)
        model = self.__create_relation(model, relations)
        model = self.__create_columns(model, columns)

        if self.__session is not None:
            self.__session.add(model)

        if self.__session is not None and commit:
            self.__session.commit()

        return model

    def __create_relation(self, model: T, relations) -> T:
        for relation_name, relation_property in filter(
            lambda v: not v[1].uselist, relations
        ):
            local_column = [c for c in relation_property.local_columns][0]

            should_create = all(
                [
                    not local_column.nullable,
                    getattr(model, local_column.name) is None,
                ],
            )

            if should_create:
                base_model = (
                    getattr(model, relation_name) or relation_property.mapper.class_()
                )
                constructed_model = self.__create(base_model, commit=False)
                setattr(model, relation_name, constructed_model)

        return model

    def __create_columns(self, model: T, columns) -> T:
        for column in columns:
            if not column.nullable and getattr(model, column.name) is None:
                # This column type hack is needed because of the way TypeDecorator are designed in SqlAlchemy.
                # E.G. AutoString form SqlModel is a SqlAlchemy String however it does not inherit from it. It inherits
                # from TypeDecorator. This is why we need to check if the column type is a TypeDecorator and if it is
                # get property called impl which is the actual SqlAlchemy type. This is needed to get the python type
                # of the column.
                if isinstance(column.type, TypeDecorator):
                    column_type = column.type.impl.python_type
                else:
                    column_type = column.type.python_type
                value = self.__get_value(column_type)
                setattr(model, column.name, value)

        return model

    def __get_value(self, column_type) -> typing.Any:
        if issubclass(column_type, enum.Enum):
            generator_instance = generator.EnumGenerator(column_type)
        else:
            generator_instance = self.__BASE_GENERATORS.get(column_type)

        if generator_instance is None:
            raise NotImplementedError(f"Generator for {column_type} is not implemented")

        return generator_instance.next()


class AsyncSqlModelFactory(typing.Generic[T], AsyncBaseFactory[T]):
    __BASE_GENERATORS: typing.Dict[
        typing.Union[type, None], generator.AbstractValueGenerator
    ] = {
        str: generator.StringGenerator(),
        int: generator.IntegerGenerator(),
        float: generator.FloatGenerator(),
        datetime.datetime: generator.DatetimeGenerator(),
        bool: generator.BooleanGenerator(),
        None: generator.NoneGenerator(),
        dict: generator.DictGenerator(),
    }

    def __init__(self, session: AsyncSession | None, *, auto_commit: bool):
        self.__session = session
        self.__auto_commit = auto_commit

    async def create(self, model: T):
        return await self.__create(model, self.__auto_commit)

    async def __create(self, model: T, commit: bool) -> T:
        inspected_model = inspect(model.__class__)
        relations = inspected_model.relationships.items()
        columns = list(inspected_model.columns)
        model = await self.__create_relation(model, relations)
        model = self.__create_columns(model, columns)

        if self.__session is not None:
            self.__session.add(model)

        if self.__session is not None and commit:
            await self.__session.commit()

        return model

    async def __create_relation(self, model: T, relations) -> T:
        for relation_name, relation_property in filter(
            lambda v: not v[1].uselist, relations
        ):
            local_column = [c for c in relation_property.local_columns][0]

            should_create = all(
                [
                    not local_column.nullable,
                    getattr(model, local_column.name) is None,
                ],
            )

            if should_create:
                base_model = (
                    getattr(model, relation_name) or relation_property.mapper.class_()
                )
                constructed_model = await self.__create(base_model, commit=False)
                setattr(model, relation_name, constructed_model)

        return model

    def __create_columns(self, model: T, columns) -> T:
        for column in columns:
            if not column.nullable and getattr(model, column.name) is None:
                # This column type hack is needed because of the way TypeDecorator are designed in SqlAlchemy.
                # E.G. AutoString form SqlModel is a SqlAlchemy String however it does not inherit from it. It inherits
                # from TypeDecorator. This is why we need to check if the column type is a TypeDecorator and if it is
                # get property called impl which is the actual SqlAlchemy type. This is needed to get the python type
                # of the column.
                if isinstance(column.type, TypeDecorator):
                    column_type = column.type.impl.python_type
                else:
                    column_type = column.type.python_type
                value = self.__get_value(column_type)
                setattr(model, column.name, value)

        return model

    def __get_value(self, column_type) -> typing.Any:
        if issubclass(column_type, enum.Enum):
            generator_instance = generator.EnumGenerator(column_type)
        else:
            generator_instance = self.__BASE_GENERATORS.get(column_type)

        if generator_instance is None:
            raise NotImplementedError(f"Generator for {column_type} is not implemented")

        return generator_instance.next()
