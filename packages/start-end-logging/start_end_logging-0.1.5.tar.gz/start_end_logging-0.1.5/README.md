# start-end-logging

A very simple Python logging library that logs the start and end of a process step and, in particular, indicates the
elapsed time.

## Installation

```pip install start-end-logging``` or ```poetry add start-end-logging```

## Usage

```
import logging
import time

from start_end_logging.start_end_logging import log_start, log_end, init_logging

log = logging.getLogger(__name__)

if __name__ == "__main__":
    init_logging("../logs", "log.log")
    log_start("main process", log)
    log_start("preparing something", log)
    time.sleep(0.15)
    log_end()
    log_start("preparing something other", log)
    time.sleep(0.05)
    log_end()
    time.sleep(0.25)
    log_end()
```

Output:

```
2024-01-23 20:38:09,305 - __main__ - INFO - (1) start main process.
2024-01-23 20:38:09,305 - __main__ - INFO - (2) start preparing something.
2024-01-23 20:38:09,456 - __main__ - INFO - (2) end preparing something. time elapsed: 00:00:00.151.
2024-01-23 20:38:09,456 - __main__ - INFO - (2) start preparing something other.
2024-01-23 20:38:09,508 - __main__ - INFO - (2) end preparing something other. time elapsed: 00:00:00.052.
2024-01-23 20:38:09,758 - __main__ - INFO - (1) end main process. time elapsed: 00:00:00.453.
```

