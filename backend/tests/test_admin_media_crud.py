"""Offline unit tests for Admin Media & Signs CMS CRUD endpoints and UI."""
import asyncio
import io
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Bootstrap paths
backend_dir = Path(__file__).resolve().parent.parent
project_dir = backend_dir.parent
for p in [str(backend_dir), str(project_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import HTTPException
from fastapi import UploadFile
from starlette.datastructures import Headers
from fastapi.testclient import TestClient

import server
from media_catalog import CATEGORIES
from server import (
    AdminMediaCreate,
    AdminMediaUpdate,
    admin_create_media,
    admin_delete_media,
    admin_list_media,
    admin_upload_media_file,
    admin_update_media,
    app,
    require_admin,
)


class _MockGridFSBucket:
    uploads = []
    deleted = []

    def __init__(self, database):
        self.database = database

    async def upload_from_stream(self, filename, stream, metadata=None):
        from bson import ObjectId
        self.__class__.uploads.append((filename, stream.read(), metadata or {}))
        return ObjectId("64b64c000000000000000001")

    async def delete(self, file_id):
        self.__class__.deleted.append(str(file_id))


class _MockCursor:
    def __init__(self, docs):
        self.docs = list(docs)

    def sort(self, *args, **kwargs):
        return self

    async def to_list(self, length=None):
        return self.docs[:length] if length else self.docs


class _MockCollection:
    def __init__(self, docs=None):
        self.docs = list(docs or [])

    def find(self, query=None, projection=None):
        query = query or {}
        results = []
        for doc in self.docs:
            matched = True
            for k, v in query.items():
                if k == "$or":
                    sub_match = False
                    for condition in v:
                        for ck, cv in condition.items():
                            if isinstance(cv, dict) and "$regex" in cv:
                                pattern = cv["$regex"]
                                options = cv.get("$options", "")
                                flags = re.IGNORECASE if "i" in options else 0
                                # Handle nested keys e.g. i18n.no.title
                                val = doc
                                for part in ck.split("."):
                                    val = val.get(part, {}) if isinstance(val, dict) else None
                                if isinstance(val, list):
                                    if any(re.search(pattern, str(item), flags) for item in val):
                                        sub_match = True
                                        break
                                elif val and re.search(pattern, str(val), flags):
                                    sub_match = True
                                    break
                    if not sub_match:
                        matched = False
                        break
                elif doc.get(k) != v:
                    if isinstance(v, dict) and "$ne" in v:
                        if doc.get(k) == v["$ne"]:
                            matched = False
                            break
                    else:
                        matched = False
                        break
            if matched:
                doc_copy = dict(doc)
                if projection and projection.get("_id") == 0:
                    doc_copy.pop("_id", None)
                results.append(doc_copy)
        return _MockCursor(results)

    async def find_one(self, query, projection=None):
        cursor = self.find(query, projection)
        results = await cursor.to_list(1)
        return results[0] if results else None

    async def insert_one(self, doc):
        d = dict(doc)
        if "_id" not in d:
            d["_id"] = "mock_id_" + str(len(self.docs) + 1)
        self.docs.append(d)
        return type("InsertResult", (), {"inserted_id": d["_id"]})()

    async def update_one(self, query, update):
        target = await self.find_one(query)
        if not target:
            return type("UpdateResult", (), {"matched_count": 0, "modified_count": 0})()
        for doc in self.docs:
            if (query.get("media_id") and doc.get("media_id") == query.get("media_id")) or \
               (query.get("id") and doc.get("id") == query.get("id")):
                if "$set" in update:
                    doc.update(update["$set"])
                return type("UpdateResult", (), {"matched_count": 1, "modified_count": 1})()
        return type("UpdateResult", (), {"matched_count": 0, "modified_count": 0})()

    async def delete_one(self, query):
        for i, doc in enumerate(self.docs):
            if (query.get("media_id") and doc.get("media_id") == query.get("media_id")) or \
               (query.get("id") and doc.get("id") == query.get("id")):
                self.docs.pop(i)
                return type("DeleteResult", (), {"deleted_count": 1})()
        return type("DeleteResult", (), {"deleted_count": 0})()


class _MockDatabase:
    def __init__(self, media_docs=None):
        self.media_catalog = _MockCollection(media_docs or [])
        self.learning_videos = _MockCollection([])


class TestAdminMediaCRUD(unittest.TestCase):
    def setUp(self):
        _MockGridFSBucket.uploads = []
        _MockGridFSBucket.deleted = []
        self.initial_media = [
            {
                "media_id": "vid_stopp_01",
                "type": "video",
                "category": "stoppelengde",
                "tags": ["stoppelengde", "reaksjonslengde"],
                "media_url": "/api/assets/vid_stopp_01.mp4",
                "thumbnail_url": "/api/assets/thumbs/thumb_vid_stopp_01.jpg",
                "audio_url": None,
                "content_language": "neutral",
                "is_active": True,
                "i18n": {
                    "no": {"title": "Reaksjonslengde", "description": "Lær om reaksjonslengde"},
                    "th": {"title": "ระยะตอบสนอง", "description": "คำอธิบายระยะตอบสนอง"},
                    "en": {"title": "Reaction Distance", "description": "Learn reaction distance"},
                },
            },
            {
                "media_id": "sign_102",
                "type": "sign",
                "category": "skilt",
                "tags": ["fareskilt", "sving"],
                "media_url": "/api/assets/signs/102.png",
                "thumbnail_url": "/api/assets/signs/102.png",
                "audio_url": None,
                "content_language": "neutral",
                "is_active": False,
                "i18n": {
                    "no": {"title": "Farlig sving", "description": "Farlig sving til høyre"},
                    "th": {"title": "ทางโค้งอันตราย", "description": "ป้ายเตือนทางโค้งอันตราย"},
                    "en": {"title": "Dangerous Curve", "description": "Dangerous curve ahead"},
                },
            },
        ]
        self.mock_db = _MockDatabase(self.initial_media)

    def test_list_media_returns_items_and_total(self):
        """GET /api/admin/media must return all catalog items and total count."""
        with patch.object(server, "db", self.mock_db):
            res = asyncio.run(admin_list_media(_=None))
            self.assertEqual(res["total"], 2)
            ids = [m["media_id"] for m in res["items"]]
            self.assertIn("vid_stopp_01", ids)
            self.assertIn("sign_102", ids)

    def test_list_media_filters_by_type_and_status(self):
        """GET /api/admin/media must filter by type and active status correctly."""
        with patch.object(server, "db", self.mock_db):
            # Filter type=video
            res_video = asyncio.run(admin_list_media(type="video", _=None))
            self.assertEqual(res_video["total"], 1)
            self.assertEqual(res_video["items"][0]["media_id"], "vid_stopp_01")

            # Filter status=active
            res_active = asyncio.run(admin_list_media(status="active", _=None))
            self.assertEqual(res_active["total"], 1)
            self.assertEqual(res_active["items"][0]["media_id"], "vid_stopp_01")

            # Filter status=inactive
            res_inactive = asyncio.run(admin_list_media(status="inactive", _=None))
            self.assertEqual(res_inactive["total"], 1)
            self.assertEqual(res_inactive["items"][0]["media_id"], "sign_102")

    def test_create_media_success(self):
        """POST /api/admin/media creates a new media document with full i18n."""
        new_item = AdminMediaCreate(
            media_id="vid_vike_01",
            type="video",
            category="vikeplikt",
            tags=["vikeplikt", "høyreregel"],
            media_url="/api/assets/vid_vike_01.mp4",
            thumbnail_url="/api/assets/thumbs/vid_vike_01.jpg",
            audio_url="/api/audio/vike_expl.mp3",
            content_language="neutral",
            is_active=True,
            i18n={
                "no": {"title": "Høyreregelen", "description": "Vikeplikt fra høyre"},
                "th": {"title": "กฎการให้ทางขวา", "description": "หลักการให้ทางรถจากทางขวา"},
                "en": {"title": "Priority to the right", "description": "Yielding to traffic from right"},
            },
        )
        with patch.object(server, "db", self.mock_db):
            res = asyncio.run(admin_create_media(new_item, _=None))
            self.assertTrue(res["ok"])
            self.assertEqual(res["media"]["media_id"], "vid_vike_01")
            self.assertEqual(res["media"]["category"], "vikeplikt")
            self.assertEqual(len(self.mock_db.media_catalog.docs), 3)

    def test_create_media_rejects_duplicate_id(self):
        """POST /api/admin/media rejects duplicate media_id."""
        duplicate = AdminMediaCreate(
            media_id="vid_stopp_01",
            type="video",
            category="stoppelengde",
            tags=["duplicate"],
            media_url="/api/assets/dup.mp4",
            i18n={
                "no": {"title": "x", "description": "x"},
                "th": {"title": "x", "description": "x"},
                "en": {"title": "x", "description": "x"},
            },
        )
        with patch.object(server, "db", self.mock_db):
            with self.assertRaises(HTTPException) as ctx:
                asyncio.run(admin_create_media(duplicate, _=None))
            self.assertEqual(ctx.exception.status_code, 400)

    def test_create_media_requires_all_three_languages(self):
        """POST /api/admin/media enforces 100% language isolation by requiring NO, TH, EN."""
        missing_th = AdminMediaCreate(
            media_id="vid_vike_incomplete",
            type="video",
            category="vikeplikt",
            tags=["vikeplikt"],
            media_url="/api/assets/test.mp4",
            i18n={
                "no": {"title": "Norsk", "description": ""},
                "en": {"title": "English", "description": ""},
            },
        )
        with patch.object(server, "db", self.mock_db):
            with self.assertRaises(HTTPException) as ctx:
                asyncio.run(admin_create_media(missing_th, _=None))
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertIn("th", ctx.exception.detail)

    def test_update_media_success(self):
        """PUT /api/admin/media/{media_id} updates metadata and active status."""
        update_data = AdminMediaUpdate(
            category="vikeplikt",
            is_active=False,
            tags=["ny_tagg"],
            i18n={
                "no": {"title": "Oppdatert tittel", "description": "Ny beskrivelse"},
            },
        )
        with patch.object(server, "db", self.mock_db):
            res = asyncio.run(admin_update_media("vid_stopp_01", update_data, _=None))
            self.assertTrue(res["ok"])
            self.assertFalse(res["media"]["is_active"])
            self.assertEqual(res["media"]["category"], "vikeplikt")
            self.assertEqual(res["media"]["tags"], ["ny_tagg"])
            self.assertEqual(res["media"]["i18n"]["no"]["title"], "Oppdatert tittel")
            # Other language titles should remain preserved
            self.assertEqual(res["media"]["i18n"]["th"]["title"], "ระยะตอบสนอง")

    def test_update_media_404_for_unknown_id(self):
        """PUT /api/admin/media/{media_id} returns 404 for unknown media_id."""
        with patch.object(server, "db", self.mock_db):
            with self.assertRaises(HTTPException) as ctx:
                asyncio.run(admin_update_media("non_existent_id", AdminMediaUpdate(is_active=True), _=None))
            self.assertEqual(ctx.exception.status_code, 404)

    def test_delete_media_success_and_404(self):
        """DELETE /api/admin/media/{media_id} removes item and returns 404 if not found."""
        with patch.object(server, "db", self.mock_db):
            res = asyncio.run(admin_delete_media("vid_stopp_01", confirm=True, _=None))
            self.assertTrue(res["ok"])
            self.assertEqual(res["deleted"], "vid_stopp_01")
            self.assertEqual(len(self.mock_db.media_catalog.docs), 1)

            # Second delete must 404
            with self.assertRaises(HTTPException) as ctx:
                asyncio.run(admin_delete_media("vid_stopp_01", confirm=True, _=None))
            self.assertEqual(ctx.exception.status_code, 404)

    def test_http_endpoint_admin_security(self):
        """Verify endpoints are registered in FastAPI and protected by require_admin."""
        client = TestClient(app)
        # Without token, must return 401 Unauthorized / 403 Forbidden
        resp = client.get("/api/admin/media")
        self.assertIn(resp.status_code, (401, 403))

        # With mock admin override
        app.dependency_overrides[require_admin] = lambda: {"sub": "admin_test", "role": "admin"}
        try:
            with patch.object(server, "db", self.mock_db):
                resp = client.get("/api/admin/media")
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.json()["total"], 2)
        finally:
            app.dependency_overrides.pop(require_admin, None)

    def test_shared_upload_persists_optimized_image_and_returns_stable_link(self):
        from PIL import Image

        image_bytes = io.BytesIO()
        Image.new("RGB", (2200, 1000), "navy").save(image_bytes, format="PNG")
        upload = UploadFile(
            filename="Høyre regelen.png",
            file=io.BytesIO(image_bytes.getvalue()),
            headers=Headers({"content-type": "image/png"}),
        )
        with patch.object(server, "AsyncIOMotorGridFSBucket", _MockGridFSBucket):
            result = asyncio.run(admin_upload_media_file(upload, replace_file_id=None, _=None))

        self.assertEqual(result["media_type"], "image")
        self.assertEqual(result["content_type"], "image/webp")
        self.assertEqual(result["link_name"], "hoeyre_regelen")
        self.assertEqual(result["url"], "/api/media/files/64b64c000000000000000001")
        self.assertTrue(result["transformed"])
        self.assertEqual(_MockGridFSBucket.uploads[0][0], "hoeyre_regelen.webp")

    def test_admin_html_ui_components(self):
        """Verify admin.html has the tab, media view container, and CRUD functions."""
        admin_html_path = Path(__file__).resolve().parent.parent / "admin.html"
        html = admin_html_path.read_text(encoding="utf-8")
        self.assertIn('id="tab-media"', html)
        self.assertIn('id="media-view"', html)
        self.assertIn("loadAdminMedia", html)
        self.assertIn("openAdminMediaModal", html)
        self.assertIn("saveAdminMedia", html)
        self.assertIn("deleteAdminMedia", html)

    def test_shared_attachment_workflow_covers_all_admin_content_owners(self):
        """Every web-first admin content editor exposes the same reusable upload flow."""
        admin_html_path = Path(__file__).resolve().parent.parent / "admin.html"
        html = admin_html_path.read_text(encoding="utf-8")
        for owner_type in (
            "question",
            "book_section",
            "studybook",
            "traffic_sign",
            "video",
            "podcast",
            "glossary",
        ):
            self.assertIn(f"mediaAttachmentsPanel('{owner_type}'", html)
            self.assertIn(owner_type, server.ADMIN_MEDIA_OWNERS)
        self.assertIn("/admin/media-links/", html)
        self.assertIn("image/jpeg,image/png,image/webp", html)
        self.assertIn("video/mp4,video/webm", html)
        self.assertIn("audio/mpeg", html)
        self.assertIn("application/pdf", html)

    def test_uncategorized_uploads_use_neutral_general_category(self):
        self.assertEqual(AdminMediaCreate.model_fields["category"].default, "generelt")
        self.assertIn("generelt", CATEGORIES)

    def test_video_modal_ui_components(self):
        """Verify admin.html has MP4/file upload zone, file_path field, and video preview."""
        admin_html_path = Path(__file__).resolve().parent.parent / "admin.html"
        html = admin_html_path.read_text(encoding="utf-8")
        self.assertIn('id="vd-file-path"', html)
        self.assertIn('id="vd-preview-box"', html)
        self.assertIn("uploadVideoModalFile", html)
        self.assertIn("updateVideoPreview", html)
        self.assertIn("video_stoppelengde_80.mp4", html)

    def test_admin_create_video_with_file_path(self):
        """Videos can be created with direct file_path (e.g. MP4) without YouTube URL."""
        server.db = _MockDatabase()
        payload = {
            "title_no": "Stoppelengde i 80 km/t",
            "file_path": "/public_assets/video_stoppelengde_80.mp4",
            "topic_tags": ["Bremsing"],
        }
        res = asyncio.run(server.admin_create_video(payload))
        self.assertTrue(res["id"])
        self.assertEqual(res["title_no"], "Stoppelengde i 80 km/t")
        self.assertEqual(res["file_path"], "/public_assets/video_stoppelengde_80.mp4")
        self.assertEqual(res["thumbnail_url"], "/api/assets/thumbs/thumb_stoppelengde_80.jpg")

    def test_admin_create_video_requires_title_and_source(self):
        """Must have title_no and either youtube_url or file_path."""
        server.db = _MockDatabase()
        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(server.admin_create_video({"file_path": "/public_assets/video_test.mp4"}))
        self.assertEqual(ctx.exception.status_code, 400)

        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(server.admin_create_video({"title_no": "Kun tittel"}))
        self.assertEqual(ctx.exception.status_code, 400)

    def test_admin_delete_video_success(self):
        """Video deletion works reliably for video documents."""
        server.db = _MockDatabase()
        payload = {
            "title_no": "Slettes video",
            "file_path": "/public_assets/video_stoppelengde_50.mp4",
        }
        created = asyncio.run(server.admin_create_video(payload))
        video_id = created["id"]
        del_res = asyncio.run(server.admin_delete_video(video_id))
        self.assertEqual(del_res["message"], "Deleted")
        self.assertEqual(del_res["id"], video_id)

    def test_is_safe_catalog_url_allows_public_assets_and_spaces(self):
        from media_catalog import is_safe_catalog_url
        self.assertTrue(is_safe_catalog_url("/public_assets/video_stoppelengde_80.mp4"))
        self.assertTrue(is_safe_catalog_url("/public_assets/stopping_distance_80km h.mp4"))
        self.assertTrue(is_safe_catalog_url("/static/videos/test.mp4"))


if __name__ == "__main__":
    unittest.main()

