import time
from typing import Callable, Optional

from .exceptions import PlatynUiFatalError
from .settings import Settings

__all__ = ["wait_for"]


def wait_for(
    *predicates: Callable[[], bool],
    timeout: Optional[float] = None,
    delay: Optional[float] = None,
    invalidater: Optional[Callable[[], None]] = None,
) -> bool:
    if timeout is None:
        timeout = Settings.current().wait_for_timeout

    if delay is None:
        delay = Settings.current().wait_for_delay

    start_time = time.time()
    result = False

    while not result:
        if time.time() - start_time > timeout:
            break
        for p in predicates:
            if time.time() - start_time > timeout:
                break
            try:
                result = p()
            except (PlatynUiFatalError, KeyboardInterrupt, SystemExit):
                raise

            if not result:
                break

        if result:
            break

        time.sleep(delay)

        if invalidater is not None:
            invalidater()

    return result
