from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterable
from typing import Any, ClassVar
from weakref import ReferenceType


class ComponentError(Exception):
    """Raised when a component cannot process correctly"""


class Component(ABC, AsyncIterator):
    """
    A component that can be passed to a pipeline to create a chain of commands.
    Consuming an Iterable and yielding an AsyncIterator.
    It can also be called directly by iterating over its process method with individual values.
    """

    _instances: ClassVar[list[ReferenceType[Component]]] = []

    @classmethod
    def instances(cls) -> list[Component]:
        """
        Conveniency class method returning a list of all running instances of Component
        Also remove instances that are not referenced anymore from _instances
        Can be used for graceful shutdown
        """
        return [instance for reference in cls._instances if (instance := reference()) is not None]

    @classmethod
    def register_instance(cls, self: Component) -> None:
        cls._instances.append(ReferenceType(self, cls.remove_instance))

    @classmethod
    def remove_instance(cls, ref: ReferenceType) -> None:
        """
        Remove an instance from the list of tracked instances.
        """
        cls._instances.remove(ref)

    def __init__(self) -> None:
        """
        Init registers the instance. By default an instance does nothing.
        """
        self.__class__.register_instance(self)
        self._prev_component: Component | None = None
        self._source_iter: AsyncIterator
        self._is_running = True

    @property
    def is_running(self) -> bool:
        """
        Can be overriden to define what is_running means.
        """
        return self._is_running

    def stop(self) -> None:
        """
        Can be overriden for custom stop logic.
        """
        self._is_running = False
        if self._prev_component:
            self._prev_component.stop()

    @staticmethod
    async def _wrap_source(source: Source) -> AsyncIterator[Any]:
        """
        A helper method to wrap synchronous iterators with async functionality and yield items.
        """
        if isinstance(source, AsyncIterator):
            async for item in source:
                yield item
        elif isinstance(source, Iterable):
            for item in source:
                yield item
                await asyncio.sleep(0)  # Yield control to keep the event loop responsive
        else:
            raise ComponentError("Source data must be an Iterable or AsyncIterator.")

    async def _make_source_iter(self, source: Source) -> AsyncIterator[Any]:
        """
        Generate items from the source data and process each item.
        This method combines fetching and processing logic.
        """
        async for item in self._wrap_source(source):
            async for processed_item in self.process(item):
                yield processed_item
                await asyncio.sleep(0)  # Yield control to keep the event loop responsive

    def source(self, source: Source) -> Component:
        """
        This method can be called on any element of a chain.
        It transforms a Source into an AsyncIterator and based on the type of Source:
        - Iterator/AsyncIterator: it will propagate to the first component and reset the pipeline.
        - Component: such as when called by `.then` it sets the previous component as the source.
        """
        self._source_iter = None

        if self._prev_component:
            self._prev_component.source(source)
            self._source_iter = self._make_source_iter(self._prev_component)
            return self

        if isinstance(source, Component):
            self._prev_component = source

        self._source_iter = self._make_source_iter(source)
        return self

    def __aiter__(self) -> AsyncIterator[Any]:
        return self

    async def __anext__(self) -> Any:
        if not self.is_running:
            raise StopAsyncIteration
        return await self._source_iter.__anext__()

    @abstractmethod
    async def process(self, item: Any) -> AsyncIterator[Any]:
        """
        Method to be overridden by subclasses to define specific processing logic.
        """
        yield item

    def then(self, component: Component) -> Component:
        """
        Chain another component to process the output of this component.
        """
        component.source(self)
        return component

    async def run(self) -> None:
        """
        Consume all items in this component.
        Can be overriden for custom logic.
        """
        async for _ in self:
            pass


Source = Component | Iterable[Any] | AsyncIterator[Any]
