# What 2 Time?

Reusable timing code that handles unit conversion,
pretty printing time, total of repeat and
(in future) re-entrant timers.

A timer can be creted and will default to printing
total time on stopping:
```python
>>> from what2_time import Timer
>>> t = Timer().start()
>>> t.stop()
Elapsed time: 1.8890 seconds
```

Or given a name for ease of inspection
```python
>>> from what2_time import Timer
>>> t = Timer("FooTime").start()
>>> t.stop()
FooTime - Elapsed time: 1.4432 seconds
```

Alternatively, the output can be logged to
any callable such as a logger:
```python
>>> from what2_time import Timer
>>> import logging
>>> logger = logging.getLogger()
>>> logging.basicConfig(level=10)
>>> t = Timer(logger=logger.info).start()
>>> t.stop()
INFO:root:Elapsed time: 1.2577 seconds
```

Or instead set no logger and handle logging yourself:
```python
>>> from what2_time import Timer
>>> t = Timer(logger=None).start()
>>> elapsed = t.stop()
>>> print(elapsed)
1.587853118
```

A timer can also be used as a context manager:
```python
>>> import time
>>> from what2_time import Timer
>>> with Timer("ContextTimer"):
...     time.sleep(1)
ContextTimer - Elapsed time: 1.0004 seconds
```

If you want to time the total time of something
that is not performed in a single block, instead
a `MetaTimer` can be used:
```python
>>> import time
>>> from what2_time import MetaTimer
>>> with MetaTimer("MetaT"):
...     time.sleep(1)
...
>>> with MetaTimer("MetaT"):
...     time.sleep(1)
...
>>> print(MetaTimer.get_meta_duration("MetaT"))
2.00162006
```
