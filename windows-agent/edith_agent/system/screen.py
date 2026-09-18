import io
import base64
import tempfile
from pathlib import Path
from typing import Dict, Any, Tuple
from PIL import ImageGrab


def take_screenshot() -> Tuple[bool, Dict[str, Any]]:
    """Captures a screenshot of the primary display."""
    try:
        image = ImageGrab.grab()
        # Save a temporary screenshot file
        temp_dir = Path(tempfile.gettempdir()) / "edith"
        temp_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = temp_dir / "latest_screenshot.png"
        image.save(screenshot_path, format="PNG")

        # Also generate a base64 thumbnail for quick transmission
        image.thumbnail((640, 360))
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=70)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return True, {
            "message": "Screenshot captured successfully.",
            "file_path": str(screenshot_path),
            "thumbnail_base64": img_str,
            "width": image.width,
            "height": image.height
        }
    except Exception as e:
        return False, {
            "code": "SCREENSHOT_FAILED",
            "message": f"Failed to capture screenshot: {str(e)}"
        }
