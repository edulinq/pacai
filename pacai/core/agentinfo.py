import typing

DEFAULT_MOVE_DELAY: int = 100
""" The default delay between agent moves. """

class AgentInfo:
    """
    Argument used to construct an agent.
    Common arguments used by the engine are stored as top-level fields,
    while arguments that spcecific child agents may use are stored in a general dict.
    """

    def __init__(self, name: str = '',
            move_delay: int = DEFAULT_MOVE_DELAY,
            **kwargs) -> None:
        name = name.strip()
        if (len(name) == 0):
            raise ValueError("Agent name cannot be empty.")

        if (move_delay <= 0):
            raise ValueError("Agent move delay must be > 0.")

        self.name: str = name
        self.move_delay: int = move_delay

        self.extra_arguments: dict[str, typing.Any] = kwargs

    def set(self, name: str, value: typing.Any) -> None:
        if (name == 'name'):
            self.name = str(value)
        elif (name == 'move_delay'):
            self.move_delay = int(value)
        else:
            self.extra_arguments[name] = value

    def update(self, other: 'AgentInfo') -> None:
        self.name = other.name
        self.move_delay = other.move_delay
        self.extra_arguments.update(other.extra_arguments)
