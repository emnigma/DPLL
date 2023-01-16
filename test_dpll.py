from unittest import TestCase
import unittest

from utils import pe

from logic import Var, Not, And, Or
from dpll import literals_in_conjunct
from dpll import single_literals
from dpll import pure_literals
from dpll import rm_conjunct_if_contains_literal
from dpll import DPLL


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

        self.assertEqual(rm_conjunct_if_contains_literal(q1, [c1, c2, c3]), [c3])
        self.assertEqual(rm_conjunct_if_contains_literal(q2, [c1, c2, c3]), [c2])
        self.assertEqual(
            rm_conjunct_if_contains_literal(Not(q2), [c1, c2, c3]), [c1, c3]
        )

    def test_dpll(self):
        q1, q2, q3 = Var("q1"), Var("q2"), Var("q3")
        f1 = Not(Or(q1, And(q2, Not(q3))))  # !(q1 v (q2 ^ !q3))
        f2 = And(q1, Not(q1))

        DPLL(f1)
        DPLL(f2)




def main():
    unittest.main()


if __name__ == "__main__":
    main()
