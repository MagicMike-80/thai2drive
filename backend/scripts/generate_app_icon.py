"""Generate Thai2Drive app icon master (1024x1024) using Gemini Nano Banana."""
import asyncio
import base64
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

from emergentintegrations.llm.chat import LlmChat, UserMessage  # noqa: E402

OUTPUT = Path("/app/frontend/assets/icons/master_1024.png")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

PROMPT = """Create a premium, modern mobile app icon design, 1024x1024 square PNG, sharp edges, no blur.

DESIGN:
- Background: dark navy-blue gradient (deep navy top → slightly lighter blue bottom, clean, flat-looking — not too much 3D)
- Centered bold text "T2D" in large modern sans-serif letters:
  * "T" is bright white
  * "2" is bold orange/yellow (vivid, high-contrast highlight)
  * "D" is bright white
  * Letters should be flat with subtle depth, not heavy 3D
- Above the text: a small, clean Thai flag waving ribbon (red, white, blue horizontal stripes, waving)
- Below the "T2D" text: a small, stylized minimalist road element — a simple dark grey road with white dashed center lines, receding in perspective toward the horizon (think tiny, subtle, centered)
- Overall style: modern, flat-ish, sharp, high contrast, similar to premium Duolingo / iOS style icons
- No shadows, no gloss, no text other than "T2D"
- Must be readable and recognizable when scaled down to 48x48 pixels
- Safe padding around edges (no content touches edges)
- Square composition, centered layout

Communicates: driving education, Thai identity, learning driving theory.
Output: clean 1024x1024 app icon PNG."""


async def main():
    api_key = os.getenv("EMERGENT_LLM_KEY") or "sk-emergent-b48A3D57008C8350c6"
    chat = LlmChat(
        api_key=api_key,
        session_id="t2d-icon-master",
        system_message="You are an expert mobile app icon designer.",
    )
    chat.with_model("gemini", "gemini-3.1-flash-image-preview").with_params(modalities=["image", "text"])
    msg = UserMessage(text=PROMPT)
    text, images = await chat.send_message_multimodal_response(msg)
    print(f"Text: {(text or '')[:200]}")
    if not images:
        print("No images returned")
        sys.exit(1)
    img = images[0]
    data = base64.b64decode(img["data"])
    OUTPUT.write_bytes(data)
    print(f"Saved master icon ({len(data)//1024} KB, mime={img.get('mime_type')}) -> {OUTPUT}")


asyncio.run(main())
