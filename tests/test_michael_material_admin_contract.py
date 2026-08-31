import ast
import unittest
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
SERVER = (ROOT / "backend" / "server.py").read_text(encoding="utf-8")
ADMIN = (ROOT / "backend" / "admin.html").read_text(encoding="utf-8")
TEACHER_CHAT = (ROOT / "backend" / "teacher_chat.py").read_text(encoding="utf-8")


class FakeHTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def load_validation_helpers():
    wanted = {
        "MICHAEL_MATERIAL_TYPES",
        "MICHAEL_MATERIAL_FIELDS",
        "_clean_string_list",
        "_clean_multilang",
        "_is_safe_michael_material_url",
        "_normalize_michael_material_payload",
        "_validate_ready_michael_material",
    }
    tree = ast.parse(SERVER)
    nodes = []
    for node in tree.body:
        name = getattr(node, "name", None)
        targets = [target.id for target in getattr(node, "targets", []) if isinstance(target, ast.Name)]
        if name in wanted or any(target in wanted for target in targets):
            nodes.append(node)
    module = ast.Module(body=nodes, type_ignores=[])
    namespace = {"Any": Any, "Dict": Dict, "List": List, "HTTPException": FakeHTTPException}
    exec(compile(module, "server_helpers", "exec"), namespace)
    return namespace


class MichaelMaterialAdminContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = load_validation_helpers()

    def test_admin_routes_are_protected_and_additive(self):
        self.assertIn('@api_router.get("/admin/michael-materials")', SERVER)
        self.assertIn('@api_router.post("/admin/michael-materials")', SERVER)
        self.assertIn('@api_router.patch("/admin/michael-materials/{material_id}")', SERVER)
        self.assertGreaterEqual(SERVER.count('Depends(require_admin)'), 3)
        self.assertIn("db.michael_materials", SERVER)

    def test_material_references_existing_sources_and_safe_urls(self):
        self.assertIn('MICHAEL_MATERIAL_TYPES = {"sign", "intersection_image", "video"}', SERVER)
        self.assertIn('db.traffic_signs.find_one({"id": source_id}', SERVER)
        self.assertIn('db.learning_videos.find_one({"id": source_id}', SERVER)
        self.assertIn('value.startswith("/api/")', SERVER)
        self.assertIn('value.startswith("https://")', SERVER)
        self.assertIn('Approved material must have a previewable source', SERVER)
        self.assertNotIn("data:image", SERVER[SERVER.index("MICHAEL_MATERIAL_TYPES"):SERVER.index("# ── Podcasts")])

    def test_approved_material_requires_all_three_languages(self):
        self.assertIn('for lang in ("no", "th", "en")', SERVER)
        self.assertIn('for field in ("title", "caption")', SERVER)
        self.assertIn('approved_for_michael', SERVER)

    def test_validation_accepts_complete_approved_item_and_rejects_incomplete_item(self):
        normalize = self.helpers["_normalize_michael_material_payload"]
        validate = self.helpers["_validate_ready_michael_material"]
        complete = normalize({
            "type": "intersection_image",
            "source_url": "/api/assets/junctions/t-kryss.jpg",
            "title": {"no": "T-kryss", "th": "ทางแยกตัวที", "en": "T-junction"},
            "caption": {"no": "Se etter vikeplikt.", "th": "มองหาป้ายให้ทาง", "en": "Check right-of-way."},
            "topic_tags": ["vikeplikt", "vikeplikt", ""],
            "sign_ids": ["202_0"],
            "situation_tags": ["T-kryss"],
            "active": True,
            "approved_for_michael": True,
            "priority": 20,
        })
        validate(complete)
        self.assertEqual(complete["topic_tags"], ["vikeplikt"])
        complete["caption"]["th"] = ""
        with self.assertRaises(FakeHTTPException) as error:
            validate(complete)
        self.assertEqual(error.exception.status_code, 400)

    def test_validation_rejects_unsafe_image_url_and_unknown_fields(self):
        normalize = self.helpers["_normalize_michael_material_payload"]
        validate = self.helpers["_validate_ready_michael_material"]
        with self.assertRaises(FakeHTTPException):
            normalize({"type": "sign", "unexpected": "value"})
        draft = normalize({"type": "intersection_image", "source_url": "javascript:alert(1)"})
        with self.assertRaises(FakeHTTPException):
            validate(draft)

    def test_admin_has_tab_filters_preview_and_deactivation(self):
        for token in (
            'tab-michael-materials',
            'Godkjent materiale for Michael',
            'loadMichaelMaterials()',
            'openMichaelMaterialModal',
            'michaelMaterialPreview',
            'deactivateMichaelMaterial',
            'populateMichaelMaterialSources',
            'Koblede skilt-ID-er',
            'Situasjonsknagger',
        ):
            self.assertIn(token, ADMIN)

    def test_patch_one_does_not_add_material_response_to_teacher_chat(self):
        self.assertNotIn("michael_materials", TEACHER_CHAT)
        self.assertNotIn("approved_for_michael", TEACHER_CHAT)


if __name__ == "__main__":
    unittest.main()
