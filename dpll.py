from __future__ import annotations

from typing import Optional
from logic import Var, Not, Or, And, Proposition, Negate
from utils import pe, se
from cnf import create_cnf


class SAT:
    def __init__(self, model: dict[Var:bool]) -> None:
        self.model = model


class UNSAT:
    def __init__(self, S: list[Proposition]) -> None:
        self.S = S


def literals_in_conjunct(conjunct: Proposition) -> list[Var]:
    def _literals_in_conjunct(conjunct, accumulator):
        match conjunct:
            case Var():
                accumulator.add(conjunct)
            case Not(val=p):
                if isinstance(p, Var):
                    accumulator.add(conjunct)
                else:
                    _literals_in_conjunct(p, accumulator)
            case And(values=(p1, p2)) | Or(values=(p1, p2)):
                _literals_in_conjunct(p1, accumulator)
                _literals_in_conjunct(p2, accumulator)

        return accumulator

    return list(_literals_in_conjunct(conjunct, set()))


def literal_exists_in_conjunct(conjunct: Proposition, literal) -> bool:
    return literal in literals_in_conjunct(conjunct)


def rm_conjunct_if_contains_literal(S: list[Proposition], literal) -> list[Proposition]:
    def _no_literal_in_conjunct(conjunct):
        return not literal_exists_in_conjunct(conjunct, literal)

    return list(filter(_no_literal_in_conjunct, S))


def single_literals(S: list[Proposition]) -> list[Var]:
    return list(filter(lambda p: isinstance(p, Var), S))


def pure_literals(S: list[Proposition]) -> list[Proposition]:
    def _check_pure(conjunct, var_is_pure_dict: dict[Var:bool]) -> None:
        match conjunct:
            case Var():
                if Negate(conjunct) in var_is_pure_dict.keys():
                    var_is_pure_dict[Negate(conjunct)] = False
                else:
                    var_is_pure_dict[conjunct] = True
            case Not(val=p):
                if isinstance(p, Var):
                    if p in var_is_pure_dict.keys():
                        var_is_pure_dict[p] = False
                    else:
                        var_is_pure_dict[conjunct] = True
                else:
                    _check_pure(p, var_is_pure_dict)
            case And(values=(p1, p2)) | Or(values=(p1, p2)):
                _check_pure(p1, var_is_pure_dict)
                _check_pure(p2, var_is_pure_dict)

    var_is_pure_dict: dict[Var:bool] = {}
    for conjunct in S:
        _check_pure(conjunct, var_is_pure_dict)

    return list(map(lambda x: x[0], filter(lambda x: x[1], var_is_pure_dict.items())))


def EliminatePureLiteral(
    conjunct: Proposition, l: Proposition
) -> Optional[Proposition]:
    def _walk_remove(conjunct, l):
        match conjunct:
            case Var():
                if conjunct == l:
                    return None
                return conjunct

            case Not(val=p):
                if p == l.val:
                    return None
                return conjunct

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
                        return conjunct

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
                        return conjunct

    return _walk_remove(conjunct, l)


def UnitPropagate(S: list[Proposition], l: Proposition) -> list[Proposition]:
    def _no_literal_in_conjunct(conjunct):
        return not literal_exists_in_conjunct(conjunct, l)

    def _eliminate_pure_in_S(S):
        return EliminatePureLiteral(S, Negate(l))

    return list(map(_eliminate_pure_in_S, list(filter(_no_literal_in_conjunct, S))))


def ChooseLiteral(S) -> Var:
    # pick first
    return literals_in_conjunct(S[0])[0]


def DPLL(S, M) -> SAT | UNSAT:
    if not S:
        return SAT(M)
    if None in S:
        return UNSAT(S)

    for literal in single_literals(S):  # распространение юницикличного дизъюнкта
        S = UnitPropagate(S, literal)
        M[literal] = True

    for literal in pure_literals(S):
        S = rm_conjunct_if_contains_literal(S, literal)
        M[literal] = True

    if not S:
        return SAT(M)
    if None in S:
        return UNSAT(S)

    literal = ChooseLiteral(S)

    positive_literal_M = M.copy()
    positive_literal_M[literal] = True

    guessed_result = DPLL([*S, literal], positive_literal_M)
    if isinstance(guessed_result, SAT):
        return guessed_result
    else:
        negative_literal_M = M.copy()  # potential source of error? TODO: check
        negative_literal_M[literal] = False
        return DPLL([*S, Negate(literal)], negative_literal_M)


def main():
    q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")

    # formula = Or(q1, And(q2, q3))
    formula = And(q1, And(q2, Negate(q3)))
    # formula = And(q1, Negate(Negate(q1)))
    # formula = And(q1, Not(q1))
    print(f"{se(formula)=}")

    cnf = create_cnf(formula)
    print(f"{se(cnf)=}")

    match DPLL(cnf, {}):
        case SAT(model=model):
            print("SAT")
            for k, v in model.items():
                print(se(k), "->", v)
        case UNSAT(S=s):
            print("UNSAT")
            pe(s)


if __name__ == "__main__":
    main()
