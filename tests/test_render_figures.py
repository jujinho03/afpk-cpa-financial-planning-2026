"""Verify figure integrity and provenance without changing model assumptions."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("render_figures", ROOT / "scripts/render_figures.py")
FIGURES = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = FIGURES
SPEC.loader.exec_module(FIGURES)
SVG = "{http://www.w3.org/2000/svg}"


class JudgeFigureTests(unittest.TestCase):
    def test_accessible_self_contained_deterministic_figures(self):
        scratch = ROOT / ".test_tmp"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            directory = Path(tmp)
            first = FIGURES.render(ROOT / "outputs/tables", directory)
            second = FIGURES.render(ROOT / "outputs/tables", directory)
            self.assertEqual(first, second)
            self.assertEqual(len(first), 3)
            for name, content in first.items():
                with self.subTest(name=name):
                    self.assertEqual((directory/name).read_text(encoding="utf-8"), content)
                    root = ET.fromstring(content)
                    self.assertEqual(root.attrib["role"], "img")
                    self.assertTrue(root.find(SVG+"title").text)
                    self.assertTrue(root.find(SVG+"desc").text)
                    self.assertFalse(root.findall(".//" + SVG + "script"))
                    self.assertNotIn("href=", content)

    def test_figures_retain_payment_and_reserve_distinction(self):
        summary, rows, paths = FIGURES.load_exports(ROOT / "outputs/tables")
        self.assertEqual(len(rows), 720)
        self.assertEqual(paths["A"][-1]["raw_cash"], -555)
        content = FIGURES.liquidity(paths, summary)
        self.assertIn("27.10 안전자금 이탈", content)
        self.assertIn("28.01 미충당액 발생", content)
        self.assertIn("A -555", content)
        self.assertIn("0 미만 = 미충당액", content)
        value = FIGURES.financial_value(summary)
        for number in ["6,717", "6,062", "5,853", "5,259"]:
            self.assertIn(number, value)


if __name__ == "__main__":
    unittest.main()
