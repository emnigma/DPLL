import unittest

from utils import pe, se

from logic import Var, And, Or, Negate as Not
from dpll import Model, literal_exists_in_conjuction, literals_in_conjuction
from dpll import single_literals
from dpll import pure_literals
from dpll import rm_conjuction_if_contains_literal
from dpll import EliminatePureLiteral
from dpll import UnitPropagate
from cnf import create_cnf
from dpll import SAT, UNSAT, DPLL


class TestDPLL(unittest.TestCase):
    def test_not_parity(self):
        q1 = Var("q1")

        self.assertIs(q1, Not(Not(q1)))
        self.assertIs(q1, Not(Not(Not(Not(q1)))))
        self.assertNotEqual(q1, (Not(q1)))
        self.assertNotEqual(q1, Not(Not(Not(q1))))

    def test_cnf(self):
        # lecture example
        q1, q2, q3, p1, p2 = Var("q1"), Var("q2"), Var("q3"), Var("p1"), Var("p2")

        formula = Not(And(q1, Or(q2, Not(q3))))
        cnf = create_cnf(formula)
        expected = [
            Not(p2),
            Or(Or(q2, Not(q3)), Not(p1)),
            Or(Not(q2), p1),
            Or(q3, p1),
            Or(Not(p2), q1),
            Or(Not(p2), p1),
            Or(Or(Not(q1), Not(p1)), p2),
        ]

        self.assertEqual(set(cnf), set(expected))

    def test_get_all_literals_in_conjuction(self):

        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        formula = Not(And(q1, Or(q2, Not(Not(q3)))))

        literals = literals_in_conjuction(formula)
        expected = [q1, q2, Not(Not(q3))]

        self.assertEqual(set(literals), set(expected))

    def test_literal_exists_in_conjuction(self):
        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        formula = And(Not(q1), And(Not(Not(q1)), And(Not(Not(Not(q1))), q2)))

        existing = map(
            lambda l: literal_exists_in_conjuction(formula, l), [q1, Not(q1), q2, q3]
        )
        expected = [True, True, True, False]

        self.assertEqual(set(existing), set(expected))

    def test_get_single_literals(self):

        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        formula = Not(And(q1, Or(q2, Not(q3))))

        singles = single_literals([Not(q1), formula, q3])
        expected = [Not(q1), q3]

        self.assertEqual(set(singles), set(expected))

    def test_get_pure_literals(self):
        a, b, c, d = Var("a"), Var("b"), Var("c"), Var("d")

        test_set = [
            (
                [
                    Or(b, c),
                    Or(c, d),
                    Or(c, Not(d)),
                    Or(Not(c), d),
                    Or(a, Or(Not(c), Not(d))),
                    Or(Not(b), Or(Not(c), d)),
                    Or(Not(a), Or(b, Not(c))),
                    Or(Not(a), Or(Not(b), c)),
                ],
                [],
            ),
            ([c, And(b, Not(c)), Not(And(a, Or(Not(b), c))), a], [a]),
        ]

        for f, expected in test_set:
            self.assertEqual(pure_literals(f), expected)

    def test_rm_conjuction_if_contains_literal(self):

        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        c1 = Or(q1, q2)
        c2 = And(Not(q2), Or(q1, q3))
        c3 = And(Not(q1), q2)

        self.assertEqual(rm_conjuction_if_contains_literal([c1, c2, c3], q1), [c3])
        self.assertEqual(rm_conjuction_if_contains_literal([c1, c2, c3], q2), [c2])
        self.assertEqual(
            rm_conjuction_if_contains_literal([c1, c2, c3], Not(q1)), [c1, c2]
        )

    def test_eliminate_pure_literal1(self):
        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")

        test_set = [
            ([Or(q1, q2)], q1, [q2]),
            ([q1, Or(q1, q2), Not(q3)], Not(q3), [q1, Or(q1, q2), None]),
            ([Or(q2, Not(Not(q3))), q1], Not(q3), [Or(q2, Not(Not(q3))), q1]),
        ]

        for cnf, l, expected in test_set:
            self.assertEqual(
                list(map(lambda c: EliminatePureLiteral(c, l), cnf)), expected
            )

    def test_unit_propagate(self):
        # ???????????? ?????? ??????????????????, ?? ?????????????? ???????????? l, ???????????????????? ?????? !l ???? ????????????????????
        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        a, c, d = Var("a"), Var("c"), Var("d")
        test_set = [
            ([q1], q1, []),
            ([q1], Not(q1), [None]),
            ([q1, Or(Not(q1), q2), Not(q3)], q1, [q2, Not(q3)]),
            ([q1, Or(q1, q2), Not(q3)], q1, [Not(q3)]),
            ([Or(a, Or(Not(c), d))], c, [Or(a, d)]),
        ]

        for cnf, l, expected in test_set:
            self.assertEqual(UnitPropagate(cnf, l), expected)

    def test_model(self):
        q1, q2 = Var("q1"), Var("q2")
        m = Model()

        m.add(q1, True)
        m.add(q2, False)

        self.assertEqual({q1: True, q2: False}, m.inner)

    def _test_dpll_sat_unsat(self):
        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")

        test_set = map(
            lambda x: (create_cnf(x[0]), x[1]),
            [
                (And(q1, Not(q1)), UNSAT),  # q1 ^ !q1
                (And(q1, Not(Not(q1))), SAT),  # q1 ^ !!q1
                (Not(And(q1, And(q2, Not(q3)))), SAT),  # q1 ^ (q2 ^ !q3)
            ],
        )

        for formula, expected in test_set:
            self.assertIsInstance(DPLL(formula, Model()), expected)

    def test_lecture_dpll(self):
        a, b, c, d = Var("a"), Var("b"), Var("c"), Var("d")
        phi = [
            Or(Not(a), Or(b, c)),
            Or(a, Or(c, d)),
            Or(a, Or(c, Not(d))),
            Or(a, Or(Not(c), d)),
            Or(a, Or(Not(c), Not(d))),
            Or(Not(b), Or(Not(c), d)),
            Or(Not(a), Or(b, Not(c))),
            Or(Not(a), Or(Not(b), c)),
        ]

        result = DPLL(phi, Model())
        self.assertIsInstance(result, SAT)

        self.assertEqual(result.model.inner, {a: True, b: True, c: True, d: True})


def main():
    unittest.main()


if __name__ == "__main__":
    main()
