from typing import Callable, Dict, List, Set, Union


class Mutator:
    def __init__(
        self,
        obj: object,
        names: List[str],
        wrapped: Set[str],
        replacers: Dict[str, Callable],
        prefixes: Dict[str, List[Callable]],
        postfixes: Dict[str, List[Callable]],
    ):
        self.__obj = obj
        self.__names = names
        self.__wrapped = wrapped
        self.__replacers = replacers
        self.__prefixes = prefixes
        self.__postfixes = postfixes

        for name in names:
            if name not in self.__wrapped:
                self.__wrapped.add(name)
                self.__wrap(name)

    def __wrap(self, name: str):
        raw = getattr(self.__obj, name)

        def wrapper(*args, **kwargs):
            if name in self.__prefixes:
                for hook in self.__prefixes[name]:
                    if hook(*args, **kwargs) == False:
                        return None

            value = None

            if name in self.__replacers:
                value = self.__replacers[name](*args, **kwargs)
            else:
                value = raw(*args, **kwargs)

            if name in self.__postfixes:
                for hook in self.__postfixes[name]:
                    hook(value, args, kwargs)

            return value

        setattr(self.__obj, name, wrapper)

    def prefix(self, hook: Callable):
        for name in self.__names:
            if name not in self.__prefixes:
                self.__prefixes[name] = []

            self.__prefixes[name].append(hook)

        return self

    def postfix(self, hook: Callable):
        for name in self.__names:
            if name not in self.__postfixes:
                self.__postfixes[name] = []

            self.__postfixes[name].append(hook)

        return self

    def replace(self, replacer: Union[Callable, object]):
        """
        Replaces the corresponding methods
        with the given callable,
        or the object's method with the same name.
        """
        is_callable = callable(replacer)

        for name in self.__names:
            if is_callable:
                self.__replacers[name] = replacer
            else:
                self.__replacers[name] = getattr(replacer, name)

        return self

    def remove_postfix(self, callable: Callable):
        for name in self.__names:
            if name not in self.__postfixes:
                continue

            self.__postfixes[name].remove(callable)

        return self

    def remove_prefix(self, callable: Callable):
        for name in self.__names:
            if name not in self.__prefixes:
                continue

            self.__prefixes[name].remove(callable)

        return self

    def remove_replacer(self):
        """
        Remove replacers from these methods.
        """
        for name in self.__names:
            if name in self.__replacers:
                del self.__replacers[name]

        return self
