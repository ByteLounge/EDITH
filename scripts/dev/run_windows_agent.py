"""Script to launch the EDITH Windows Agent."""
import subprocess
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
agent_dir = root_dir / "windows-agent"

if __name__ == "__main__":
    print("Starting EDITH Windows Agent...")
    subprocess.run([
        sys.executable, "-m", "edith_agent.main"
    ] + sys.argv[1:], cwd=agent_dir)
