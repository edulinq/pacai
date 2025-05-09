import abc
import heapq
import typing

T = typing.TypeVar('T')
""" A generic type to ensure type consistency for all the container classes. """

class FringeContainer(abc.ABC, typing.Generic[T]):
    """
    A generic container base class that is useful for a search fringe
    (but can be used for any sort of storage).
    """

    def __init__(self) -> None:
        self._items: list[T] = []
        """
        The underlying storage for our container's items.
        We can just use a normal list as long as we are careful about how we work with it.
        """

    def is_empty(self) -> bool:
        """ Returns True if the container is empty. """

        return (len(self._items) == 0)

    def __len__(self) -> int:
        """ Override the len() operator to get the size of the container. """

        return len(self._items)

    @abc.abstractmethod
    def push(self, item: T) -> None:
        """ Add an item to this container. """

    @abc.abstractmethod
    def pop(self) -> T:
        """ Remove the next item from this container. """

class Stack(FringeContainer[T]):
    """
    A container with a last-in-first-out (LIFO) queuing policy.
    See https://en.wikipedia.org/wiki/Stack_(abstract_data_type) .
    """

    def push(self, item: T) -> None:
        """ Push an item onto the stack. """

        self._items.append(item)

    def pop(self) -> T:
        """ Pop the most recently pushed item from the stack. """

        return self._items.pop()

class Queue(FringeContainer[T]):
    """
    A container with a first-in-first-out (FIFO) queuing policy.
    See: https://en.wikipedia.org/wiki/Queue_(abstract_data_type) .
    """

    def push(self, item: T) -> None:
        """ Enqueue the item into the queue. """

        self._items.insert(0, item)

    def pop(self) -> T:
        """ Dequeue the earliest enqueued item still in the queue. """

        return self._items.pop()

class PriorityQueue(FringeContainer[T]):
    """
    A container with a queuing policy that prioritizes objects with lower priority..
    See: https://en.wikipedia.org/wiki/Priority_queue .

    Each inserted item has a priority associated with it,
    and the user is usually interested in quick retrieval of the lowest-priority item in the queue.
    This data structure allows O(1) access to the lowest-priority item.

    Note that this PriorityQueue does not allow you to change the priority of an item.
    However, you may insert the same item multiple times with different priorities.
    """

    def push(self, item: T, priority: float) -> None:  # type: ignore  # pylint: disable=arguments-differ
        """ Enqueue the item into the priority queue. """

        pair = (priority, item)
        heapq.heappush(self._items, pair)  # type: ignore

    def pop(self) -> T:
        """ Dequeue the earliest enqueued item still in the priority queue. """

        (_, item) = heapq.heappop(self._items)  # type: ignore
        return item  # type: ignore

@typing.runtime_checkable
class PriorityFunction(typing.Protocol):
    """
    A function that assigns a priority value to an object being inserted into the priority queue.
    """

    def __call__(self, item: typing.Any) -> float:
        ...

class PriorityQueueWithFunction(PriorityQueue[T]):
    """
    Implements a priority queue with the same push/pop signature of the Queue and the Stack classes.
    This is designed for drop-in replacement for those two classes.
    The caller has to provide a priority function, which extracts each item's priority.
    """

    def __init__(self, priority_func: PriorityFunction) -> None:
        super().__init__()

        self._priority_func: PriorityFunction = priority_func
        """ The function to get a priority for each item in this container. """

    def push(self, item: T) -> None:  # type: ignore  # pylint: disable=arguments-differ
        """
        Adds an item to the queue with priority from the priority function
        """

        super().push(item, self._priority_func(item))
