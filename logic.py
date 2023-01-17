class Proposition:
    pass


class Var(Proposition):
    def __init__(self, val: str) -> None:
        self.val = val

    def __str__(self) -> str:
        return self.val

    def __hash__(self) -> int:
        return self.val.__hash__()


class Or(Proposition):
    def __init__(self, p1, p2) -> None:
        self.values = (p1, p2)

    def __hash__(self) -> int:
        return self.values.__hash__()

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Or):
            return False

        return set(self.values) == set(__o.values)


class And(Proposition):
    def __init__(self, p1, p2) -> None:
        self.values = (p1, p2)

    def __hash__(self) -> int:
        return self.values.__hash__()

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, And):
            return False

        return set(self.values) == set(__o.values)


class Not(Proposition):
    def __init__(self, p) -> None:
        self.val = p

    def __str__(self) -> str:
        return f"!({self.val})"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Not):
            return False

        return self.val == __o.val

    def __hash__(self) -> int:
        return self.val.__hash__() + "!".__hash__()
