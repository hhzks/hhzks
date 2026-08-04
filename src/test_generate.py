"""Unit tests for the generator (spec §3 assertions, §5, §6, §8)."""

import datetime as dt
import os
import tempfile
import unittest
from pathlib import Path

import generate
import lightsout as lo
import puzzle
import render

REPO = "hhzks/hhzks"
DAY = dt.date(2026, 8, 4)


def make_root():
    """A throwaway checkout of `main`: README with markers, plus the tile art."""
    root = Path(tempfile.mkdtemp())
    (root / "img").mkdir()
    (root / "img" / "on.svg").write_text("<svg>on</svg>", encoding="utf-8")
    (root / "img" / "off.svg").write_text("<svg>off</svg>", encoding="utf-8")
    (root / "README.md").write_text(
        f"## Hi\n\n{render.START_MARKER}\nold\n{render.END_MARKER}\n\ntail\n",
        encoding="utf-8",
    )
    return root


class TestGraphIntegrityChecks(unittest.TestCase):
    """Spec §3: a wrong state count is a generator bug -- fail, don't publish."""

    def test_a_correct_state_space_passes(self):
        generate.check_graph(lo.reachable(0x0000))

    def test_a_short_state_space_is_rejected(self):
        with self.assertRaises(generate.GeneratorError):
            generate.check_graph({0x0000, 0x0001})

    def test_a_state_space_without_the_solved_board_is_rejected(self):
        states = lo.reachable(0x0000) - {0x0000} | {0xFFFF ^ 0x1}
        with self.assertRaises(generate.GeneratorError):
            generate.check_graph(states)


class TestStateGraphOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = make_root()
        cls.out = Path(tempfile.mkdtemp())
        cls.puzzle = puzzle.for_date(DAY)
        generate.write_state_graph(cls.puzzle, REPO, cls.out, cls.root)

    def test_one_file_per_reachable_state(self):
        self.assertEqual(len(list(self.out.glob("s/*/*.md"))), 4096)

    def test_every_state_is_at_its_sharded_path(self):
        for state in lo.reachable(self.puzzle.start):
            self.assertTrue((self.out / render.state_path(state)).is_file())

    def test_shards_stay_around_256_files(self):
        for shard in (self.out / "s").iterdir():
            self.assertLessEqual(len(list(shard.glob("*.md"))), 300)

    def test_both_tile_images_are_published(self):
        self.assertTrue((self.out / "img" / "on.svg").is_file())
        self.assertTrue((self.out / "img" / "off.svg").is_file())

    def test_only_two_images_exist_for_the_whole_game(self):
        self.assertEqual(len(list(self.out.rglob("*.svg"))), 2)

    def test_clicking_a_tile_leads_to_the_xored_state(self):
        state = self.puzzle.start
        page = (self.out / render.state_path(state)).read_text(encoding="utf-8")
        for i in range(16):
            self.assertIn(render.relative_link(state, state ^ lo.MASKS[i]), page)

    def test_every_relative_link_resolves_to_a_real_file(self):
        for path in self.out.glob("s/*/*.md"):
            text = path.read_text(encoding="utf-8")
            for target in generate.relative_targets(text):
                self.assertTrue(
                    (path.parent / target).resolve().exists(), f"{path.name} -> {target}"
                )

    def test_the_solved_page_is_the_finished_one(self):
        page = (self.out / "s" / "0" / "0000.md").read_text(encoding="utf-8")
        self.assertIn("Solved", page)


class TestReadmeUpdate(unittest.TestCase):
    def test_readme_board_is_written_between_the_markers(self):
        root = make_root()
        generate.write_readme(puzzle.for_date(DAY), REPO, root)
        text = (root / "README.md").read_text(encoding="utf-8")
        self.assertIn(render.START_MARKER, text)
        self.assertIn(render.END_MARKER, text)
        self.assertNotIn("old", text)
        self.assertIn("## Hi", text)
        self.assertIn("tail", text)

    def test_readme_links_point_at_the_daily_branch(self):
        root = make_root()
        generate.write_readme(puzzle.for_date(DAY), REPO, root)
        text = (root / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"https://github.com/{REPO}/blob/daily/s/", text)


class TestArchive(unittest.TestCase):
    def test_entry_is_appended_to_the_month_file(self):
        root = make_root()
        generate.append_archive(puzzle.for_date(DAY), root)
        text = (root / "archive" / "2026-08.md").read_text(encoding="utf-8")
        self.assertIn("2026-08-04", text)

    def test_appending_twice_does_not_duplicate_the_entry(self):
        root = make_root()
        p = puzzle.for_date(DAY)
        self.assertTrue(generate.append_archive(p, root))
        self.assertFalse(generate.append_archive(p, root))
        text = (root / "archive" / "2026-08.md").read_text(encoding="utf-8")
        self.assertEqual(text.count("## 2026-08-04"), 1)

    def test_separate_months_go_to_separate_files(self):
        root = make_root()
        generate.append_archive(puzzle.for_date(dt.date(2026, 7, 31)), root)
        generate.append_archive(puzzle.for_date(dt.date(2026, 8, 1)), root)
        self.assertTrue((root / "archive" / "2026-07.md").is_file())
        self.assertTrue((root / "archive" / "2026-08.md").is_file())

    def test_entries_accumulate_in_date_order(self):
        root = make_root()
        for day in (2, 3, 4):
            generate.append_archive(puzzle.for_date(dt.date(2026, 8, day)), root)
        text = (root / "archive" / "2026-08.md").read_text(encoding="utf-8")
        self.assertLess(text.index("2026-08-02"), text.index("2026-08-03"))
        self.assertLess(text.index("2026-08-03"), text.index("2026-08-04"))


class TestMain(unittest.TestCase):
    def run_main(self, root, out, date=DAY):
        return generate.main(
            ["--date", date.isoformat(), "--out", str(out), "--root", str(root)],
            env={"GITHUB_REPOSITORY": REPO},
        )

    def test_a_full_run_produces_graph_readme_and_archive(self):
        root, out = make_root(), Path(tempfile.mkdtemp())
        self.run_main(root, out)
        self.assertEqual(len(list(out.glob("s/*/*.md"))), 4096)
        self.assertIn("blob/daily", (root / "README.md").read_text(encoding="utf-8"))
        self.assertTrue((root / "archive" / "2026-08.md").is_file())

    def test_todays_solution_is_not_published_in_the_archive(self):
        root, out = make_root(), Path(tempfile.mkdtemp())
        self.run_main(root, out)
        archived = "".join(
            p.read_text(encoding="utf-8") for p in (root / "archive").glob("*.md")
        )
        self.assertNotIn(str(DAY), archived)

    def test_the_archive_holds_yesterdays_puzzle(self):
        root, out = make_root(), Path(tempfile.mkdtemp())
        self.run_main(root, out)
        text = (root / "archive" / "2026-08.md").read_text(encoding="utf-8")
        self.assertIn(str(DAY - dt.timedelta(days=1)), text)

    def test_the_repo_is_read_from_the_environment_not_hardcoded(self):
        root, out = make_root(), Path(tempfile.mkdtemp())
        generate.main(
            ["--date", DAY.isoformat(), "--out", str(out), "--root", str(root)],
            env={"GITHUB_REPOSITORY": "someone/else"},
        )
        self.assertIn("someone/else", (root / "README.md").read_text(encoding="utf-8"))

    def test_a_missing_repository_environment_variable_is_an_error(self):
        root, out = make_root(), Path(tempfile.mkdtemp())
        with self.assertRaises(generate.GeneratorError):
            generate.main(
                ["--date", DAY.isoformat(), "--out", str(out), "--root", str(root)],
                env={},
            )

    def test_running_the_same_date_twice_gives_identical_output(self):
        root, out = make_root(), Path(tempfile.mkdtemp())
        self.run_main(root, out)
        first = (out / "s" / "0" / "0000.md").read_text(encoding="utf-8")
        readme_first = (root / "README.md").read_text(encoding="utf-8")

        root2, out2 = make_root(), Path(tempfile.mkdtemp())
        self.run_main(root2, out2)
        self.assertEqual(first, (out2 / "s" / "0" / "0000.md").read_text(encoding="utf-8"))
        self.assertEqual(readme_first, (root2 / "README.md").read_text(encoding="utf-8"))

    def test_a_stale_previous_graph_is_cleared_before_writing(self):
        root, out = make_root(), Path(tempfile.mkdtemp())
        stale = out / "s" / "9" / "9999.md"
        stale.parent.mkdir(parents=True)
        stale.write_text("yesterday", encoding="utf-8")
        self.run_main(root, out)
        remaining = {p.read_text(encoding="utf-8") for p in out.glob("s/*/*.md")}
        self.assertNotIn("yesterday", remaining)
        self.assertEqual(len(list(out.glob("s/*/*.md"))), 4096)

    def test_defaulting_to_today_needs_no_date_flag(self):
        root, out = make_root(), Path(tempfile.mkdtemp())
        generate.main(
            ["--out", str(out), "--root", str(root)], env={"GITHUB_REPOSITORY": REPO}
        )
        self.assertEqual(len(list(out.glob("s/*/*.md"))), 4096)


if __name__ == "__main__":
    unittest.main()
