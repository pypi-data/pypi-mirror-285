from enum import Enum


class LifeCycle(Enum):
    SINGLETON = 1
    TRANSIENT = 2
    SCOPED = 3
