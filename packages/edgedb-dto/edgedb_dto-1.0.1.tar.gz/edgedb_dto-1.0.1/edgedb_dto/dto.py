from dataclasses import asdict
from pydantic.dataclasses import dataclass
from collections import namedtuple
from edgedb import AsyncIOClient, Client
import json


async def async_recurse(executor, attribute):
    """
    Recursively processes attributes asynchronously, handling DTOs, lists, tuples, and namedtuples.

    Args:
        executor: The EdgeDB executor.
        attribute: The attribute to process.

    Returns:
        Processed attribute.
    """
    attribute_type = type(attribute)

    if issubclass(attribute_type, DTO):
        subquery_result = await attribute.run(executor)
        return subquery_result.id if subquery_result else None

    if issubclass(attribute_type, list):
        return [await async_recurse(executor, item) for item in attribute]

    if issubclass(attribute_type, tuple) and hasattr(attribute, "_fields"):
        attribute_factory = namedtuple(attribute_type.__name__, attribute._fields)
        results = []
        for field in attribute._fields:
            tuple_attribute = getattr(attribute, field)
            results.append(await async_recurse(executor, tuple_attribute))
        return attribute_factory(*results)

    if issubclass(attribute_type, tuple):
        return tuple([await async_recurse(executor, item) for item in attribute])

    return attribute


def sync_recurse(executor, attribute):
    """
    Recursively processes attributes synchronously, handling DTOs, lists, and namedtuples.

    Args:
        executor: The EdgeDB executor.
        attribute: The attribute to process.

    Returns:
        Processed attribute.
    """
    attribute_type = type(attribute)

    if issubclass(attribute_type, DTO):
        subquery_result = attribute.run(executor)
        return subquery_result.id if subquery_result else None

    if issubclass(attribute_type, list):
        return [sync_recurse(executor, item) for item in attribute]

    if issubclass(attribute_type, tuple) and hasattr(attribute, "_fields"):
        attribute_factory = namedtuple(attribute_type.__name__, attribute._fields)
        results = []
        for field in attribute._fields:
            tuple_attribute = getattr(attribute, field)
            results.append(sync_recurse(executor, tuple_attribute))
        return attribute_factory(*results)

    if issubclass(attribute_type, tuple):
        return tuple([sync_recurse(executor, item) for item in attribute])

    return attribute


@dataclass(kw_only=True)
class DTO:
    """
    Base class for Data Transfer Objects (DTOs) with EdgeDB.
    """

    def to_json(self, exclude_attributes: set = set()) -> str:
        """
        Generates a json object of the current state of the DTO class.

        Returns:
            json: A json object representing the current state of the DTO class.
        """
        dto_dict = asdict(self)
        for att in exclude_attributes:
            del dto_dict[att]
        return json.dumps(dto_dict, default=str)

    def to_dict(self, exclude_attributes: set = set()) -> str:
        """
        Generates a dictionary of the current state of the DTO class.

        Returns:
            dict: A dictionary representing the current state of the DTO class.
        """
        return asdict(self)

    def run(self, **kwargs):
        """
        Must be implemented by a subclass. Calls the generated function by edgedb-py.
        Example:
            def run(self, executor: Client, transaction: bool = False) -> list[BatchQueryResult]:
                return self._run(executor, transaction)
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def _query(self, **kwargs):
        """
        Must be implemented by a subclass. Creates a DTO specific for an EdgeQL file.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    async def _run_async(self, executor: AsyncIOClient, transaction: bool = False):
        """
        Executes the query asynchronously. Should be called by the run method.

        Args:
            executor: EdgeDB AsyncIOClient.
            transaction: If True, run within a transaction.

        Returns:
            Query result.
        """

        async def query(executor):
            for field_name, _ in self.__annotations__.items():
                old_value = getattr(self, field_name)
                new_value = await async_recurse(executor, old_value)
                setattr(self, field_name, new_value)
            kwargs = self.to_dict()

            # Remove DTO base class Attributes from kwds to avoid query errors
            # This can break python versions < 3.11
            for kw in DTO.__annotations__.keys():
                kwargs.pop(kw)

            return await self._query(**kwargs, executor=executor)

        if transaction:
            async for tx in executor.transaction():
                async with tx:
                    return await query(tx)

        return await query(executor)

    def _run(self, executor: Client, transaction: bool = False):
        """
        Executes the query synchronously. Should be called by the run method.

        Args:
            executor: EdgeDB Client.
            transaction: If True, run within a transaction.

        Returns:
            Query result.
        """

        def query(executor):
            for field_name, _ in self.__annotations__.items():
                old_value = getattr(self, field_name)
                new_value = sync_recurse(executor, old_value)
                setattr(self, field_name, new_value)
            kwargs = self.to_dict()

            # Remove DTO base class Attributes from kwds to avoid query errors
            for kw in DTO.__annotations__.keys():
                kwargs.pop(kw)

            return self._query(**kwargs, executor=executor)

        if transaction:
            for tx in executor.transaction():
                with tx:
                    return query(tx)
        return query(executor)
