from logic import Proposition, Var, Or, And, Negate as Not, Imp, Eq
from utils import se, pe
from cnf import create_cnf
from dpll import DPLL, Model, SAT, UNSAT

import z3


def accumulate_items(array, bin_op):
    if len(array) == 1:
        return array[0]

    accumulator = None
    for conjunct in array:
        if accumulator == None:
            accumulator = conjunct
        else:
            accumulator = bin_op(accumulator, conjunct)

    return accumulator


def problem_z3(k, v_size):

    vertexes = [f"p{i}" for i in range(v_size)]
    edges: set[tuple[str, str]] = set()
    for v1 in vertexes:
        for v2 in vertexes:
            if (v2, v1) in edges or v1 == v2:
                continue

            edges.add((v1, v2))

    def get_edge(e: tuple[str, str], c):
        v1, v2 = sorted(list(e))

        if (v1, v2) not in edges:
            raise RuntimeError

        return z3.Bool(f"e_{c}_{v1}_{v2}")

    edges_colored: dict[z3.Bool : tuple(str, str)] = dict()

    for v1, v2 in edges:
        for c in range(k):
            edges_colored[z3.Bool(f"e_{c}_{v1}_{v2}")] = (v1, v2)

    colored = []
    for edge in edges:
        inner = []
        for c in range(k):
            p = get_edge(edge, c)
            inner.append(p)

        colored.append(z3.Or(*inner))
    colored = z3.And(*colored)

    colored_unique = []
    for edge in edges:
        for c in range(k):
            p = get_edge(edge, c)

            inner = []
            for c_s in range(k):
                if c_s == c:
                    continue
                p_s = get_edge(edge, c_s)
                inner.append(z3.Not(p_s))
            inner = z3.Implies(p, z3.And(*inner))

            colored_unique.append(inner)
    colored_unique = z3.And(*colored_unique)

    visited: set[tuple[str, str, str]] = set()
    task = []
    for v1 in vertexes:
        for v2 in vertexes:
            for v3 in vertexes:
                vs = tuple(sorted((v1, v2, v3)))
                if len(set(vs)) != 3:
                    continue
                if vs in visited:
                    continue

                for c in range(k):
                    p_u_c = get_edge((v1, v2), c)
                    p_v_c = get_edge((v2, v3), c)
                    p_g_c = get_edge((v1, v3), c)
                    task.append(z3.Implies(p_u_c, z3.Or(z3.Not(p_v_c), z3.Not(p_g_c))))
                    task.append(z3.Implies(p_v_c, z3.Or(z3.Not(p_u_c), z3.Not(p_g_c))))
                    task.append(z3.Implies(p_g_c, z3.Or(z3.Not(p_v_c), z3.Not(p_u_c))))

                visited.add(vs)

    task = z3.And(*task)
    return z3.And(colored, colored_unique, task)


def problem_manual(k, v_size):

    vertexes = [f"p{i}" for i in range(v_size)]
    edges: set[tuple[str, str]] = set()
    for v1 in vertexes:
        for v2 in vertexes:
            if (v2, v1) in edges or v1 == v2:
                continue

            edges.add((v1, v2))

    def get_edge(e: tuple[str, str], c):
        v1, v2 = sorted(list(e))

        if (v1, v2) not in edges:
            raise RuntimeError

        return Var(f"e_{c}_{v1}_{v2}")

    edges_colored: dict[Var : tuple(str, str)] = dict()

    for v1, v2 in edges:
        for c in range(k):
            edges_colored[Var(f"e_{c}_{v1}_{v2}")] = (v1, v2)

    colored = []
    for edge in edges:
        inner = []
        for c in range(k):
            p = get_edge(edge, c)
            inner.append(p)

        # colored.append(z3.Or(*inner))
        colored.append(accumulate_items(inner, Or))
    # colored = z3.And(*colored)
    colored = accumulate_items(colored, And)

    colored_unique = []
    for edge in edges:
        for c in range(k):
            p = get_edge(edge, c)

            inner = []
            for c_s in range(k):
                if c_s == c:
                    continue
                p_s = get_edge(edge, c_s)
                inner.append(Not(p_s))

            # inner = Imp(p, And(*inner))
            if inner:
                inner = Imp(p, accumulate_items(inner, And))
                colored_unique.append(inner)

    # colored_unique = z3.And(*colored_unique)
    colored_unique = accumulate_items(colored_unique, And)

    visited: set[tuple[str, str, str]] = set()
    task = []
    for v1 in vertexes:
        for v2 in vertexes:
            for v3 in vertexes:
                vs = tuple(sorted((v1, v2, v3)))
                if len(set(vs)) != 3:
                    continue
                if vs in visited:
                    continue

                for c in range(k):
                    p_u_c = get_edge((v1, v2), c)
                    p_v_c = get_edge((v2, v3), c)
                    p_g_c = get_edge((v1, v3), c)
                    task.append(Imp(p_u_c, Or(Not(p_v_c), Not(p_g_c))))
                    task.append(Imp(p_v_c, Or(Not(p_u_c), Not(p_g_c))))
                    task.append(Imp(p_g_c, Or(Not(p_v_c), Not(p_u_c))))

                visited.add(vs)

    # task = z3.And(*task)
    task = accumulate_items(task, And)

    # return z3.And(colored, colored_unique, task)

    res = None
    if colored != None:
        res = colored
    if colored_unique != None:
        res = And(res, colored_unique)
    if task != None:
        res = And(res, task)

    if res == None:
        # чтобы вернуть True
        return And(Var("True_var"), Var("True_var"))

    return res


def main():
    s = z3.Solver()
    f = problem_z3(k=2, v_size=7)
    s.add(f)
    if s.check() == z3.sat:
        print(s.model())
    else:
        print(s.check())


def main_man(k=2, v_size=4):
    def solve(formula):
        print("manual DPLL:")
        print(f"### task: {k=}, {v_size=} ###")
        # print(f"{se(formula)=}")

        cnf = create_cnf(formula)

        # print(f"{se(cnf)=}")

        res = DPLL(cnf, Model())
        match res:
            case SAT(model=model):
                print("SAT")
                model.pe()
            case UNSAT():
                print("UNSAT")
        return res

    # 5 -> unsat
    # 6 -> unsat
    f = problem_manual(k=k, v_size=v_size)

    return(solve(f))


def z3_main(k, v_size):
    print("z3 solver:")
    print(f"### task: {k=}, {v_size=} ###")
    s = z3.Solver()
    f = problem_z3(k=k, v_size=v_size)
    s.add(f)
    if s.check() == z3.sat:
        print(s.model())
    else:
        print(s.check())
    return s.check()


if __name__ == "__main__":

    k = 1
    sat = True
    max_v_size = 0

    # еще можно бинпоиском, но эффективность спорна
    while sat:
        k, v_size = k, max_v_size + 1

        manual_res = main_man(k, v_size)
        z3_res = z3_main(k, v_size)

        if (
            manual_res == UNSAT
            and z3_res == z3.sat
            or type(manual_res) == SAT
            and z3_res == z3.unsat
        ):
            raise RuntimeError("Results does not match!")

        if z3_res == z3.unsat or manual_res == UNSAT:
            sat = False
        else:
            max_v_size += 1


    print(max_v_size)
