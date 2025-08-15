import typing

import edq.util.json

class Ticket(edq.util.json.DictConverter):
    """
    An agent's Ticket determines when they will move next.
    A ticket is a tuple of three values: (next move time, last move time, number of moves).
    Tickets should be treated as immutable.
    The agent with the lowest ticket (starting with the first value and moving to the next on a tie) gets to move next.
    All "time" values represented by a ticket are abstract and do not relate to any actual time units.
    """

    def __init__(self,
            next_time: int,
            last_time: int,
            num_moves: int) -> None:
        self.next_time: int = next_time
        """ The next time the ticket is allowed to move. """

        self.last_time: int = last_time
        """ The last time that the agent moved. """

        self.num_moves: int = num_moves
        """ The total number of times this agent has moved so far. """

    def is_before(self, other: 'Ticket') -> bool:
        """ Return true if this ticket comes before the other ticket. """

        self_tuple = (self.next_time, self.last_time, self.num_moves)
        other_tuple = (other.next_time, other.last_time, other.num_moves)

        return self_tuple < other_tuple

    def next(self, move_delay: int) -> 'Ticket':
        """ Get the next ticket in the sequence for this agent. """

        return Ticket(
            next_time = self.next_time + move_delay,
            last_time = self.next_time,
            num_moves = self.num_moves + 1,
        )

    def to_dict(self) -> dict[str, typing.Any]:
        return vars(self).copy()

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> typing.Any:
        data = data.copy()
        return cls(**data)
