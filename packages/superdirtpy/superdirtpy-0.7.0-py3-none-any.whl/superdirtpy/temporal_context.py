from __future__ import annotations

import copy
import time
from datetime import datetime, timedelta


class TemporalContext:
    def __init__(self, dryrun: bool = False) -> None:
        init_vtime = datetime.now()
        self.__init_vtime = init_vtime
        self.__vtime = init_vtime
        self.__dryrun = dryrun

    def elapsed_time(self) -> timedelta:
        return self.__vtime - self.__init_vtime

    def now(self) -> datetime:
        return self.__vtime

    def set_now(self, now: datetime) -> None:
        self.__vtime = now

    def __sleep(self) -> None:
        if self.is_dryrun():
            return
        delta_sec = (self.__vtime - datetime.now()).total_seconds()
        if delta_sec > 0:
            time.sleep(delta_sec)

    def sleep(self, delta: timedelta) -> None:
        self.__vtime += delta
        self.__sleep()

    def sleep_until(self, until: datetime) -> None:
        self.__vtime = until
        self.__sleep()

    def is_dryrun(self) -> bool:
        return self.__dryrun

    def clone(self) -> TemporalContext:
        return copy.deepcopy(self)
