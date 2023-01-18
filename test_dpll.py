from unittest import TestCase
import unittest

from utils import pe, se

from logic import Var, And, Or, Negate as Not
from dpll import Model, literal_exists_in_conjunct, literals_in_conjunct
from dpll import single_literals
from dpll import pure_literals
from dpll import rm_conjunct_if_contains_literal
from dpll import EliminatePureLiteral
from dpll import UnitPropagate
from cnf import create_cnf
from dpll import SAT, UNSAT, DPLL


class TestDPLL(TestCase):
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

    def test_get_all_literals_in_conjunct(self):

        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        formula = Not(And(q1, Or(q2, Not(Not(q3)))))

        literals = literals_in_conjunct(formula)
        expected = [q1, q2, Not(Not(q3))]

        self.assertEqual(set(literals), set(expected))

    def test_literal_exists_in_conjunct(self):
        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        formula = And(Not(q1), And(Not(Not(q1)), And(Not(Not(Not(q1))), q2)))

        existing = map(
            lambda l: literal_exists_in_conjunct(formula, l), [q1, Not(q1), q2, q3]
        )
        expected = [True, True, True, False]

        self.assertEqual(set(existing), set(expected))

    def test_get_single_literals(self):

        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        formula = Not(And(q1, Or(q2, Not(q3))))

        singles = single_literals([q1, formula, q3])
        expected = [q1, q3]

        self.assertEqual(set(singles), set(expected))

    def test_get_pure_literals(self):

        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        formula = Not(And(q1, Or(q2, Not(q3))))

        single_literals = pure_literals([q3, Not(q2), formula])
        expected = [q1]

        self.assertEqual(set(single_literals), set(expected))

    def test_rm_conjunct_if_contains_literal(self):

        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        c1 = Or(q1, q2)
        c2 = And(Not(q2), Or(q1, q3))
        c3 = And(Not(q1), q2)

        self.assertEqual(rm_conjunct_if_contains_literal([c1, c2, c3], q1), [c3])
        self.assertEqual(rm_conjunct_if_contains_literal([c1, c2, c3], q2), [c2])
        self.assertEqual(
            rm_conjunct_if_contains_literal([c1, c2, c3], Not(q1)), [c1, c2]
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
        # убрать все дизъюнкты, в которые входит l, вычеркнуть все !l из оставшихся
        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        test_set = [
            ([q1], q1, []),
            ([q1], Not(q1), [None]),
            ([q1, Or(Not(q1), q2), Not(q3)], q1, [q2, Not(q3)]),
            ([q1, Or(q1, q2), Not(q3)], q1, [Not(q3)]),
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
            self.assertIsInstance(DPLL(formula, {}), expected)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
