class Proposition:
    pass


class Var(Proposition):
    def __init__(self, val: str) -> None:
        self.val = val

    def __str__(self) -> str:
        return self.val

    def __hash__(self) -> int:
        return self.val.__hash__()

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Var):
            return False
        return self.val == __o.val


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
        if not (isinstance(__o, Not) or isinstance(__o, Var)):
            return False

        match (self, __o):
            case (Var(val=v1), Var(val=v2)):
                return v1 == v2
            case (Not(val=v1), Not(val=v2)):
                return v1 == v2
            case _:
                return False

    def __hash__(self) -> int:
        return self.val.__hash__() + "!".__hash__()


def Negate(p: Proposition | Not) -> Proposition | Not:
    match p:
        case Var():
            return Not(p)
        case Not(val=p):
            return p
        case _:
            return Not(p)
