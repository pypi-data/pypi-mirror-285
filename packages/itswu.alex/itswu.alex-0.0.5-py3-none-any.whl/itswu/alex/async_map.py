import asyncio
from typing import (
    AsyncIterable,
    Awaitable,
    Callable,
    List,
    Iterable,
    Optional,
    TypeVar,
    Union,
    Tuple,
)

T = TypeVar("T")
U = TypeVar("U")


async def _wait_one(
    futures: List[Awaitable[U]], first_only: bool
) -> Tuple[U, List[Awaitable[U]]]:
    if first_only:
        return (await futures[0]), futures[1:]
    else:
        finished, running = await asyncio.wait(
            futures, return_when=asyncio.FIRST_COMPLETED
        )
        assert finished
        return (await next(iter(finished))), list(running)


async def async_map(
    map_fn: Callable[[T], Awaitable[U]],
    iterable: Union[Iterable[T], AsyncIterable[T]],
    max_concurrency: Optional[int] = None,
    ordered: bool = True,
) -> AsyncIterable[U]:
    running = []

    async def handle_iteration(item):
        nonlocal running
        running.append(asyncio.create_task(map_fn(item)))

        if max_concurrency and len(running) >= max_concurrency:
            finished, running = await _wait_one(running, first_only=ordered)
            yield finished

    if isinstance(iterable, Iterable):
        for item in iterable:
            async for result in handle_iteration(item):
                yield result
    elif isinstance(iterable, AsyncIterable):
        async for item in iterable:
            async for result in handle_iteration(item):
                yield result
    else:
        assert ValueError(
            f"`iterable` must be either an Iterable or AsyncIterable. Not {type(iterable)}"
        )

    while running:
        finished, running = await _wait_one(running, first_only=ordered)
        yield finished
