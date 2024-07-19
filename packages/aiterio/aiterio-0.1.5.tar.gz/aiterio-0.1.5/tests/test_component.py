from collections.abc import AsyncIterator

import pytest

from aiterio import Component, ComponentError


class Add(Component):
    def __init__(self, addend: int = 1) -> None:
        super().__init__()
        self._addend = addend

    async def process(self, item: int) -> AsyncIterator[int]:
        yield item + self._addend


class Multiply(Component):
    def __init__(self, factor: int = 1) -> None:
        super().__init__()
        self._factor = factor

    async def process(self, item: int) -> AsyncIterator[int]:
        yield item * self._factor


async def test_processing_integers() -> None:
    component = Add(1).source(range(5))
    result = [value async for value in component]
    assert result == [1, 2, 3, 4, 5]


async def test_multiple_components() -> None:
    pipeline = Add(1).source(range(5)).then(Multiply(factor=2))
    result = [value async for value in pipeline]
    assert result == [2, 4, 6, 8, 10]


async def test_non_iterator_source() -> None:
    component = Add(1).source(1234)  # type: ignore[arg-type]
    with pytest.raises(ComponentError):
        await component.run()


async def test_type() -> None:
    Component._type_checking = True  # noqa: SLF001
    component = Add(1).source(["a", "b", "c"])
    with pytest.raises(TypeError):
        await component.run()
    Component._type_checking = False  # noqa: SLF001


async def test_source_last() -> None:
    pipeline = Add(2).then(Multiply(3)).source([1, 2, 3])
    result = [value async for value in pipeline]
    assert result == [9, 12, 15]


async def test_source_multiple() -> None:
    pipeline = Add(2).then(Multiply(3))
    result = [value async for value in pipeline.source([1, 2, 3])]
    assert result == [9, 12, 15]

    result = [value async for value in pipeline.source([3, 2, 1])]
    assert result == [15, 12, 9]


async def test_source_exhaustion() -> None:
    pipeline = Add(2).source([1, 2, 3]).then(Multiply(3))
    result = [value async for value in pipeline]
    assert result == [9, 12, 15]

    # source is not called again so this is exhausted
    result = [value async for value in pipeline]
    assert result == []

    result = [value async for value in pipeline.source([3, 2, 1])]
    assert result == [15, 12, 9]
