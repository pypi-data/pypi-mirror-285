import asyncio
import timeit
from collections.abc import AsyncIterator, Iterator

from aiterio import Component


# 1. Synchronous function to increment a number
def inc(x: int) -> int:
    return x + 1


# 2. Iterator version
def iter_inc() -> Iterator[int]:
    for i in range(1000):
        yield inc(i)


# 3. Asynchronous iterator version
async def async_iter_inc() -> AsyncIterator[int]:
    for i in range(1000):
        await asyncio.sleep(0)  # necessary for async behavior
        yield inc(i)


# 4. Using Component
class IncComponent(Component):
    async def process(self, item: int) -> AsyncIterator[int]:
        yield inc(item)


async def run_sync() -> None:
    list(map(inc, range(1000)))


async def run_iter_inc() -> None:
    list(iter_inc())


async def run_async_iter() -> None:
    async for _ in async_iter_inc():
        pass


async def run_async_pipeline() -> None:
    component = IncComponent().source(async_iter_inc())
    async for _ in component:
        pass


async def run_async_pipeline_type_checking() -> None:
    component = IncComponent().source(async_iter_inc())
    async for _ in component:
        pass


# Benchmarking functions
def benchmark_sync() -> None:
    asyncio.run(run_sync())


def benchmark_iter() -> None:
    asyncio.run(run_iter_inc())


def benchmark_async_iter() -> None:
    asyncio.run(run_async_iter())


def benchmark_async_pipeline() -> None:
    asyncio.run(run_async_pipeline())


def benchmark_async_pipeline_type_checking() -> None:
    asyncio.run(run_async_pipeline_type_checking())


# Running benchmarks
if __name__ == "__main__":
    print("Benchmarking synchronous function:")
    print(timeit.timeit("benchmark_sync()", globals=globals(), number=100))

    print("Benchmarking iterator:")
    print(timeit.timeit("benchmark_iter()", globals=globals(), number=100))

    print("Benchmarking asynchronous iterator:")
    print(timeit.timeit("benchmark_async_iter()", globals=globals(), number=100))

    print("Benchmarking Component:")
    print(timeit.timeit("benchmark_async_pipeline()", globals=globals(), number=100))

    print("Benchmarking Component with type_checking:")
    print(timeit.timeit("benchmark_async_pipeline_type_checking()", globals=globals(), number=100))
