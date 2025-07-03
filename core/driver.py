#!/usr/bin/env python3
"""
🚗 Claude Driver - Browser Automation for AI-Human Collaboration

CLAUDE: This is your main browser automation tool.
ALWAYS read CLAUDE.md workflow before using this tool!

Usage:
    python core/driver.py http    # Start HTTP API server
    python core/driver.py         # Interactive mode
"""

import asyncio
from playwright.async_api import async_playwright
import pyautogui
from PIL import Image
import os
import time
import json
import logging
from datetime import datetime
from bs4 import BeautifulSoup, Comment
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn


def get_claude_workflow_reminder():
    """Return workflow guidance for Claude"""
    return {
        "workflow_reminder": [
            "1. ALWAYS read CLAUDE.md first",
            "2. Capture page state before extraction",
            "3. Analyze with tools/page_analyzer.py",
            "4. Test on small samples first",
            "5. Save intermediate results frequently",
        ],
        "next_steps_after_capture": [
            "Use Read tool on the HTML file returned",
            "Run: python tools/page_analyzer.py <html_file>",
            "Create/use site-specific extractor in sites/",
            "Validate results before continuing",
        ],
        "documentation": "Read CLAUDE.md for complete workflow guide",
    }


class BrowserController:
    def __init__(self):
        self.browser = None
        self.page = None
        self.playwright = None
        self.capture_counter = self._load_counter()

        # Setup logging with session organization
        session_id = datetime.now().strftime("%Y-%m-%d_%H-%M")
        log_dir = f"./sessions/{session_id}"
        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(f"{log_dir}/session.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)
        self.session_dir = log_dir

    def _load_counter(self):
        """Load the persistent capture counter"""
        counter_file = "./tmp/capture_counter.txt"
        try:
            if os.path.exists(counter_file):
                with open(counter_file, "r") as f:
                    return int(f.read().strip())
        except:
            pass
        return 0

    def _save_counter(self):
        """Save the capture counter"""
        os.makedirs("./tmp", exist_ok=True)
        with open("./tmp/capture_counter.txt", "w") as f:
            f.write(str(self.capture_counter))

    async def start_browser(self):
        """Start the browser instance"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
            ],
        )

        self.page = await self.browser.new_page()

        # Get screen dimensions and set to full height
        screen_size = pyautogui.size()
        await self.page.set_viewport_size(
            {"width": 1280, "height": screen_size.height - 100}
        )

        # Set user agent to look more human
        await self.page.set_user_agent(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.logger.info("Browser started successfully")

    async def capture_state(self):
        """Capture current page state with enhanced analysis"""
        if not self.page:
            raise Exception("Browser not started")

        self.capture_counter += 1
        self._save_counter()

        # Get page info
        url = self.page.url
        title = await self.page.title()
        timestamp = time.time()

        # Create filenames
        html_file = f"./tmp/page_{self.capture_counter:03d}.html"
        screenshot_file = f"./tmp/screenshot_{self.capture_counter:03d}.png"
        analysis_file = f"./tmp/page_{self.capture_counter:03d}_analysis.json"

        # Get HTML content
        html_content = await self.page.content()

        # Clean HTML for analysis while preserving structure
        cleaned_html = self._clean_html_for_analysis(html_content)

        # Save HTML
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(cleaned_html)

        # Take screenshot and optimize
        await self.page.screenshot(path=screenshot_file, full_page=True)
        self._optimize_screenshot(screenshot_file)

        # Generate analysis hints for Claude
        analysis = self._analyze_page_structure(cleaned_html, url, title)
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Captured: {html_file}, {screenshot_file}")

        result = {
            "html": html_file,
            "screenshot": screenshot_file,
            "analysis": analysis_file,
            "url": url,
            "title": title,
            "timestamp": timestamp,
        }

        # Add Claude workflow guidance
        result.update(get_claude_workflow_reminder())

        return result

    def _clean_html_for_analysis(self, html_content):
        """Clean HTML while preserving structure for extraction"""
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove noise but keep data attributes
        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Add analysis hints
        self._add_analysis_hints(soup)

        return str(soup)

    def _add_analysis_hints(self, soup):
        """Add data attributes to help Claude identify patterns"""
        # Mark potential containers
        for elem in soup.find_all(["div", "section", "article"]):
            children = elem.find_all(["a", "span", "p", "h1", "h2", "h3"])
            if len(children) > 3:
                elem["data-claude-container"] = "potential-item"

        # Mark prices
        for elem in soup.find_all(string=re.compile(r"[¥$€£]\d")):
            if elem.parent:
                elem.parent["data-claude-price"] = "detected"

        # Mark dates
        for elem in soup.find_all(string=re.compile(r"\d{4}|\w+\s+\d+,\s*\d{4}")):
            if elem.parent:
                elem.parent["data-claude-date"] = "detected"

    def _analyze_page_structure(self, html_content, url, title):
        """Generate analysis for Claude"""
        soup = BeautifulSoup(html_content, "html.parser")

        analysis = {
            "page_info": {
                "url": url,
                "title": title,
                "timestamp": datetime.now().isoformat(),
            },
            "structure": {
                "total_elements": len(soup.find_all()),
                "containers": len(soup.find_all(["div", "section", "article"])),
                "links": len(soup.find_all("a")),
                "forms": len(soup.find_all("form")),
                "tables": len(soup.find_all("table")),
            },
            "detected_patterns": {
                "potential_items": len(
                    soup.find_all(attrs={"data-claude-container": "potential-item"})
                ),
                "prices_detected": len(
                    soup.find_all(attrs={"data-claude-price": "detected"})
                ),
                "dates_detected": len(
                    soup.find_all(attrs={"data-claude-date": "detected"})
                ),
            },
            "suggested_selectors": self._suggest_selectors(soup),
            "claude_hints": [
                "Use tools/page_analyzer.py for detailed analysis",
                "Look for repeated patterns in containers",
                "Check data-claude-* attributes for detected elements",
                "Test selectors on small samples first",
            ],
        }

        return analysis

    def _suggest_selectors(self, soup):
        """Suggest likely selectors for common patterns"""
        suggestions = {}

        # Common container patterns
        container_classes = []
        for elem in soup.find_all("div", class_=True):
            classes = elem.get("class", [])
            for cls in classes:
                if any(
                    keyword in cls.lower()
                    for keyword in ["item", "order", "product", "card", "box"]
                ):
                    container_classes.append(f".{cls}")

        if container_classes:
            suggestions["containers"] = list(set(container_classes[:5]))

        # Pagination patterns
        pagination_selectors = []
        for elem in soup.find_all(["a", "button"]):
            text = elem.get_text().strip().lower()
            if any(word in text for word in ["next", "more", "次", "→"]):
                if elem.get("class"):
                    pagination_selectors.append(f".{' '.join(elem['class'])}")

        if pagination_selectors:
            suggestions["pagination"] = list(set(pagination_selectors[:3]))

        return suggestions

    def _optimize_screenshot(self, screenshot_path):
        """Optimize screenshot for Claude analysis"""
        try:
            with Image.open(screenshot_path) as img:
                # Resize to reasonable width for analysis
                if img.width > 800:
                    ratio = 800 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((800, new_height), Image.Resampling.LANCZOS)
                    img.save(screenshot_path, optimize=True, quality=85)
        except Exception as e:
            self.logger.warning(f"Screenshot optimization failed: {e}")

    async def navigate_to(self, url, wait_load=True):
        """Navigate to URL with smart waiting"""
        if not self.page:
            await self.start_browser()

        try:
            if wait_load:
                await self.page.goto(url, wait_until="networkidle", timeout=30000)
            else:
                await self.page.goto(url, timeout=30000)

            # Wait a bit for dynamic content
            await asyncio.sleep(2)

            self.logger.info(f"Navigated to: {url}")
            return {"status": "success", "url": url, "title": await self.page.title()}
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            raise Exception(f"Navigation failed: {e}")

    async def close(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.logger.info("Browser closed")


# HTTP API with workflow enforcement
app = FastAPI(
    title="Claude Driver",
    description="Browser automation designed for AI-human collaboration",
    version="1.0.0",
)

# Global browser controller
controller = BrowserController()


class NavigateRequest(BaseModel):
    url: str
    wait_load: Optional[bool] = True


@app.get("/")
async def root():
    """API root with Claude guidance"""
    return {
        "service": "Claude Driver",
        "status": "ready",
        "claude_instructions": get_claude_workflow_reminder(),
        "endpoints": {
            "GET /status": "Check browser status and get workflow guidance",
            "POST /navigate": "Navigate to URL",
            "POST /capture": "Capture current page state",
            "GET /docs": "API documentation",
        },
    }


@app.get("/status")
async def get_status():
    """Get browser status with Claude workflow guidance"""
    current_url = "about:blank"
    current_title = ""

    if controller.page:
        try:
            current_url = controller.page.url
            current_title = await controller.page.title()
        except:
            pass

    # Find latest captures
    import glob

    html_files = glob.glob("./tmp/page_*.html")
    latest_capture = None
    if html_files:
        latest_capture = max(html_files, key=os.path.getmtime)

    return {
        "status": "ready" if controller.page else "not_initialized",
        "url": current_url,
        "title": current_title,
        "capture_count": controller.capture_counter,
        "latest_capture": latest_capture,
        "session_dir": controller.session_dir,
        **get_claude_workflow_reminder(),
    }


@app.post("/navigate")
async def navigate(request: NavigateRequest):
    """Navigate to URL with Claude workflow guidance"""
    try:
        result = await controller.navigate_to(request.url, request.wait_load)
        result.update(get_claude_workflow_reminder())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/capture")
async def capture():
    """Capture current page state with analysis for Claude"""
    try:
        result = await controller.capture_state()

        # Add specific guidance for what Claude should do next
        result["claude_next_actions"] = [
            f"1. Read the captured HTML: Use Read tool on {result['html']}",
            f"2. Analyze page structure: python tools/page_analyzer.py {result['html']}",
            f"3. Check analysis hints: Use Read tool on {result['analysis']}",
            "4. Create/run site-specific extractor in sites/ directory",
            "5. Test extraction on small sample first",
        ]

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    await controller.close()


def main():
    """Main entry point with mode selection"""
    import sys

    # Show Claude the workflow reminder
    print("🚗 Claude Driver - Browser Automation")
    print("=" * 50)
    print("📖 CLAUDE: Read CLAUDE.md for complete workflow guide!")
    print()

    if len(sys.argv) > 1 and sys.argv[1] == "http":
        print("🌐 Starting HTTP API server...")
        print("📋 Available endpoints:")
        print("  GET  /status   - Browser status + workflow guidance")
        print("  POST /navigate - Navigate to URL")
        print("  POST /capture  - Capture page state with analysis")
        print("  GET  /docs     - Interactive API documentation")
        print()
        print("🔗 API will be available at: http://localhost:8000")
        print("📚 Documentation at: http://localhost:8000/docs")
        print()

        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("💡 Usage:")
        print("  python core/driver.py http    # Start HTTP API server")
        print("  python core/driver.py         # This help message")
        print()
        print("📖 CLAUDE: Always start with HTTP mode for best collaboration!")


if __name__ == "__main__":
    main()

