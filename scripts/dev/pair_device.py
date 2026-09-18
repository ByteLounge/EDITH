"""Script to pair a device with EDITH Core."""
import subprocess
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
agent_dir = root_dir / "windows-agent"

if __name__ == "__main__":
    subprocess.run([
        sys.executable, "-m", "edith_agent.main", "--pair"
    ], cwd=agent_dir)
