"""Unit tests for verify.py.

A verifier is only worth having if it fails when the build is broken, so each
test corrupts a good build in one specific way and asserts the right check
catches it (spec §9).
"""

import datetime as dt
import shutil
import tempfile
import unittest
from pathlib import Path

import generate
import lightsout as lo
import puzzle
import render
import verify

REPO = "hhzks/hhzks"
DAY = dt.date(2026, 8, 4)

ROOT = OUT = PUZZLE = None


def setUpModule():
    global ROOT, OUT, PUZZLE
    ROOT = Path(tempfile.mkdtemp())
    OUT = Path(tempfile.mkdtemp())
    (ROOT / "img").mkdir()
    (ROOT / "img" / "on.svg").write_text("<svg>on</svg>", encoding="utf-8")
    (ROOT / "img" / "off.svg").write_text("<svg>off</svg>", encoding="utf-8")
    (ROOT / "README.md").write_text(
        f"## Hi\n\n{render.START_MARKER}\nold\n{render.END_MARKER}\n\n"
        f"## Lights Out\n\nEvery tile toggles its neighbours.\n",
        encoding="utf-8",
    )
    generate.main(
        ["--date", DAY.isoformat(), "--out", str(OUT), "--root", str(ROOT)],
        env={"GITHUB_REPOSITORY": REPO},
    )
    PUZZLE = puzzle.for_date(DAY)


class Corrupted:
    """Break one file, then put it back."""

    def __init__(self, path):
        self.path = Path(path)

    def __enter__(self):
        self.backup = self.path.read_bytes() if self.path.exists() else None
        return self.path

    def __exit__(self, *exc):
        if self.backup is None:
            self.path.unlink(missing_ok=True)
        else:
            self.path.write_bytes(self.backup)
        return False


class TestCleanBuildPasses(unittest.TestCase):
    def test_a_freshly_generated_build_has_no_errors(self):
        self.assertEqual(verify.verify(PUZZLE, REPO, OUT, ROOT), [])

    def test_main_exits_zero_on_a_clean_build(self):
        code = verify.main(
            ["--date", DAY.isoformat(), "--out", str(OUT), "--root", str(ROOT)],
            env={"GITHUB_REPOSITORY": REPO},
        )
        self.assertEqual(code, 0)


class TestStateSpaceChecks(unittest.TestCase):
    def test_the_state_space_is_the_expected_size(self):
        self.assertEqual(verify.check_state_space(PUZZLE), [])

    def test_difficulty_inside_the_band_passes(self):
        self.assertEqual(verify.check_difficulty(PUZZLE), [])

    def test_difficulty_outside_the_band_is_reported(self):
        too_easy = puzzle.Puzzle(date=DAY, start=lo.MASKS[0], min_clicks=1, solution=1)
        self.assertTrue(verify.check_difficulty(too_easy))


class TestFileChecks(unittest.TestCase):
    def test_a_missing_state_file_is_caught(self):
        victim = OUT / render.state_path(lo.click(PUZZLE.start, 3))
        with Corrupted(victim) as path:
            path.unlink()
            errors = verify.check_files(PUZZLE, OUT)
        self.assertTrue(any("missing" in e for e in errors))

    def test_an_unreachable_extra_file_is_caught(self):
        stray = OUT / "s" / "0" / "0001.md"
        with Corrupted(stray) as path:
            path.write_text("stray", encoding="utf-8")
            errors = verify.check_files(PUZZLE, OUT)
        self.assertTrue(any("unexpected" in e for e in errors))


class TestLinkChecks(unittest.TestCase):
    def test_a_dangling_link_is_caught(self):
        victim = OUT / render.state_path(PUZZLE.start)
        with Corrupted(victim) as path:
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace("](../", "](../z/nope.md)(../", 1), encoding="utf-8")
            errors = verify.check_links(OUT)
        self.assertTrue(errors)

    def test_clean_links_produce_no_errors(self):
        self.assertEqual(verify.check_links(OUT), [])


class TestTileChecks(unittest.TestCase):
    def test_a_flipped_tile_no_longer_matches_the_state_id(self):
        state = PUZZLE.start
        victim = OUT / render.state_path(state)
        lit = "on" if state & 1 else "off"
        wrong = "off" if lit == "on" else "on"
        with Corrupted(victim) as path:
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(f"img/{lit}.svg", f"img/{wrong}.svg", 1), encoding="utf-8")
            errors = verify.check_tiles(OUT)
        self.assertTrue(any("pattern" in e for e in errors))

    def test_a_dropped_tile_is_caught(self):
        victim = OUT / render.state_path(lo.click(PUZZLE.start, 1))
        with Corrupted(victim) as path:
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace('<img src="../../img/', "<x ", 1), encoding="utf-8")
            errors = verify.check_tiles(OUT)
        self.assertTrue(any("16" in e for e in errors))

    def test_clean_tiles_produce_no_errors(self):
        self.assertEqual(verify.check_tiles(OUT), [])


class TestClickTargetChecks(unittest.TestCase):
    def test_a_rewired_tile_link_is_caught(self):
        state = lo.click(PUZZLE.start, 9)
        victim = OUT / render.state_path(state)
        right = render.relative_link(state, state ^ lo.MASKS[0])
        wrong = render.relative_link(state, state ^ lo.MASKS[7])
        with Corrupted(victim) as path:
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(right, wrong, 1), encoding="utf-8")
            errors = verify.check_click_targets(PUZZLE, OUT)
        self.assertTrue(errors)

    def test_correctly_wired_clicks_produce_no_errors(self):
        self.assertEqual(verify.check_click_targets(PUZZLE, OUT), [])


class TestReadmeChecks(unittest.TestCase):
    def test_missing_markers_are_caught(self):
        with Corrupted(ROOT / "README.md") as path:
            path.write_text("no markers here\n", encoding="utf-8")
            errors = verify.check_readme(REPO, ROOT, OUT)
        self.assertTrue(any("marker" in e for e in errors))

    def test_a_readme_url_pointing_at_a_missing_state_is_caught(self):
        with Corrupted(ROOT / "README.md") as path:
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace("/blob/daily/s/", "/blob/daily/nope/", 1), encoding="utf-8")
            errors = verify.check_readme(REPO, ROOT, OUT)
        self.assertTrue(errors)

    def test_a_clean_readme_produces_no_errors(self):
        self.assertEqual(verify.check_readme(REPO, ROOT, OUT), [])


class TestProfileAnchor(unittest.TestCase):
    """Every state page links back to `#lights-out`; the heading must survive."""

    def test_the_anchor_heading_is_present(self):
        readme = ROOT / "README.md"
        with Corrupted(readme) as path:
            path.write_text("# Profile\n\n## Lights Out\n\ntext\n", encoding="utf-8")
            self.assertEqual(verify.check_profile_anchor(ROOT), [])

    def test_a_renamed_heading_is_caught(self):
        readme = ROOT / "README.md"
        with Corrupted(readme) as path:
            path.write_text("# Profile\n\n## The Puzzle\n\ntext\n", encoding="utf-8")
            errors = verify.check_profile_anchor(ROOT)
        self.assertTrue(any("lights-out" in e for e in errors))

    def test_the_dated_block_heading_does_not_satisfy_the_anchor(self):
        readme = ROOT / "README.md"
        with Corrupted(readme) as path:
            path.write_text("# Profile\n\n### Lights Out · 2026-08-04\n", encoding="utf-8")
            self.assertTrue(verify.check_profile_anchor(ROOT))

    def test_state_pages_link_to_the_anchor_the_readme_provides(self):
        page = (OUT / render.state_path(PUZZLE.start)).read_text(encoding="utf-8")
        self.assertIn("#lights-out", page)
        self.assertEqual(verify.check_profile_anchor(ROOT), [])


class TestMainFailsLoudly(unittest.TestCase):
    def test_main_exits_nonzero_when_the_build_is_broken(self):
        victim = OUT / render.state_path(lo.click(PUZZLE.start, 12))
        with Corrupted(victim) as path:
            path.unlink()
            code = verify.main(
                ["--date", DAY.isoformat(), "--out", str(OUT), "--root", str(ROOT)],
                env={"GITHUB_REPOSITORY": REPO},
            )
        self.assertNotEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
