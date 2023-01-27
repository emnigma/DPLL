#!/usr/bin/python3

import itertools
import z3


def generate_n_pos_indexes(array_len: int, n_negatives: int):
    positive_indexes = set(
        itertools.combinations([i for i in range(array_len)], n_negatives)
    )
    return positive_indexes


def popcount_n(literals: list, n: int):
    for pos_indexes in generate_n_pos_indexes(len(literals), n):
        new_array = literals.copy()

        for i in range(len(new_array)):
            if i not in pos_indexes:
                new_array[i] = z3.Not(new_array[i])

        yield new_array


def z3_coords_to_var(row, col):
    return z3.Bool(f"p_{row}_{col}")


def chk_bomb(field, row, col):
    HEIGHT, WIDTH = len(field), len(field[0])
    s = z3.Solver()
    s.set(unsat_core=True)

    # make empty border
    # all variables are negated (because they must be False)
    visited_border_constraints = set()
    for c in range(WIDTH + 2):

        s.assert_and_track(z3.Not(z3_coords_to_var(0, c)), f"border_{0}_{c}")
        visited_border_constraints.add(f"border_{0}_{c}")
        s.assert_and_track(
            z3.Not(z3_coords_to_var(HEIGHT + 1, c)), f"border_{HEIGHT + 1}_{c}"
        )
        visited_border_constraints.add(f"border_{HEIGHT + 1}_{c}")

    for r in range(HEIGHT + 2):
        # clauses.append("-" + coords_to_var(r, 0))
        # clauses.append("-" + coords_to_var(r, WIDTH + 1))

        if f"border_{r}_{0}" not in visited_border_constraints:
            s.assert_and_track(z3.Not(z3_coords_to_var(r, 0)), f"border_{r}_{0}")
        if f"border_{r}_{WIDTH + 1}" not in visited_border_constraints:
            s.assert_and_track(
                z3.Not(z3_coords_to_var(r, WIDTH + 1)), f"border_{r}_{WIDTH + 1}"
            )

    for r in range(1, HEIGHT + 1):
        for c in range(1, WIDTH + 1):
            t = field[r - 1][c - 1]
            if t in "012345678":
                # cell at r, c (in which we are standing now) is empty (False):
                s.assert_and_track(z3.Not(z3_coords_to_var(r, c)), f"!p_{r}_{c}")
                # we need an empty border so the following expression would work for all possible cells:
                neighbours = [
                    z3_coords_to_var(r - 1, c - 1),
                    z3_coords_to_var(r - 1, c),
                    z3_coords_to_var(r - 1, c + 1),
                    z3_coords_to_var(r, c - 1),
                    z3_coords_to_var(r, c + 1),
                    z3_coords_to_var(r + 1, c - 1),
                    z3_coords_to_var(r + 1, c),
                    z3_coords_to_var(r + 1, c + 1),
                ]

                conjs = []
                for conj in popcount_n(neighbours, int(t)):
                    conjs.append(z3.And(*conj))
                conjs = z3.Or(*conjs)
                s.assert_and_track(conjs, f"p_{r}_{c}_has_{int(t)}_nei")

    # place a bomb
    s.assert_and_track(z3_coords_to_var(row, col), f"bomb_{row}_{col}")

    if s.check() == z3.unsat:
        print("row=%d, col=%d, unsat!" % (row, col))
        # print(s.unsat_core())
    # else:
    # print("row=%d, col=%d, sat!" % (row, col))
    # print(s.model())
    return s.check()


def check_field(field):
    for r in range(1, len(field) + 1):
        for c in range(1, len(field[0]) + 1):
            if field[r - 1][c - 1] == "?":
                chk_bomb(field, r, c)


field0 = ["1?1", "111", "00?"]  # ok
field2 = [
    "01?10001?",
    "01?100011",
    "011100000",
    "000000000",
    "111110011",
    "????1001?",
    "????3101?",
    "?????211?",
    "?????????",
]  # ok
field4 = ["?0"]  # ok
field5 = ["0?0"]  # ok
field6 = ["?0?"]  # ok
field7 = ["1?"]  # ok
field8 = ["1?", "?1"]  # ok
field9 = ["232", "???", "232"]  # ok
field10 = ["23", "??"]  # ok


def main():

    check_field(field2)


def test():
    test_cases = [
        (1, 3, True),
        (6, 2, True),
        (6, 3, True),
        (7, 4, True),
        (7, 9, True),
        (8, 9, True),
        (1, 9, False),
        (9, 1, False),
        (6, 9, False),
    ]

    for row, col, no_bomb in test_cases:
        assert (chk_bomb(field2, row, col) == z3.unsat) == no_bomb


if __name__ == "__main__":
    test()
