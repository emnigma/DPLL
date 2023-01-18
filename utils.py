from logic import Var, Or, And, Not, Proposition


def se(e):
    def _se(expression, accumulator: list[str]):
        match expression:
            case Var(val=p):
                accumulator.append(p)

            case Not(val=p):
                accumulator.append("!")
                _se(p, accumulator)

            case And(values=(p1, p2)):
                accumulator.append("(")
                _se(p1, accumulator)
                accumulator.append(" ^ ")
                _se(p2, accumulator)
                accumulator.append(")")

            case Or(values=(p1, p2)):
                accumulator.append("(")
                _se(p1, accumulator)
                accumulator.append(" v ")
                _se(p2, accumulator)
                accumulator.append(")")

            case None:
                accumulator.append("□")
        return accumulator

    match e:
        case Proposition() | None:
            return "".join(_se(e, []))
        case [*vals]:
            return " ^ ".join(se(val) for val in vals)
        case _:
            raise RuntimeError("Dummy")


def pe(e):
    print(se(e))
