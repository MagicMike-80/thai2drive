"""Compatibility wrapper for backend/scripts/import_michael_videos.py."""
from backend.scripts.import_michael_videos import *  # noqa: F401, F403
from backend.scripts.import_michael_videos import validate_video_spec  # noqa: F401

if __name__ == "__main__":
    from backend.scripts.import_michael_videos import main
    raise SystemExit(main())
