from logic import Var, Not, Or, And, Negate as Not, Imp, Eq
from utils import se, pe
from cnf import create_cnf
from dpll import DPLL, Model, SAT, UNSAT


def main():
    p, q, r = Var("p"), Var("q"), Var("r")

    formula_from_task3a = Eq(Imp(p, q), Imp(Not(q), Not(p)))
    formula_from_task3b = Eq(Imp(p, Imp(q, r)), Imp(Not(r), Imp(Not(q), Not(p))))

    formula_from_task4 = Not(Imp(Not(And(p, q)), Not(r)))  # !((p ^ q) v !r)

    def solve(task, formula):
        print(f"### task: {task} ###")
        print(f"{se(formula)=}")

        cnf = create_cnf(formula)

        print(f"{se(cnf)=}")

        match DPLL(cnf, Model()):
            case SAT(model=model):
                print("SAT")
                model.pe()
            case UNSAT():
                print("UNSAT")
        print()

    solve("3a", formula_from_task3a)
    solve("3a negated", Not(formula_from_task3a))
    solve("3b", formula_from_task3b)
    solve("4", formula_from_task4)


if __name__ == "__main__":
    main()
