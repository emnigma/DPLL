from logic import Var, Or, And, Not
from utils import pe

count = -1


def get_next_index():
    global count
    count += 1
    return str(count)


def CNF(phi, delta):
    match phi:
        case Var():
            return (phi, delta)

        case Not(val=p):
            l, delta_stroke = CNF(p, delta)
            return (Not(l), delta_stroke)

        case And(values=(p1, p2)):
            l1, delta1 = CNF(p1, delta)
            l2, delta2 = CNF(p2, delta1)
            p = Var("p" + get_next_index())
            delta_stroke = delta2 + [
                Or(Or(l1, l2), Not(p)),
                Or(Not(l1), p),
                Or(Not(l2), p),
            ]

            return (p, delta_stroke)

        case Or(values=(p1, p2)):
            l1, delta1 = CNF(p1, delta)
            l2, delta2 = CNF(p2, delta1)
            p = Var("p" + get_next_index())
            delta_stroke = delta2 + [
                Or(Or(l1, l2), Not(p)),
                Or(Not(l1), p),
                Or(Not(l2), p),
            ]

            return (p, delta_stroke)
    raise RuntimeError


def create_CNF(formula):
    phi, delta = CNF(formula, [])
    return [phi, *delta]


def main():
    q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")

    formula = Not(And(q1, Or(q2, Not(q3))))
    
    for item in create_CNF(formula):
        pe(item)


if __name__ == "__main__":
    main()
