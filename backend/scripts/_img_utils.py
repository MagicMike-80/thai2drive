"""
Helper to convert an image file to a compact Base64 data-URI.
Returns: data:image/jpeg;base64,...
"""
import base64
import io
from PIL import Image


def image_to_base64(path: str, max_dim: int = 500, quality: int = 82) -> str:
    img = Image.open(path)
    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        img = img.resize(
            (int(img.size[0] * ratio), int(img.size[1] * ratio)),
            Image.LANCZOS,
        )
    if img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return "data:image/jpeg;base64," + b64
