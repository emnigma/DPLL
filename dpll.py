from logic import Var, Not, Or, And, Proposition
from utils import pe, se
from cnf import create_CNF


class SAT:
    def __init__(self, model: dict[Var:bool]) -> None:
        self.model = model


class UNSAT:
    pass


class EmptyDisjunct:
    pass


def literals_in_conjunct(conjunct: Proposition) -> list[Var]:
    def _literals_in_conjunct(conjunct, accumulator):
        match conjunct:
            case Var():
                accumulator.append(conjunct)
            case Not(val=p):
                if isinstance(p, Var):
                    accumulator.append(conjunct)
                else:
                    _literals_in_conjunct(p, accumulator)
            case And(values=(p1, p2)) | Or(values=(p1, p2)):
                _literals_in_conjunct(p1, accumulator)
                _literals_in_conjunct(p2, accumulator)

        return accumulator

    return _literals_in_conjunct(conjunct, [])


def literal_exists_in_conjunct(literal, conjunct: Proposition) -> bool:
    return literal in literals_in_conjunct(conjunct)


def rm_conjunct_if_contains_literal(literal, S: list[Proposition]) -> list[Proposition]:
    def _no_literal_in_conjunct(conjunct):
        return not literal_exists_in_conjunct(literal, conjunct)

    return list(filter(_no_literal_in_conjunct, S))


def single_literals(S: list[Proposition]) -> list[Var]:
    return list(filter(lambda p: isinstance(p, Var), S))


def pure_literals(S: list[Proposition]) -> list[Proposition]:
    def _check_pure(conjunct, var_is_pure_dict: dict[Var:bool]) -> None:
        match conjunct:
            case Var():
                if Not(conjunct) in var_is_pure_dict.keys():
                    var_is_pure_dict[Not(conjunct)] = False
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


def EliminatePureLiteral(S: list[Proposition], l: Proposition) -> list[Proposition]:
    S.remove(l)
    return S


def UnitPropagate(S: list[Proposition], l: Proposition) -> list[Proposition]:
    def _no_literal_in_conjunct(conjunct):
        return not literal_exists_in_conjunct(l, conjunct)

    return EliminatePureLiteral(
        list(filter(_no_literal_in_conjunct, S)), Not(l)
    )


def ChooseLiteral(S) -> Var:
    # pick first
    return literals_in_conjunct(S[0])[0]


def DPLL(S, M) -> SAT | UNSAT:
    if not S:
        return SAT(M)
    if EmptyDisjunct in S:
        return UNSAT

    for literal in single_literals(S):
        S = UnitPropagate(S, literal)
        M[literal] = True

    for literal in pure_literals(S):
        S = rm_conjunct_if_contains_literal(literal, S)
        M[literal] = True

    if not S:
        return SAT(M)
    if EmptyDisjunct in S:
        return UNSAT

    literal = ChooseLiteral(S)

    positive_literal_M = M.copy()
    positive_literal_M[literal] = True

    guessed_result = DPLL([*S, literal], positive_literal_M)
    if isinstance(guessed_result, SAT):
        return guessed_result
    else:
        negative_literal_M = M.copy()
        negative_literal_M[literal] = False
        return DPLL([*S, literal], negative_literal_M)


def main():
    q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")

    formula = Not(Or(q1, And(q2, Not(q3))))
    # formula = And(q1, Not(Not(q1)))
    pe(formula)
    
    cnf = create_CNF(formula)
    pe(cnf)

    sat = DPLL(cnf, {})

    print(sat.model)
    for k, v in sat.model.items():
        print(se(k), v)


if __name__ == "__main__":
    main()
