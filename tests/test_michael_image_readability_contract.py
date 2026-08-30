import unittest
from pathlib import Path


WEBAPP = (Path(__file__).resolve().parents[1] / "backend" / "webapp.py").read_text(encoding="utf-8")


class MichaelImageReadabilityContractTests(unittest.TestCase):
    def test_teacher_images_are_compact_and_text_is_readable_on_mobile(self):
        self.assertIn(".teacher-inline-image { max-height:210px; }", WEBAPP)
        self.assertIn("font-size:1.05rem; line-height:1.65", WEBAPP)
        self.assertIn("img.className = 'teacher-inline-image';", WEBAPP)
        self.assertNotIn("img.style.cssText = 'width:100%;", WEBAPP)


if __name__ == "__main__":
    unittest.main()
