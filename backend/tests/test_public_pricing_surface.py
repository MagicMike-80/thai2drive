"""Rendered public pricing navigation: no credentials or production writes."""
import sys
import unittest
from pathlib import Path
from html.parser import HTMLParser

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from landing import build_landing_page


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.targets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a":
            self.targets.append(attrs.get("href"))


class PublicPricingSurfaceTests(unittest.TestCase):
    def test_pricing_links_resolve_for_each_language(self):
        for lang in ("no", "th", "en"):
            with self.subTest(lang=lang):
                html = build_landing_page("", "", "", lang)
                parser = Links()
                parser.feed(html)
                self.assertIn("#pricing", parser.targets)
                self.assertEqual(parser.ids.count("pricing"), 1)
                self.assertIn(f"/{lang}/app", parser.targets)
                section = html.split('<section id="pricing"', 1)[1].split('</section>', 1)[0]
                self.assertIn('id="publicPricingPlans"', section)
                self.assertNotIn('99', section)


if __name__ == "__main__":
    unittest.main()
