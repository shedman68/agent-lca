#!/usr/bin/env python3
"""Save one PNG of every app page into docs/kb/screenshots/.

Offline: Streamlit is started on localhost and nothing is sent off the machine.
Needs the Playwright package and the Chrome already installed on the machine
(``pip install playwright``; no browser download). Run from the repo root:

    python3 scripts/screenshots.py
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "kb" / "screenshots"
# Sidebar label, on-page heading, file. The package page's heading is longer than its nav label.
PAGES = [
    ("Overall picture", "Overall picture", "overall-picture.png"),
    ("Findings", "Findings", "findings.png"),
    ("Package", "Measures package", "package.png"),
    ("Needs a human", "Needs a human", "needs-a-human.png"),
    ("Ask the data", "Ask the data", "ask.png"),
    ("Next year", "Next year", "next-year.png"),
]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_until_up(port: int, proc: subprocess.Popen, timeout: float = 40) -> None:
    import urllib.request

    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{port}/"
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"streamlit exited with {proc.returncode}")
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return
        except OSError:
            time.sleep(0.3)
    raise TimeoutError(f"streamlit did not answer on {port}")


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright is not installed. From the repo root: pip install playwright", file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    port = _free_port()
    env = os.environ.copy()
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "app/app.py",
            "--server.headless", "true",
            "--server.address", "127.0.0.1",
            "--server.port", str(port),
            "--browser.gatherUsageStats", "false",
        ],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    try:
        _wait_until_up(port, proc)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                channel="chrome",
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            # Tall viewport: Streamlit scrolls inside the page, so full_page stops at the window.
            page = browser.new_page(viewport={"width": 1440, "height": 2400})
            page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle", timeout=60000)
            for link, heading, filename in PAGES:
                page.get_by_role("link", name=link, exact=True).click()
                page.get_by_role("heading", name=heading, exact=True).wait_for(timeout=30000)
                page.wait_for_timeout(800)
                target = OUT_DIR / filename
                page.screenshot(path=str(target), full_page=False)
                print(f"wrote {target.relative_to(ROOT)}")
            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
