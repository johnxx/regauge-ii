import asyncio
import time
from math import floor

debug = False

def print_dbg(some_string, **kwargs):
    if debug:
        return print(some_string, **kwargs)

async def schedule(frequency, coroutine_function, *args, **kwargs):
    run_every_ms = floor(1_000 / frequency)
    print_dbg("Running {} every {} ms".format(coroutine_function, run_every_ms))
    while True:
        started_ms = time.ticks_ms()
        await coroutine_function(*args, **kwargs)
        remaining_ms = run_every_ms - time.ticks_diff(time.ticks_ms(), started_ms)
        if remaining_ms > 0:
            print_dbg("Sleeping for {} ms".format(remaining_ms))
            await asyncio.sleep_ms(remaining_ms)