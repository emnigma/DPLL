from logic import Var, Not, Or, And, Negate as Not
from utils import se, pe
from cnf import create_cnf
from dpll import DPLL, Model, SAT, UNSAT


def main():
    q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
    formula = Not(And(q1, Or(q2, Not(q3))))  # !(q1 ^ (q2 v !q3))

    print(f"{se(formula)=}")

    cnf = create_cnf(formula)

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
