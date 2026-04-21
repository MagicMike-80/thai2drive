"""Refine existing app icon: larger T2D, more spacing, more separation from flag."""
import asyncio
import base64
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent  # noqa: E402

MASTER = Path("/app/frontend/assets/icons/master_1024.png")
OUT = Path("/app/frontend/assets/icons/master_1024_v2.png")
BACKUP = Path("/app/frontend/assets/icons/master_1024_v1_backup.png")

PROMPT = """Use this exact app icon as reference and make ONLY these specific small improvements,
keeping everything else identical (same premium 3D style, same rounded-square shape, same dark navy
blue gradient background, same Thai flag wave at top, same road with yellow edges and dashed center line,
same orange color for "2", same white color for "T" and "D", same 3D beveled letter style):

1. Make the "T2D" text noticeably LARGER (bolder and bigger, filling more of the center area).
2. Move the "T2D" text slightly DOWNWARD, so there is a clearer gap between the Thai flag wave
   at the top and the text below it. The flag should not overlap the letters.
3. Add more horizontal SPACING between the letters T, 2, and D — so each letter is clearly
   isolated and readable.
4. Ensure the text is crisp and readable even at very small sizes (48×48 pixels) — strong contrast,
   bold strokes, no thin parts.

Do not change colors, style, background, flag design, or road design. Keep the icon composition
and premium 3D aesthetic. Output 1024×1024 square PNG, no blur, sharp edges."""


async def main():
    api_key = os.getenv("EMERGENT_LLM_KEY") or "sk-emergent-b48A3D57008C8350c6"

    ref_bytes = MASTER.read_bytes()
    ref_b64 = base64.b64encode(ref_bytes).decode("utf-8")

    chat = LlmChat(
        api_key=api_key,
        session_id="t2d-icon-refine-v2",
        system_message="You are an expert mobile app icon designer. Edit the provided icon precisely as requested, preserving all other elements exactly.",
    )
    chat.with_model("gemini", "gemini-3.1-flash-image-preview").with_params(modalities=["image", "text"])

    msg = UserMessage(text=PROMPT, file_contents=[ImageContent(ref_b64)])
    text, images = await chat.send_message_multimodal_response(msg)
    print(f"Text: {(text or '')[:300]}")
    if not images:
        print("ERROR: No image returned")
        sys.exit(1)
    img = images[0]
    data = base64.b64decode(img["data"])
    OUT.write_bytes(data)
    print(f"Saved refined icon -> {OUT} ({len(data)//1024} KB, mime={img.get('mime_type')})")


asyncio.run(main())
