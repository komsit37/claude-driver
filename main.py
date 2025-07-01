import asyncio
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright
import pyautogui
from PIL import Image
import os
import time
import json
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import re


class BrowserController:
    def __init__(self):
        self.browser = None
        self.page = None
        self.playwright = None
        self.capture_counter = self._load_counter()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('./tmp/browser.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_counter(self):
        """Load the persistent capture counter"""
        counter_file = './tmp/capture_counter.txt'
        try:
            if os.path.exists(counter_file):
                with open(counter_file, 'r') as f:
                    return int(f.read().strip())
        except:
            pass
        return 0
    
    def _save_counter(self):
        """Save the persistent capture counter"""
        counter_file = './tmp/capture_counter.txt'
        try:
            with open(counter_file, 'w') as f:
                f.write(str(self.capture_counter))
        except:
            pass
    
    def _clean_html_for_scraping(self, html_content):
        """Clean HTML content to reduce tokens while preserving scraping-relevant data"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove non-content elements that don't help with scraping
        tags_to_remove = [
            'script', 'style', 'noscript', 'meta', 'link', 'base',
            'object', 'embed', 'applet', 'iframe', 'frame', 'frameset',
            'map', 'area', 'canvas', 'audio', 'video', 'source', 'track'
        ]
        
        for tag in tags_to_remove:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, soup.__class__.Comment)):
            comment.extract()
        
        # Remove attributes that don't help with scraping but keep important ones
        important_attrs = {
            'href', 'src', 'alt', 'title', 'value', 'placeholder', 'name', 
            'id', 'class', 'type', 'action', 'method', 'for', 'role',
            'data-testid', 'data-test', 'aria-label', 'aria-labelledby'
        }
        
        for element in soup.find_all():
            if element.attrs:
                # Keep only important attributes
                attrs_to_keep = {}
                for attr, value in element.attrs.items():
                    if attr in important_attrs:
                        # Simplify class attributes - keep only first few classes
                        if attr == 'class' and isinstance(value, list):
                            attrs_to_keep[attr] = value[:3]  # Keep max 3 classes
                        else:
                            attrs_to_keep[attr] = value
                element.attrs = attrs_to_keep
        
        # Remove empty elements that don't contribute content
        for element in soup.find_all():
            if (not element.get_text(strip=True) and 
                not element.find('img') and 
                not element.find('input') and 
                not element.find('button') and
                not element.name in ['br', 'hr', 'input', 'img', 'area']):
                element.decompose()
        
        # Normalize whitespace
        cleaned_html = str(soup)
        # Remove excessive whitespace
        cleaned_html = re.sub(r'\s+', ' ', cleaned_html)
        cleaned_html = re.sub(r'>\s+<', '><', cleaned_html)
        
        original_size = len(html_content)
        cleaned_size = len(cleaned_html)
        reduction_percent = ((original_size - cleaned_size) / original_size) * 100
        
        self.logger.info(f"HTML cleaned: {original_size} -> {cleaned_size} bytes ({reduction_percent:.1f}% reduction)")
        
        return cleaned_html
    
    async def start(self):
        """Start browser and return initial status"""
        self.logger.info("Starting browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            channel="chrome"  # Use installed Chrome instead of Chromium
        )
        self.page = await self.browser.new_page()
        await self.page.goto("about:blank")
        self.logger.info("Browser started successfully")
        return await self.capture_state()
    
    async def capture_state(self):
        """Capture both HTML and screenshot"""
        self.logger.info("Capturing page state...")
        
        # Increment counter for new capture
        self.capture_counter += 1
        self._save_counter()
        
        # Get HTML content and clean it for scraping
        html_content = await self.page.content()
        cleaned_html = self._clean_html_for_scraping(html_content)
        html_filename = f"page_{self.capture_counter:03d}.html"
        html_path = f"./tmp/{html_filename}"
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_html)
        
        # Take screenshot (simplified)
        screenshot_filename = f"screenshot_{self.capture_counter:03d}.png"
        screenshot_path = f"./tmp/{screenshot_filename}"
        
        await self.page.screenshot(path=screenshot_path, full_page=False)  # Viewport only for speed
        
        # Resize screenshot for efficiency
        img = Image.open(screenshot_path)
        width, height = img.size
        if width > 800:
            new_width = 800
            new_height = int(height * (new_width / width))
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            img.save(screenshot_path, optimize=True, quality=85)
        
        self.logger.info(f"State captured - HTML: {html_path}, Screenshot: {screenshot_path}")
        
        return {
            "html": html_path,
            "screenshot": screenshot_path,
            "url": self.page.url,
            "title": await self.page.title()
        }
    
    async def navigate(self, url):
        """Navigate to URL"""
        self.logger.info(f"Navigating to: {url}")
        await self.page.goto(url, wait_until='networkidle')
        self.logger.info(f"Navigation completed - Current URL: {self.page.url}")
        return await self.capture_state()
    
    async def click(self, x, y):
        """Click at coordinates"""
        self.logger.info(f"Clicking at coordinates: ({x}, {y})")
        await self.page.mouse.click(x, y)
        await self.page.wait_for_timeout(1000)
        self.logger.info("Click completed")
        return await self.capture_state()
    
    async def type_text(self, text):
        """Type text at current focus"""
        self.logger.info(f"Typing text: {text}")
        await self.page.keyboard.type(text)
        self.logger.info("Text input completed")
        return await self.capture_state()
    
    async def press_key(self, key):
        """Press a key"""
        self.logger.info(f"Pressing key: {key}")
        await self.page.keyboard.press(key)
        self.logger.info("Key press completed")
        return await self.capture_state()
    
    async def scroll(self, direction="down", amount=3):
        """Scroll the page"""
        self.logger.info(f"Scrolling {direction} by {amount} units")
        if direction.lower() == "down":
            await self.page.mouse.wheel(0, amount * 100)
        elif direction.lower() == "up":
            await self.page.mouse.wheel(0, -amount * 100)
        elif direction.lower() == "left":
            await self.page.mouse.wheel(-amount * 100, 0)
        elif direction.lower() == "right":
            await self.page.mouse.wheel(amount * 100, 0)
        
        await self.page.wait_for_timeout(1000)  # Wait for scroll to complete
        return await self.capture_state()
    
    async def wait_for_element(self, selector, timeout=10000):
        """Wait for element to appear"""
        self.logger.info(f"Waiting for element: {selector}")
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            self.logger.info(f"Element found: {selector}")
            return await self.capture_state()
        except Exception as e:
            self.logger.error(f"Element not found: {selector} - {str(e)}")
            return {"error": f"Element not found: {selector}"}
    
    async def find_elements_by_text(self, text, tag="*"):
        """Find elements containing specific text"""
        self.logger.info(f"Finding elements with text: {text}")
        elements = await self.page.locator(f"{tag}:has-text('{text}')").all()
        
        element_info = []
        for i, element in enumerate(elements[:10]):  # Limit to first 10
            try:
                box = await element.bounding_box()
                if box:
                    element_info.append({
                        "index": i,
                        "text": await element.text_content(),
                        "tag": await element.tag_name(),
                        "x": box["x"] + box["width"] / 2,
                        "y": box["y"] + box["height"] / 2,
                        "width": box["width"],
                        "height": box["height"]
                    })
            except:
                continue
        
        self.logger.info(f"Found {len(element_info)} elements with text: {text}")
        return {
            "elements": element_info,
            "count": len(element_info),
            "search_text": text
        }
    
    async def extract_links(self):
        """Extract all links from current page"""
        self.logger.info("Extracting all links from page")
        links = await self.page.locator('a[href]').all()
        
        link_data = []
        for link in links[:50]:  # Limit to first 50 links
            try:
                href = await link.get_attribute('href')
                text = await link.text_content()
                if href and text and text.strip():
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = self.page.url.split('/')[0] + '//' + self.page.url.split('/')[2] + href
                    elif not href.startswith('http'):
                        continue
                    
                    link_data.append({
                        "text": text.strip(),
                        "url": href,
                        "domain": href.split('/')[2] if '/' in href else href
                    })
            except:
                continue
        
        self.logger.info(f"Extracted {len(link_data)} links")
        return {"links": link_data, "count": len(link_data)}
    
    async def extract_forms(self):
        """Extract all forms and their fields"""
        self.logger.info("Extracting forms from page")
        forms = await self.page.locator('form').all()
        
        form_data = []
        for i, form in enumerate(forms):
            try:
                # Get form attributes
                action = await form.get_attribute('action') or ''
                method = await form.get_attribute('method') or 'GET'
                
                # Get all input fields
                inputs = await form.locator('input, select, textarea').all()
                fields = []
                
                for input_elem in inputs:
                    field_type = await input_elem.get_attribute('type') or 'text'
                    name = await input_elem.get_attribute('name') or ''
                    placeholder = await input_elem.get_attribute('placeholder') or ''
                    required = await input_elem.get_attribute('required') is not None
                    
                    if name:  # Only include fields with names
                        fields.append({
                            "name": name,
                            "type": field_type,
                            "placeholder": placeholder,
                            "required": required
                        })
                
                form_data.append({
                    "index": i,
                    "action": action,
                    "method": method.upper(),
                    "fields": fields,
                    "field_count": len(fields)
                })
            except:
                continue
        
        self.logger.info(f"Extracted {len(form_data)} forms")
        return {"forms": form_data, "count": len(form_data)}
    
    async def get_page_structure(self):
        """Get semantic structure of the page"""
        self.logger.info("Analyzing page structure")
        
        structure = {
            "title": await self.page.title(),
            "url": self.page.url,
            "headings": [],
            "main_content": "",
            "navigation": [],
            "buttons": [],
            "images": []
        }
        
        # Extract headings (h1-h6)
        for level in range(1, 7):
            headings = await self.page.locator(f'h{level}').all()
            for heading in headings:
                text = await heading.text_content()
                if text and text.strip():
                    structure["headings"].append({
                        "level": level,
                        "text": text.strip()
                    })
        
        # Extract main content areas
        main_selectors = ['main', '[role="main"]', '.main', '#main', '.content', '#content']
        for selector in main_selectors:
            try:
                main = await self.page.locator(selector).first
                if main:
                    content = await main.text_content()
                    if content and len(content) > len(structure["main_content"]):
                        structure["main_content"] = content.strip()[:1000]  # Limit length
                    break
            except:
                continue
        
        # Extract navigation links
        nav_selectors = ['nav a', '[role="navigation"] a', '.nav a', '.navigation a']
        for selector in nav_selectors:
            try:
                nav_links = await self.page.locator(selector).all()
                for link in nav_links[:10]:  # Limit to 10
                    text = await link.text_content()
                    href = await link.get_attribute('href')
                    if text and text.strip():
                        structure["navigation"].append({
                            "text": text.strip(),
                            "url": href
                        })
                if structure["navigation"]:
                    break
            except:
                continue
        
        # Extract buttons
        buttons = await self.page.locator('button, input[type="button"], input[type="submit"]').all()
        for button in buttons[:10]:  # Limit to 10
            try:
                text = await button.text_content() or await button.get_attribute('value') or ''
                if text.strip():
                    structure["buttons"].append(text.strip())
            except:
                continue
        
        # Extract images with alt text
        images = await self.page.locator('img[alt]').all()
        for img in images[:10]:  # Limit to 10
            try:
                alt = await img.get_attribute('alt')
                src = await img.get_attribute('src')
                if alt and alt.strip():
                    structure["images"].append({
                        "alt": alt.strip(),
                        "src": src
                    })
            except:
                continue
        
        return structure
    
    async def smart_extract(self, data_type="auto"):
        """Smart extraction based on page content"""
        self.logger.info(f"Smart extraction for data type: {data_type}")
        
        html_content = await self.page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        extracted_data = {
            "extraction_type": data_type,
            "timestamp": datetime.now().isoformat(),
            "url": self.page.url
        }
        
        if data_type == "auto" or data_type == "products":
            # Extract product-like data
            products = []
            
            # Common product selectors
            product_selectors = [
                '[data-testid*="product"]',
                '.product',
                '[class*="product"]',
                '[class*="item"]',
                '.listing',
                '[class*="listing"]'
            ]
            
            for selector in product_selectors:
                try:
                    elements = await self.page.locator(selector).all()
                    for element in elements[:20]:  # Limit to 20
                        try:
                            text = await element.text_content()
                            if text and len(text.strip()) > 50:  # Substantial content
                                # Look for prices
                                price_match = re.search(r'[¥$€£]\s*[\d,]+(?:\.\d{2})?', text)
                                price = price_match.group(0) if price_match else None
                                
                                # Look for titles (first line or strong text)
                                title_elem = await element.locator('h1, h2, h3, h4, strong, .title, [class*="title"]').first
                                title = await title_elem.text_content() if title_elem else text.split('\n')[0]
                                
                                products.append({
                                    "title": title.strip() if title else "No title",
                                    "price": price,
                                    "description": text.strip()[:200] + "..." if len(text) > 200 else text.strip()
                                })
                        except:
                            continue
                    
                    if products:
                        break
                except:
                    continue
            
            extracted_data["products"] = products
        
        if data_type == "auto" or data_type == "tables":
            # Extract tabular data
            tables = []
            table_elements = await self.page.locator('table').all()
            
            for i, table in enumerate(table_elements[:5]):  # Limit to 5 tables
                try:
                    rows = await table.locator('tr').all()
                    table_data = []
                    
                    for row in rows[:20]:  # Limit to 20 rows
                        cells = await row.locator('td, th').all()
                        row_data = []
                        for cell in cells:
                            cell_text = await cell.text_content()
                            row_data.append(cell_text.strip() if cell_text else "")
                        if row_data:
                            table_data.append(row_data)
                    
                    if table_data:
                        tables.append({
                            "index": i,
                            "rows": len(table_data),
                            "columns": len(table_data[0]) if table_data else 0,
                            "data": table_data
                        })
                except:
                    continue
            
            extracted_data["tables"] = tables
        
        if data_type == "auto" or data_type == "contacts":
            # Extract contact information
            text_content = soup.get_text()
            
            # Email patterns
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text_content)
            
            # Phone patterns (various formats)
            phones = re.findall(r'(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}|\+?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4})', text_content)
            
            # Address patterns (basic)
            address_patterns = re.findall(r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)', text_content)
            
            extracted_data["contacts"] = {
                "emails": list(set(emails))[:10],
                "phones": list(set(phones))[:10],
                "addresses": list(set(address_patterns))[:5]
            }
        
        return extracted_data
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


async def execute_command(controller, command):
    """Execute a single command and return result"""
    command = command.strip()
    controller.logger.info(f"Executing command: {command}")
    
    try:
        if command == "capture" or command == "screenshot":
            state = await controller.capture_state()
            return {"status": "success", "message": f"State captured", **state}
        elif command.startswith("navigate "):
            url = command[9:]
            state = await controller.navigate(url)
            return {"status": "success", "message": f"Navigated to {url}", **state}
        elif command.startswith("click "):
            parts = command[6:].split()
            if len(parts) >= 2:
                x, y = int(parts[0]), int(parts[1])
                state = await controller.click(x, y)
                return {"status": "success", "message": f"Clicked at ({x}, {y})", **state}
            else:
                return {"status": "error", "message": "Click command needs x y coordinates"}
        elif command.startswith("type "):
            text = command[5:]
            state = await controller.type_text(text)
            return {"status": "success", "message": f"Typed: {text}", **state}
        elif command.startswith("key "):
            key = command[4:]
            state = await controller.press_key(key)
            return {"status": "success", "message": f"Pressed {key}", **state}
        elif command.startswith("scroll "):
            parts = command[7:].split()
            direction = parts[0] if parts else "down"
            amount = int(parts[1]) if len(parts) > 1 else 3
            state = await controller.scroll(direction, amount)
            return {"status": "success", "message": f"Scrolled {direction} by {amount}", **state}
        elif command.startswith("wait "):
            selector = command[5:]
            result = await controller.wait_for_element(selector)
            if "error" in result:
                return {"status": "error", "message": result["error"]}
            return {"status": "success", "message": f"Element found: {selector}", **result}
        elif command.startswith("find "):
            text = command[5:]
            result = await controller.find_elements_by_text(text)
            return {"status": "success", "message": f"Found {result['count']} elements", **result}
        elif command == "links":
            result = await controller.extract_links()
            return {"status": "success", "message": f"Extracted {result['count']} links", **result}
        elif command == "forms":
            result = await controller.extract_forms()
            return {"status": "success", "message": f"Found {result['count']} forms", **result}
        elif command == "structure":
            result = await controller.get_page_structure()
            return {"status": "success", "message": "Page structure analyzed", **result}
        elif command.startswith("extract "):
            data_type = command[8:] or "auto"
            result = await controller.smart_extract(data_type)
            product_count = len(result.get('products', []))
            table_count = len(result.get('tables', []))
            return {"status": "success", "message": f"Smart extraction complete - {product_count} products, {table_count} tables", **result}
        elif command == "quit":
            return {"status": "quit", "message": "Quitting browser"}
        else:
            return {"status": "error", "message": f"Unknown command: {command}"}
    except Exception as e:
        controller.logger.error(f"Error executing command '{command}': {str(e)}")
        return {"status": "error", "message": f"Error: {str(e)}"}


async def file_based_browser():
    """File-based browser control for Claude Code"""
    # Ensure tmp directory exists
    os.makedirs("./tmp", exist_ok=True)
    
    controller = BrowserController()
    commands_file = "./tmp/commands.txt"
    results_file = "./tmp/results.txt"
    
    controller.logger.info("=== STARTING FILE-BASED BROWSER CONTROL ===")
    controller.logger.info(f"Commands file: {commands_file}")
    controller.logger.info(f"Results file: {results_file}")
    
    print("Starting browser...")
    initial_state = await controller.start()
    
    # Write initial status
    initial_result = {
        "status": "ready", 
        "message": "Browser started successfully", 
        "timestamp": time.time(),
        **initial_state
    }
    
    with open(results_file, "w") as f:
        json.dump(initial_result, f, indent=2)
    
    controller.logger.info(f"Browser ready! Files: HTML={initial_state.get('html')}, Screenshot={initial_state.get('screenshot')}")
    print(f"Browser ready! Check {results_file} for status")
    print("\nWaiting for commands from Claude Code...")
    
    try:
        command_count = 0
        while True:
            # Check for commands file
            if os.path.exists(commands_file):
                controller.logger.info(f"Found commands file: {commands_file}")
                
                with open(commands_file, "r") as f:
                    commands = f.read().strip()
                
                if commands:
                    command_count += 1
                    controller.logger.info(f"=== COMMAND #{command_count}: {commands} ===")
                    print(f"Executing: {commands}")
                    
                    # Execute command
                    result = await execute_command(controller, commands)
                    result["timestamp"] = time.time()
                    result["command_number"] = command_count
                    
                    # Write result
                    with open(results_file, "w") as f:
                        json.dump(result, f, indent=2)
                    
                    controller.logger.info(f"Command completed: {result['message']}")
                    print(f"Result: {result['message']}")
                    
                    # Clear commands file
                    os.remove(commands_file)
                    controller.logger.info("Commands file cleared")
                    
                    # Check if quit command
                    if result.get("status") == "quit":
                        break
            
            # Poll every 200ms for faster response
            await asyncio.sleep(0.2)
                
    except Exception as e:
        controller.logger.error(f"Fatal error in file_based_browser: {str(e)}")
        print(f"Fatal error: {str(e)}")
    finally:
        controller.logger.info("=== SHUTTING DOWN BROWSER ===")
        await controller.close()
        print("Browser closed")


async def interactive_browser():
    """Interactive browser session for Claude Code"""
    controller = BrowserController()
    
    print("Starting browser...")
    screenshot_path = await controller.start()
    print(f"Initial screenshot saved: {screenshot_path}")
    
    print("\nBrowser is ready! Available commands:")
    print("- navigate <url>")
    print("- click <x> <y>") 
    print("- type <text>")
    print("- key <key_name>")
    print("- screenshot")
    print("- quit")
    
    try:
        while True:
            try:
                command = input("\nEnter command: ").strip()
            except EOFError:
                print("\nExiting...")
                break
            
            result = await execute_command(controller, command)
            print(result["message"])
            
            if result.get("status") == "quit":
                break
                
    finally:
        await controller.close()
        print("Browser closed")


def main():
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "interactive"
    
    if mode == "file":
        asyncio.run(file_based_browser())
    else:
        asyncio.run(interactive_browser())


if __name__ == "__main__":
    main()
