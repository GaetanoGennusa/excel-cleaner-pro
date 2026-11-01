"""Start a loopback-only Streamlit subprocess, check health, and always stop it."""
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8519", "--server.address", "127.0.0.1", "--server.headless", "true"],
        cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    try:
        for _ in range(40):
            if process.poll() is not None:
                raise RuntimeError("Streamlit exited before startup; check port 8519 and dependencies.")
            try:
                with urlopen("http://127.0.0.1:8519/_stcore/health", timeout=1) as response:
                    if response.status == 200 and response.read() == b"ok":
                        print("Streamlit loopback health check: HTTP 200 ok")
                        return
            except (URLError, TimeoutError):
                pass
            time.sleep(.25)
        raise RuntimeError("Streamlit health check timed out")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__":
    main()
