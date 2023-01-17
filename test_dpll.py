from unittest import TestCase
import unittest

from utils import pe

from logic import Var, Not, And, Or
from dpll import literals_in_conjunct
from dpll import single_literals
from dpll import pure_literals
from dpll import rm_conjunct_if_contains_literal
from dpll import EliminatePureLiteral
from dpll import UnitPropagate
from cnf import create_cnf
from dpll import SAT, UNSAT, DPLL


class TestDPLL(TestCase):
    def test_get_all_literals_in_conjunct(self):

        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        formula = Not(And(q1, Or(q2, Not(q3))))

        literals = literals_in_conjunct(formula)
        expected = [q1, q2, Not(q3)]

        self.assertEqual(set(literals), set(expected))

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

        cnf = [q1, Or(q1, q2), Not(q3)]  # q1 ^ (q1 v q2) ^ !q3

        eliminated = list(map(lambda S: EliminatePureLiteral(S, Not(q3)), cnf))
        expected = [q1, Or(q1, q2), None]

        self.assertEqual(eliminated, expected)

    def test_eliminate_pure_literal2(self):
        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")

        cnf = [Or(q1, q2)]  # (q1 v q2)

        eliminated = list(map(lambda S: EliminatePureLiteral(S, q1), cnf))
        expected = [q2]

        self.assertEqual(eliminated, expected)

    def _test_unit_propagate(self):

        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        cnf = [q1, Or(q1, q2), Not(q3)]  # q1 ^ (q1 v q2) ^ !q3

        propagated = UnitPropagate(cnf, q1)
        expected = [None, q2, Not(q3)]

        pe(propagated)
        pe(expected)

    def test_dpll_sat_unsat(self):
        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")

        test_set = map(
            lambda x: (create_cnf(x[0]), x[1]),
            [
                (And(q1, Not(q1)), UNSAT),  # q1 ^ !q1
                (And(q1, Not(Not(q1))), SAT),  # q1 ^ !!q1
            ],
        )

        for formula, expected in test_set:
            self.assertIsInstance(DPLL(formula, {}), expected)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
