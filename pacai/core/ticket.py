import typing

class Ticket(typing.NamedTuple):
    """
    An agent's Ticket determines when they will move next.
    A ticket is a tuple of three values: (next move time, last move time, number of moves).
    The agent with the lowest ticket (starting with the first value and moving to the next on a tie) gets to move next.
    All "time" values represented by a ticket are abstract and do not relate to any actual time units.
    """

    next_time: int
    """ The next time the ticket is allowed to move. """

    last_time: int
    """ The last time that the agent moved. """

    num_moves: int
    """ The total number of times this agent has moved so far. """

    def next(self, move_delay: int) -> 'Ticket':
        """ Get the next ticket in the sequence for this agent. """

        return Ticket(
            next_time = self.next_time + move_delay,
            last_time = self.next_time,
            num_moves = self.num_moves + 1,
        )
