import enum
import typing

import pacai.core.isolation.isolator
import pacai.core.isolation.none
import pacai.core.isolation.process

class Level(enum.Enum):
    """ An enum representing the different isolation levels supported by the engine. """

    NONE = 'none'
    PROCESS = 'process'

    def get_isolator(self, **kwargs: typing.Any) -> pacai.core.isolation.isolator.AgentIsolator:
        """ Get an isolator matching the given level. """

        isolator: pacai.core.isolation.isolator.AgentIsolator | None = None

        if (self == Level.NONE):
            isolator = pacai.core.isolation.none.NoneIsolator(**kwargs)
        elif (self == Level.PROCESS):
            isolator = pacai.core.isolation.process.ProcessIsolator(**kwargs)

        if (isolator is None):
            raise ValueError(f"Unknown isolation level '{self}'.")

        return isolator

LEVELS: list[str] = [item.value for item in Level]
