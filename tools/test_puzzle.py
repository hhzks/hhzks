"""Unit tests for deterministic daily puzzle selection (spec §4)."""

import datetime as dt
import unittest

import lightsout as lo
import puzzle


class TestSeed(unittest.TestCase):
    def test_seed_is_derived_from_the_date(self):
        self.assertEqual(
            puzzle.seed_for(dt.date(2026, 8, 4)),
            puzzle.seed_for(dt.date(2026, 8, 4)),
        )

    def test_different_dates_give_different_seeds(self):
        self.assertNotEqual(
            puzzle.seed_for(dt.date(2026, 8, 4)),
            puzzle.seed_for(dt.date(2026, 8, 5)),
        )


class TestTrivialBoards(unittest.TestCase):
    def test_all_on_is_rejected(self):
        self.assertTrue(puzzle.is_trivial(0xFFFF))

    def test_all_off_is_rejected(self):
        self.assertTrue(puzzle.is_trivial(0x0000))

    def test_single_rows_are_rejected(self):
        for row in (0x000F, 0x00F0, 0x0F00, 0xF000):
            self.assertTrue(puzzle.is_trivial(row), f"{row:04x}")

    def test_single_columns_are_rejected(self):
        for col in (0x1111, 0x2222, 0x4444, 0x8888):
            self.assertTrue(puzzle.is_trivial(col), f"{col:04x}")

    def test_four_corners_are_rejected(self):
        self.assertTrue(puzzle.is_trivial(0x9009))

    def test_checkerboards_are_rejected(self):
        self.assertTrue(puzzle.is_trivial(0x5A5A))
        self.assertTrue(puzzle.is_trivial(0xA5A5))

    def test_an_ordinary_scattered_board_is_kept(self):
        self.assertFalse(puzzle.is_trivial(0x3A17))


class TestCandidates(unittest.TestCase):
    def test_candidates_are_limited_to_the_difficulty_band(self):
        for state in puzzle.candidates():
            self.assertGreaterEqual(lo.min_clicks(state), puzzle.BAND[0])
            self.assertLessEqual(lo.min_clicks(state), puzzle.BAND[1])

    def test_candidates_exclude_trivial_boards(self):
        self.assertFalse(any(puzzle.is_trivial(s) for s in puzzle.candidates()))

    def test_every_candidate_is_solvable(self):
        for state in puzzle.candidates():
            self.assertTrue(lo.is_solvable(state))

    def test_there_are_enough_candidates_for_years_of_puzzles(self):
        self.assertGreater(len(puzzle.candidates()), 1000)


class TestDailySelection(unittest.TestCase):
    def test_selection_is_reproducible_for_a_given_date(self):
        day = dt.date(2026, 8, 4)
        self.assertEqual(puzzle.for_date(day).start, puzzle.for_date(day).start)

    def test_a_year_of_puzzles_all_land_inside_the_band(self):
        day = dt.date(2026, 1, 1)
        for _ in range(365):
            p = puzzle.for_date(day)
            self.assertTrue(puzzle.BAND[0] <= p.min_clicks <= puzzle.BAND[1], day)
            day += dt.timedelta(days=1)

    def test_a_year_of_puzzles_is_never_trivial(self):
        day = dt.date(2026, 1, 1)
        for _ in range(365):
            self.assertFalse(puzzle.is_trivial(puzzle.for_date(day).start), day)
            day += dt.timedelta(days=1)

    def test_no_puzzle_repeats_within_the_exclusion_window(self):
        day = dt.date(2026, 1, 1)
        recent = []
        for _ in range(400):
            start = puzzle.for_date(day).start
            self.assertNotIn(start, recent, f"{start:04x} repeated on {day}")
            recent = ([start] + recent)[: puzzle.REPEAT_WINDOW]
            day += dt.timedelta(days=1)

    def test_puzzle_carries_a_solution_that_clears_its_board(self):
        p = puzzle.for_date(dt.date(2026, 8, 4))
        self.assertEqual(lo.apply(p.start, p.solution), 0x0000)
        self.assertEqual(p.solution.bit_count(), p.min_clicks)

    def test_puzzle_knows_its_own_date(self):
        self.assertEqual(puzzle.for_date(dt.date(2026, 8, 4)).date, dt.date(2026, 8, 4))


if __name__ == "__main__":
    unittest.main()
