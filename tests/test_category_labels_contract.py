from pathlib import Path
import unittest


WEBAPP = Path(__file__).resolve().parents[1] / "backend" / "webapp.py"


class CategoryLabelsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = WEBAPP.read_text(encoding="utf-8")

    def test_category_header_does_not_show_a_count(self):
        self.assertIn("document.getElementById('catCount').textContent = '';", self.source)
        self.assertNotIn("document.getElementById('catCount').textContent = '(' + cats.length + ')'", self.source)

    def test_category_cards_show_only_localized_name(self):
        self.assertIn("'<div class=\"carousel-3d-label\">' + escH(name) + '</div>'", self.source)
        self.assertNotIn("'<div class=\"carousel-3d-count\">'", self.source)


if __name__ == "__main__":
    unittest.main()
