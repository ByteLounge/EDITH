"""Script to launch the EDITH Core FastAPI backend."""
import subprocess
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
backend_dir = root_dir / "backend"

if __name__ == "__main__":
    print("Starting EDITH Core Backend on http://0.0.0.0:8000 ...")
    subprocess.run([
        sys.executable, "-m", "uvicorn", "app.main:app",
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ], cwd=backend_dir)
