from typing import Any, Generator, Iterable, Type, TypeVar

T = TypeVar("T", bound=Type)


def get_all_descendant_classes(
    cls: T,
    exclude: Iterable[Type] = (),
) -> Generator[T, Any, None]:
    """
    Returns all direct and non-direct subclasses.

    exclude: List of class types that should be excluded. Their descendants are not excluded.
    """
    queue = [cls]
    subclasses = cls.__subclasses__()

    while len(queue) > 0:
        subclasses = queue.pop().__subclasses__()

        for subclass in subclasses:
            intersection = set(exclude) & set(subclass.__bases__)

            if not intersection:
                yield subclass

            queue.append(subclass)
