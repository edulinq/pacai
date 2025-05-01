import typing

import pacai.util.json
import pacai.util.reflection

DEFAULT_MOVE_DELAY: int = 100
""" The default delay between agent moves. """

class AgentInfo(pacai.util.json.DictConverter):
    """
    Argument used to construct an agent.
    Common arguments used by the engine are stored as top-level fields,
    while arguments that spcecific child agents may use are stored in a general dict.
    """

    def __init__(self,
            name: str | pacai.util.reflection.Reference = '',
            move_delay: int = DEFAULT_MOVE_DELAY,
            extra_arguments: dict[str, typing.Any] | None = None,
            **kwargs) -> None:
        if (isinstance(name, str)):
            name = pacai.util.reflection.Reference(name)

        self.name: pacai.util.reflection.Reference = name
        """ The name of the agent's class (as a reflection refernce). """

        if (move_delay <= 0):
            raise ValueError("Agent move delay must be > 0.")

        self.move_delay: int = move_delay
        """ The move delay of the agent. """

        self.extra_arguments: dict[str, typing.Any] = {}
        """
        Additional arguments to the agent.
        These are typically used by agent subclasses.
        """

        self.extra_arguments.update(kwargs)
        if (extra_arguments is not None):
            self.extra_arguments.update(extra_arguments)

    def set(self, name: str, value: typing.Any) -> None:
        if (name == 'name'):
            if (isinstance(value, pacai.util.reflection.Reference)):
                self.name = value
            else:
                self.name = pacai.util.reflection.Reference(str(value))
        elif (name == 'move_delay'):
            self.move_delay = int(value)
        else:
            self.extra_arguments[name] = value

    def update(self, other: 'AgentInfo') -> None:
        self.name = other.name
        self.move_delay = other.move_delay
        self.extra_arguments.update(other.extra_arguments)

    def to_dict(self) -> dict[str, typing.Any]:
        data = vars(self).copy()
        data['name'] = self.name.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        data = data.copy()
        data['name'] = pacai.util.reflection.Reference.from_dict(data['name'])
        return AgentInfo(**data)
