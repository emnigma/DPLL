from __future__ import annotations

from typing import Optional
from logic import Disjunction, Var, Not, Or, And, Proposition, Negate
from utils import pe, se


class SAT:
    def __init__(self, model: Model) -> None:
        self.model = model


class UNSAT:
    def __init__(self, S: Disjunction) -> None:
        self.S = S


class Model:
    def __init__(self, data=None) -> None:
        if data == None:
            self.inner = {}
        else:
            self.inner = data

    def add(self, p: Var | Not, value: bool) -> None:
        match p:
            case Var():
                self.inner[p] = value
            case Not():
                self.inner[Negate(p)] = not value

    def copy(self) -> Model:
        return Model(self.inner.copy())

    def pe(self) -> None:
        for k, v in sorted(self.inner.items(), key=lambda x: x[0].val):
            print(k, "->", v)


def literals_in_conjuction(conjuction: Proposition) -> list[Var]:
    def _literals_in_conjuction(conjuction: Proposition, accumulator: set[Proposition]):
        match conjuction:
            case Var():
                accumulator.add(conjuction)
            case Not(val=p):
                if isinstance(p, Var):
                    accumulator.add(conjuction)
                else:
                    _literals_in_conjuction(p, accumulator)
            case And(values=(p1, p2)) | Or(values=(p1, p2)):
                _literals_in_conjuction(p1, accumulator)
                _literals_in_conjuction(p2, accumulator)

        return accumulator

    return list(_literals_in_conjuction(conjuction, set()))


def literal_exists_in_conjuction(conjuction: Proposition, literal) -> bool:
    return literal in literals_in_conjuction(conjuction)


def rm_conjuction_if_contains_literal(S: Disjunction, literal) -> Disjunction:
    def _no_literal_in_conjuction(conjuction: Proposition) -> bool:
        return not literal_exists_in_conjuction(conjuction, literal)

    return list(filter(_no_literal_in_conjuction, S))


def single_literals(S: Disjunction) -> list[Var | Not]:
    def _is_literal(c: Proposition) -> bool:
        match c:
            case Var():
                return True
            case Not(val=p):
                return isinstance(p, Var)
            case _:
                return False

    return list(filter(_is_literal, S))


def pure_literals(S: Disjunction) -> list[Var | Not]:
    all_literals = set()
    for c in S:
        for literal in literals_in_conjuction(c):
            all_literals.add(literal)

    pures = set()
    for literal in all_literals:
        if not Negate(literal) in all_literals:
            pures.add(literal)

    return list(pures)


def EliminatePureLiteral(
    conjuction: Proposition, l: Proposition
) -> Optional[Proposition]:
    def _walk_remove(conjuction: Proposition, l: Proposition) -> Optional[Proposition]:
        match conjuction:
            case Var():
                if conjuction == l:
                    return None
                return conjuction

            case Not(val=p):
                if p == l.val:
                    return None
                return conjuction

            case And(values=(p1, p2)):
                left = _walk_remove(p1, l)
                right = _walk_remove(p2, l)
                match (left, right):
                    case (None, None):
                        return None
                    case (None, _):
                        return right
                    case (_, None):
                        return left
                    case (Proposition(), Proposition()):
                        return And(left, right)

            case Or(values=(p1, p2)):
                left = _walk_remove(p1, l)
                right = _walk_remove(p2, l)
                match (left, right):
                    case (None, None):
                        return None
                    case (None, _):
                        return right
                    case (_, None):
                        return left
                    case (Proposition(), Proposition()):
                        return Or(left, right)

    return _walk_remove(conjuction, l)


def UnitPropagate(S: Disjunction, l: Proposition) -> Disjunction:
    def _no_literal_in_conjuction(conjuction: Proposition) -> bool:
        return not literal_exists_in_conjuction(conjuction, l)

    def _eliminate_pure(conjuction: Proposition) -> Optional[Proposition]:
        return EliminatePureLiteral(conjuction, Negate(l))

    return list(map(_eliminate_pure, list(filter(_no_literal_in_conjuction, S))))


def ChooseLiteral(S: Disjunction) -> Var:
    # pick first
    return literals_in_conjuction(S[0])[0]


def DPLL(S: Disjunction, M: Model) -> SAT | UNSAT:
    if not S:
        return SAT(M)
    if None in S:
        return UNSAT(S)

    for literal in single_literals(S):  # распространение юницикличного дизъюнкта
        S = UnitPropagate(S, literal)
        M.add(literal, True)

    for literal in pure_literals(S):
        S = rm_conjuction_if_contains_literal(S, literal)
        M.add(literal, True)

    if not S:
        return SAT(M)
    if None in S:
        return UNSAT(S)

    literal = ChooseLiteral(S)

    positive_literal_M = M.copy()
    positive_literal_M.add(literal, True)

    guessed_result = DPLL([*S, literal], positive_literal_M)
    if isinstance(guessed_result, SAT):
        return guessed_result
    else:
        negative_literal_M = M.copy()
        negative_literal_M.add(literal, False)
        return DPLL([*S, Negate(literal)], negative_literal_M)


def main():
    a, b, c, d = Var("a"), Var("b"), Var("c"), Var("d")
    cnf = [
        Or(Not(a), Or(b, c)),
        Or(a, Or(c, d)),
        Or(a, Or(c, Not(d))),
        Or(a, Or(Not(c), d)),
        Or(a, Or(Not(c), Not(d))),
        Or(Not(b), Or(Not(c), d)),
        Or(Not(a), Or(b, Not(c))),
        Or(Not(a), Or(Not(b), c)),
    ]

    print(f"{se(cnf)=}")

    match DPLL(cnf, Model()):
        case SAT(model=model):
            print("SAT")
            model.pe()
        case UNSAT(S=s):
            print("UNSAT")
            pe(s)


if __name__ == "__main__":
    main()
