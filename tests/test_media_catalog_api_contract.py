import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = (ROOT / "backend" / "server.py").read_text(encoding="utf-8")
TEACHER = (ROOT / "backend" / "teacher_chat.py").read_text(encoding="utf-8")
INDEXES = (ROOT / "backend" / "create_indexes.py").read_text(encoding="utf-8")
SEED = (ROOT / "backend" / "seed_media_catalog.py").read_text(encoding="utf-8")


class MediaCatalogApiContractTests(unittest.TestCase):
    def test_library_route_is_jwt_protected_and_language_required(self):
        self.assertIn('@api_router.get("/library/media")', SERVER)
        self.assertIn("language: str = Query(...)", SERVER)
        self.assertIn("current_user: dict = Depends(get_current_user)", SERVER)
        self.assertIn("status_code=422", SERVER)
        self.assertIn("list_localized_catalog_media(db.media_catalog, language)", SERVER)

    def test_indexes_are_additive_and_named(self):
        self.assertIn('name="media_id_unique"', INDEXES)
        self.assertIn('name="media_active_language_tags"', INDEXES)
        self.assertIn('created["media_catalog"]', INDEXES)

    def test_michael_catalog_is_fail_soft_bounded_and_skips_exact_signs(self):
        self.assertIn("async def _get_relevant_catalog_media(", TEACHER)
        self.assertIn("requested_language in SUPPORTED_LANGUAGES", TEACHER)
        self.assertIn("if not explicit_sign_ids", TEACHER)
        self.assertIn("return approved_media[:1]", TEACHER)
        self.assertIn("catalog_media[:1]", TEACHER)
        self.assertIn('logger.warning("Media catalog lookup skipped:', TEACHER)

    def test_seed_is_dry_run_by_default_and_requires_apply_confirmation(self):
        self.assertIn('parser.add_argument("--apply", action="store_true"', SEED)
        self.assertIn('parser.add_argument("--confirm-db-name"', SEED)
        self.assertIn("if not args.apply:", SEED)
        self.assertLess(SEED.index("verify_manifest_urls(documents"), SEED.index("AsyncIOMotorClient(mongo_url)"))
        self.assertNotIn("delete_one", SEED)
        self.assertNotIn("delete_many", SEED)


if __name__ == "__main__":
    unittest.main()
