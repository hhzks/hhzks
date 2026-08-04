"""Unit tests for markdown rendering (spec §5, §6, §8)."""

import datetime as dt
import re
import unittest

import lightsout as lo
import puzzle
import render

REPO = "hhzks/hhzks"
DAY = dt.date(2026, 8, 4)
PUZZLE = puzzle.for_date(DAY)


class TestStatePaths(unittest.TestCase):
    def test_state_id_is_four_lowercase_hex_digits(self):
        self.assertEqual(render.state_id(0x000F), "000f")
        self.assertEqual(render.state_id(0xABCD), "abcd")

    def test_path_is_sharded_by_the_first_hex_character(self):
        self.assertEqual(render.state_path(0xA3F0), "s/a/a3f0.md")
        self.assertEqual(render.state_path(0x0000), "s/0/0000.md")

    def test_sharding_keeps_directories_small(self):
        shards = {render.state_path(s).split("/")[1] for s in range(0x10000)}
        self.assertEqual(len(shards), 16)

    def test_link_between_states_is_relative_to_the_shard(self):
        self.assertEqual(render.relative_link(0xA3F0, 0x3F01), "../3/3f01.md")

    def test_link_within_the_same_shard_still_goes_up_one_level(self):
        self.assertEqual(render.relative_link(0x3A00, 0x3F01), "../3/3f01.md")


class TestBoardTable(unittest.TestCase):
    def setUp(self):
        self.table = render.board_table(PUZZLE.start, link_for=lambda i: f"L{i}")

    def test_header_and_delimiter_declare_the_same_column_count(self):
        header, delimiter = self.table.splitlines()[:2]
        self.assertEqual(header.count("|"), delimiter.count("|"))
        self.assertEqual(delimiter.count(":-:"), 4)

    def test_table_has_a_header_a_delimiter_and_four_board_rows(self):
        self.assertEqual(len(self.table.splitlines()), 6)

    def test_table_renders_exactly_sixteen_tiles(self):
        self.assertEqual(self.table.count("<img"), 16)

    def test_tiles_match_the_bits_of_the_state_row_by_row(self):
        rows = self.table.splitlines()[2:]
        for r, row in enumerate(rows):
            tiles = re.findall(r"img/(on|off)\.svg", row)
            self.assertEqual(len(tiles), 4)
            for c, tile in enumerate(tiles):
                lit = PUZZLE.start >> (r * 4 + c) & 1
                self.assertEqual(tile, "on" if lit else "off", f"cell r{r}c{c}")

    def test_each_tile_links_where_the_link_function_says(self):
        for i in range(16):
            self.assertIn(f"](L{i})", self.table)

    def test_unlinked_table_renders_tiles_without_links(self):
        table = render.board_table(PUZZLE.start, link_for=None)
        self.assertEqual(table.count("<img"), 16)
        self.assertNotIn("](", table)


class TestStatePage(unittest.TestCase):
    def setUp(self):
        self.state = lo.click(PUZZLE.start, 6)
        self.page = render.state_page(PUZZLE, self.state, REPO)

    def test_page_shows_the_date(self):
        self.assertIn("2026-08-04", self.page)

    def test_page_explains_the_rule(self):
        self.assertIn("Turn every light off", self.page)

    def test_every_tile_links_to_the_state_after_clicking_it(self):
        for i in range(16):
            self.assertIn(render.relative_link(self.state, self.state ^ lo.MASKS[i]), self.page)

    def test_images_are_reached_by_climbing_out_of_the_shard(self):
        self.assertIn("../../img/", self.page)
        self.assertNotIn("(/img/", self.page)

    def test_reset_returns_to_todays_start_board(self):
        self.assertIn(render.relative_link(self.state, PUZZLE.start), self.page)

    def test_hint_is_hidden_inside_a_details_block(self):
        details = re.search(r"<details>.*</details>", self.page, re.S)
        self.assertIsNotNone(details)
        self.assertIn(str(lo.min_clicks(self.state)), details.group())

    def test_clicks_remaining_is_not_visible_outside_the_details_block(self):
        outside = re.sub(r"<details>.*</details>", "", self.page, flags=re.S)
        self.assertNotIn("clicks from solved", outside)

    def test_cross_branch_links_are_absolute(self):
        self.assertIn(f"https://github.com/{REPO}", self.page)

    def test_page_references_exactly_sixteen_images(self):
        self.assertEqual(self.page.count("<img"), 16)


class TestSolvedPage(unittest.TestCase):
    def setUp(self):
        self.page = render.state_page(PUZZLE, 0x0000, REPO)

    def test_solved_page_congratulates(self):
        self.assertIn("Solved", self.page)

    def test_solved_page_still_renders_the_board(self):
        self.assertEqual(self.page.count("<img"), 16)

    def test_solved_board_is_all_off(self):
        self.assertEqual(self.page.count("off.svg"), 16)

    def test_solved_page_has_no_tile_links(self):
        for i in range(16):
            self.assertNotIn(render.relative_link(0x0000, lo.MASKS[i]), self.page)

    def test_solved_page_reports_todays_minimum(self):
        self.assertIn(str(PUZZLE.min_clicks), self.page)

    def test_solved_page_links_back_to_the_profile(self):
        self.assertIn(f"https://github.com/{REPO}", self.page)


class TestReadmeBlock(unittest.TestCase):
    def setUp(self):
        self.block = render.readme_block(PUZZLE, REPO)

    def test_block_is_fenced_by_both_markers(self):
        self.assertTrue(self.block.startswith(render.START_MARKER))
        self.assertTrue(self.block.rstrip().endswith(render.END_MARKER))

    def test_block_shows_the_date(self):
        self.assertIn("2026-08-04", self.block)

    def test_tiles_link_absolutely_to_the_daily_branch(self):
        for i in range(16):
            target = PUZZLE.start ^ lo.MASKS[i]
            url = f"https://github.com/{REPO}/blob/daily/{render.state_path(target)}"
            self.assertIn(url, self.block)

    def test_block_contains_no_relative_links_that_cannot_cross_branches(self):
        self.assertNotIn("](../", self.block)
        self.assertNotIn("](s/", self.block)

    def test_block_states_the_rules(self):
        self.assertIn("Turn every light off", self.block)

    def test_block_does_not_promise_a_specific_time_of_day(self):
        self.assertNotIn("midnight", self.block.lower())
        self.assertIn("daily", self.block.lower())


class TestReadmeSplicing(unittest.TestCase):
    def test_only_the_region_between_markers_is_replaced(self):
        readme = (
            "# Hello\n\nabove\n\n"
            f"{render.START_MARKER}\nold board\n{render.END_MARKER}\n\nbelow\n"
        )
        updated = render.splice_readme(readme, render.readme_block(PUZZLE, REPO))
        self.assertIn("above", updated)
        self.assertIn("below", updated)
        self.assertNotIn("old board", updated)

    def test_splicing_is_idempotent(self):
        readme = f"a\n{render.START_MARKER}\nx\n{render.END_MARKER}\nb\n"
        block = render.readme_block(PUZZLE, REPO)
        once = render.splice_readme(readme, block)
        self.assertEqual(once, render.splice_readme(once, block))

    def test_missing_markers_are_an_error_rather_than_a_silent_no_op(self):
        with self.assertRaises(ValueError):
            render.splice_readme("# No markers here\n", render.readme_block(PUZZLE, REPO))


class TestArchiveEntry(unittest.TestCase):
    def setUp(self):
        self.entry = render.archive_entry(PUZZLE)

    def test_entry_records_the_date(self):
        self.assertIn("2026-08-04", self.entry)

    def test_entry_shows_the_start_board_without_links(self):
        self.assertEqual(self.entry.count("<img"), 16)
        self.assertNotIn("](", self.entry.split("Solution")[0])

    def test_entry_reports_the_minimum_solution_length(self):
        self.assertIn(str(PUZZLE.min_clicks), self.entry)

    def test_entry_lists_one_coordinate_per_click(self):
        coords = re.findall(r"r[1-4]c[1-4]", self.entry)
        self.assertEqual(len(coords), PUZZLE.min_clicks)

    def test_listed_clicks_actually_solve_the_board(self):
        click_set = 0
        for coord in re.findall(r"r([1-4])c([1-4])", self.entry):
            r, c = int(coord[0]) - 1, int(coord[1]) - 1
            click_set |= 1 << (r * 4 + c)
        self.assertEqual(lo.apply(PUZZLE.start, click_set), 0x0000)

    def test_archive_month_file_follows_the_date(self):
        self.assertEqual(render.archive_path(DAY), "archive/2026-08.md")


if __name__ == "__main__":
    unittest.main()
