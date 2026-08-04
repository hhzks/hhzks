"""Unit tests for the core Lights Out maths (spec §3, §10 step 1)."""

import unittest

import lightsout as lo


class TestClickMasks(unittest.TestCase):
    def test_there_are_sixteen_masks(self):
        self.assertEqual(len(lo.MASKS), 16)

    def test_corner_mask_covers_cell_and_two_orthogonal_neighbours(self):
        # cell 0 is top-left: itself (0), right (1), below (4)
        self.assertEqual(lo.MASKS[0], (1 << 0) | (1 << 1) | (1 << 4))

    def test_interior_mask_covers_cell_and_four_orthogonal_neighbours(self):
        # cell 5 is row 1, col 1: itself (5), up (1), down (9), left (4), right (6)
        expected = (1 << 5) | (1 << 1) | (1 << 9) | (1 << 4) | (1 << 6)
        self.assertEqual(lo.MASKS[5], expected)

    def test_bottom_right_mask_does_not_wrap_around(self):
        # cell 15: itself (15), up (11), left (14) -- and nothing on row 0 or col 0
        self.assertEqual(lo.MASKS[15], (1 << 15) | (1 << 11) | (1 << 14))

    def test_every_mask_fits_in_sixteen_bits(self):
        for i, mask in enumerate(lo.MASKS):
            self.assertEqual(mask & ~0xFFFF, 0, f"mask {i} has bits above 16")

    def test_masks_are_symmetric(self):
        # cell i toggles cell j iff cell j toggles cell i
        for i in range(16):
            for j in range(16):
                self.assertEqual(
                    bool(lo.MASKS[i] >> j & 1),
                    bool(lo.MASKS[j] >> i & 1),
                    f"asymmetry between {i} and {j}",
                )


class TestApplyingClicks(unittest.TestCase):
    def test_clicking_a_cell_toggles_it_and_its_neighbours(self):
        self.assertEqual(lo.click(0x0000, 0), lo.MASKS[0])

    def test_clicking_the_same_cell_twice_is_a_no_op(self):
        for i in range(16):
            self.assertEqual(lo.click(lo.click(0x1234, i), i), 0x1234)

    def test_click_order_is_irrelevant(self):
        forwards = lo.click(lo.click(lo.click(0, 2), 7), 11)
        backwards = lo.click(lo.click(lo.click(0, 11), 7), 2)
        self.assertEqual(forwards, backwards)

    def test_apply_click_set_matches_clicking_each_cell_in_turn(self):
        click_set = 0b1000100100010010
        state = 0x0000
        for i in range(16):
            if click_set >> i & 1:
                state = lo.click(state, i)
        self.assertEqual(lo.apply(0x0000, click_set), state)

    def test_apply_empty_click_set_changes_nothing(self):
        self.assertEqual(lo.apply(0xBEEF, 0), 0xBEEF)


class TestLinearAlgebra(unittest.TestCase):
    """Spec §3: rank(A) = 12, nullity(A) = 4."""

    def test_click_matrix_has_rank_twelve(self):
        self.assertEqual(lo.rank(), 12)

    def test_nullspace_has_sixteen_quiet_patterns(self):
        self.assertEqual(len(lo.NULLSPACE), 16)

    def test_nullspace_entries_are_distinct(self):
        self.assertEqual(len(set(lo.NULLSPACE)), 16)

    def test_quiet_patterns_change_nothing(self):
        for pattern in lo.NULLSPACE:
            self.assertEqual(lo.apply(0x0000, pattern), 0x0000)

    def test_nullspace_contains_the_empty_click_set(self):
        self.assertIn(0, lo.NULLSPACE)

    def test_nullspace_is_closed_under_xor(self):
        for a in lo.NULLSPACE:
            for b in lo.NULLSPACE:
                self.assertIn(a ^ b, lo.NULLSPACE)

    def test_all_off_board_is_solvable_with_no_clicks(self):
        self.assertEqual(lo.solve(0x0000), 0)

    def test_solve_returns_a_click_set_that_clears_the_board(self):
        for state in (lo.MASKS[0], lo.MASKS[5] ^ lo.MASKS[9], 0x0000):
            solution = lo.solve(state)
            self.assertIsNotNone(solution)
            self.assertEqual(lo.apply(state, solution), 0x0000)

    def test_solve_returns_none_for_an_unsolvable_board(self):
        unsolvable = next(s for s in range(0x10000) if not lo.is_solvable(s))
        self.assertIsNone(lo.solve(unsolvable))

    def test_exactly_one_sixteenth_of_all_boards_are_solvable(self):
        solvable = [s for s in range(0x10000) if lo.is_solvable(s)]
        self.assertEqual(len(solvable), 4096)

    def test_a_board_is_solvable_exactly_when_it_is_reachable_from_all_off(self):
        for state in (0x0000, lo.MASKS[3], 0xFFFF):
            reachable = lo.apply(0x0000, lo.solve(state) or 0) == state
            self.assertEqual(lo.is_solvable(state), reachable)


class TestMinimumSolution(unittest.TestCase):
    """Spec §3: min over the 16 quiet-pattern cosets of a particular solution."""

    def test_solved_board_needs_no_clicks(self):
        self.assertEqual(lo.min_clicks(0x0000), 0)

    def test_single_click_board_needs_one_click(self):
        self.assertEqual(lo.min_clicks(lo.MASKS[6]), 1)

    def test_minimum_click_set_actually_clears_the_board(self):
        for state in lo.reachable(0x0000):
            self.assertEqual(lo.apply(state, lo.min_click_set(state)), 0x0000)

    def test_minimum_is_never_beaten_by_any_other_solution(self):
        state = lo.MASKS[2] ^ lo.MASKS[9] ^ lo.MASKS[13]
        best = lo.min_clicks(state)
        particular = lo.solve(state)
        for quiet in lo.NULLSPACE:
            self.assertLessEqual(best, (particular ^ quiet).bit_count())

    def test_minimum_click_set_size_equals_minimum_clicks(self):
        for state in (0x0000, lo.MASKS[0], lo.MASKS[7] ^ lo.MASKS[12]):
            self.assertEqual(lo.min_click_set(state).bit_count(), lo.min_clicks(state))

    def test_unsolvable_board_has_no_minimum(self):
        unsolvable = next(s for s in range(0x10000) if not lo.is_solvable(s))
        self.assertIsNone(lo.min_clicks(unsolvable))


class TestStateGraph(unittest.TestCase):
    """Spec §3: BFS must yield exactly 4,096 states including 0x0000."""

    def test_reachable_set_has_exactly_4096_states(self):
        self.assertEqual(len(lo.reachable(0x0000)), 4096)

    def test_solved_state_is_always_reachable(self):
        start = lo.apply(0x0000, 0b0110100000010010)
        self.assertIn(0x0000, lo.reachable(start))

    def test_every_solvable_start_reaches_the_same_state_space(self):
        start = lo.apply(0x0000, 0b1010010100001001)
        self.assertEqual(lo.reachable(start), lo.reachable(0x0000))

    def test_every_reachable_state_is_solvable(self):
        for state in lo.reachable(0x0000):
            self.assertTrue(lo.is_solvable(state))

    def test_reachable_states_are_exactly_the_solvable_ones(self):
        self.assertEqual(
            lo.reachable(0x0000),
            {s for s in range(0x10000) if lo.is_solvable(s)},
        )


class TestDifficultyDistribution(unittest.TestCase):
    def test_distribution_accounts_for_every_reachable_state(self):
        self.assertEqual(sum(lo.distribution().values()), 4096)

    def test_distribution_is_keyed_by_minimum_click_count(self):
        dist = lo.distribution()
        self.assertEqual(dist[0], 1)
        self.assertTrue(all(isinstance(k, int) for k in dist))

    def test_no_board_needs_more_clicks_than_there_are_cells(self):
        self.assertLessEqual(max(lo.distribution()), 16)


if __name__ == "__main__":
    unittest.main()
