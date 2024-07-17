from itswu.alex import async_map

import asyncio
import pytest

pytest_plugins = ("pytest_asyncio",)


async def async_gen(iterable):
    for item in iterable:
        yield item


@pytest.mark.asyncio
async def test_ordered_map_iterable():
    execution_order = []

    async def fn(item):
        nonlocal execution_order
        name, t = item
        # How can this be done in a less flakey way?
        await asyncio.sleep(t)
        execution_order.append(name)
        return name

    inputs = [
        ("a", 0.2),
        ("b", 0.1),
        ("c", 0),
    ]
    gen = async_map(fn, inputs, max_concurrency=2)

    results = []
    async for item in gen:
        results.append(item)

    assert results == ["a", "b", "c"]
    assert execution_order == ["b", "a", "c"]


@pytest.mark.asyncio
async def test_ordered_map_async_iterable():
    execution_order = []

    async def fn(item):
        nonlocal execution_order
        name, t = item
        # How can this be done in a less flakey way?
        await asyncio.sleep(t)
        execution_order.append(name)
        return name

    inputs = [
        ("a", 0.2),
        ("b", 0.1),
        ("c", 0),
    ]
    gen = async_map(fn, async_gen(inputs), max_concurrency=2)

    results = []
    async for item in gen:
        results.append(item)

    assert results == ["a", "b", "c"]
    assert execution_order == ["b", "a", "c"]


@pytest.mark.asyncio
async def test_ordered_map_iterable_unordered():
    execution_order = []

    async def fn(item):
        nonlocal execution_order
        name, t = item
        # How can this be done in a less flakey way?
        await asyncio.sleep(t)
        execution_order.append(name)
        return name

    inputs = [
        ("a", 0.2),
        ("b", 0.1),
        ("c", 0),
    ]
    gen = async_map(fn, inputs, max_concurrency=2, ordered=False)

    results = []
    async for item in gen:
        results.append(item)

    assert results == execution_order
    assert execution_order == ["b", "c", "a"]


@pytest.mark.asyncio
async def test_ordered_map_async_iterable_onordered():
    execution_order = []

    async def fn(item):
        nonlocal execution_order
        name, t = item
        # How can this be done in a less flakey way?
        await asyncio.sleep(t)
        execution_order.append(name)
        return name

    inputs = [
        ("a", 0.2),
        ("b", 0.1),
        ("c", 0),
    ]
    gen = async_map(fn, async_gen(inputs), max_concurrency=2, ordered=False)

    results = []
    async for item in gen:
        results.append(item)

    assert results == execution_order
    assert execution_order == ["b", "c", "a"]
