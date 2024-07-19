# aiterio

## tl;dr

`aiterio` is a minimal library to build asynchronous pipelines based on Python's asynchronous iterators.

It transforms a syntax like:

```python
aiterator_3(aiterator_2(aiterator_1(source_data)))
```

or

```python
aiterator_1 = fn_1(source_data)
aiterator_2 = fn_2(aiterator_1)
aiterator_3 = fn_3(aiterator_3)

async for item in aiterator_3:
    pass
```

into

```python
await Component1().source(source_data).then(Component2()).then(Component3()).run()
# or
for item in Component1().source(source_data).then(Component2()).then(Component3()):
    pass
```

## Why use this?

- Minimal library without dependencies
- Simplifies usage of asynchronous iterators
- Makes it easy to create components with a single responsibility and to test them
- Built-in shutdown logic

## Alternatives / Inspiration

- Akka (java, scala): https://doc.akka.io/docs/akka/current/stream/index.html
- Faust: https://github.com/robinhood/faust
- Flink: https://flink.apache.org/
- RxPy: https://github.com/ReactiveX/RxPY
- Streamz: https://github.com/python-streamz/streamz

* License: MIT
