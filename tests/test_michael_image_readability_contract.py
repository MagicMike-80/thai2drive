import re
import unittest
from pathlib import Path


WEBAPP = (Path(__file__).resolve().parents[1] / "backend" / "webapp.py").read_text(encoding="utf-8")


class MichaelImageReadabilityContractTests(unittest.TestCase):
    def test_teacher_images_are_compact_and_text_is_readable_on_mobile(self):
        self.assertIn(".teacher-inline-image { max-height:210px; }", WEBAPP)
        rule = re.search(r"#screenTeacher\s+\.tm-bubble\s*\{([^}]*)\}", WEBAPP)
        self.assertIsNotNone(rule, "Missing mobile Michael bubble rule")
        font_size = re.search(r"font-size:\s*([0-9.]+)rem", rule.group(1))
        line_height = re.search(r"line-height:\s*([0-9.]+)", rule.group(1))
        self.assertIsNotNone(font_size, "Missing mobile Michael font size")
        self.assertIsNotNone(line_height, "Missing mobile Michael line height")
        self.assertGreaterEqual(float(font_size.group(1)), 1.05)
        self.assertGreaterEqual(float(line_height.group(1)), 1.65)
        self.assertIn("img.className = 'teacher-inline-image';", WEBAPP)
        self.assertNotIn("img.style.cssText = 'width:100%;", WEBAPP)


if __name__ == "__main__":
    unittest.main()
