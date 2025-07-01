# CLAUDE.md - Browser Interactive Control System

This repository contains a Python-based browser automation system that allows Claude Code to interactively control web browsers through both HTTP API and file-based communication. The system captures both HTML content and screenshots for comprehensive web analysis and automation.

## 🚀 Quick Start Commands

### Setup & Dependencies
```bash
# Install dependencies
uv sync
uv run playwright install

# Start browser in HTTP API mode (recommended - better error handling)
uv run python main.py http

# Start browser in file-based control mode (legacy)
uv run python main.py file

# Start browser in interactive mode (for manual testing)
uv run python main.py
```

### Common Development Commands
```bash
# Run Amazon order extraction example
uv run python amazon/extract_order.py

# Check project structure
ls -la

# View logs
tail -f ./tmp/browser.log

# Clean temporary files
rm -rf ./tmp/*
```

## 🏗️ High-Level Architecture

### Core Components

1. **main.py** - Primary browser automation engine
   - `BrowserController` class: Main automation controller with Playwright integration
   - Dual-mode operation: Interactive CLI and file-based communication
   - Smart state capture: HTML + optimized screenshots for Claude Code analysis
   - Comprehensive command processing with 15+ automation commands

2. **Dual Communication Interfaces**
   - **HTTP API Mode** (Recommended): RESTful endpoints with structured responses
     - `POST http://localhost:8000/navigate` - Navigation commands
     - `POST http://localhost:8000/click` - Interaction commands  
     - `GET http://localhost:8000/status` - Server status and current page info
     - Auto-generated docs at `http://localhost:8000/docs`
   - **File-Based Mode** (Legacy): File polling system
     - `./tmp/commands.txt` - Claude Code writes commands here
     - `./tmp/results.txt` - Browser execution results in JSON format
   - **Shared State Files**: Available in both modes
     - `./tmp/page_XXX.html` - Complete HTML content capture (cleaned for token efficiency)
     - `./tmp/screenshot_XXX.png` - Visual page state (auto-resized to 800px width)
     - `./tmp/browser.log` - Detailed execution and debugging logs

3. **Amazon Integration Example** (`amazon/` folder)
   - `extract_order.py` - Advanced order data extraction with deduplication
   - `orders.json` - Clean extracted order data (10 unique orders, ¥179,151 total)
   - Demonstrates real-world e-commerce automation patterns

### Key Technical Features

- **Chrome Integration**: Uses system Chrome browser via Playwright
- **Smart Element Detection**: Multiple strategies for finding clickable elements
- **Advanced Data Extraction**: Auto-detection of products, tables, forms, contacts
- **Robust Error Handling**: Comprehensive logging and graceful failure recovery
- **Coordinate-Precise Clicking**: Text-based element finding with exact coordinates
- **Dynamic Content Support**: Smart waiting for AJAX and SPA content loads

## 🎯 Common Use Cases & Commands

### HTTP API Commands (Recommended)

#### Web Navigation & Analysis
```bash
# Navigate to website
curl -X POST http://localhost:8000/navigate -H "Content-Type: application/json" -d '{"url": "https://example.com"}'

# Capture current page state
curl -X POST http://localhost:8000/capture

# Scroll to load more content
curl -X POST http://localhost:8000/scroll -H "Content-Type: application/json" -d '{"direction": "down", "amount": 5}'

# Wait for dynamic content
curl -X POST http://localhost:8000/wait -H "Content-Type: application/json" -d '{"selector": ".product-list", "timeout": 10000}'

# Check server status and current page
curl http://localhost:8000/status
```

#### Smart Data Extraction
```bash
# Auto-detect and extract all data types
curl -X POST http://localhost:8000/extract -H "Content-Type: application/json" -d '{"data_type": "auto"}'

# Focus on specific data types
curl -X POST http://localhost:8000/extract -H "Content-Type: application/json" -d '{"data_type": "products"}'
curl -X POST http://localhost:8000/extract -H "Content-Type: application/json" -d '{"data_type": "tables"}'
curl -X POST http://localhost:8000/extract -H "Content-Type: application/json" -d '{"data_type": "contacts"}'

# Get page structure overview
curl http://localhost:8000/structure

# Extract all links
curl http://localhost:8000/links

# Find elements by text content
curl -X POST http://localhost:8000/find -H "Content-Type: application/json" -d '{"text": "Add to Cart"}'
```

#### Interactive Control
```bash
# Click at specific coordinates
curl -X POST http://localhost:8000/click -H "Content-Type: application/json" -d '{"x": 400, "y": 300}'

# Type text in focused field
curl -X POST http://localhost:8000/type -H "Content-Type: application/json" -d '{"text": "Hello World"}'

# Press keyboard keys
curl -X POST http://localhost:8000/key -H "Content-Type: application/json" -d '{"key": "Enter"}'
curl -X POST http://localhost:8000/key -H "Content-Type: application/json" -d '{"key": "Tab"}'
```

### File-Based Commands (Legacy)

#### Web Navigation & Analysis
```bash
# Navigate to website
echo "navigate https://example.com" > ./tmp/commands.txt

# Capture current page state
echo "capture" > ./tmp/commands.txt

# Scroll to load more content
echo "scroll down 5" > ./tmp/commands.txt

# Wait for dynamic content
echo "wait .product-list" > ./tmp/commands.txt
```

### Smart Data Extraction
```bash
# Auto-detect and extract all data types
echo "extract auto" > ./tmp/commands.txt

# Focus on specific data types
echo "extract products" > ./tmp/commands.txt
echo "extract tables" > ./tmp/commands.txt
echo "extract contacts" > ./tmp/commands.txt

# Get page structure overview
echo "structure" > ./tmp/commands.txt

# Extract all links
echo "links" > ./tmp/commands.txt

# Find elements by text content
echo "find Add to Cart" > ./tmp/commands.txt
```

### Interactive Control
```bash
# Click at specific coordinates
echo "click 400 300" > ./tmp/commands.txt

# Type text in focused field
echo "type Hello World" > ./tmp/commands.txt

# Press keyboard keys
echo "key Enter" > ./tmp/commands.txt
echo "key Tab" > ./tmp/commands.txt
```

## 📁 Project Structure Understanding

```
browser-script/
├── main.py                 # Core automation engine (630 lines)
├── amazon/
│   ├── extract_order.py    # Advanced extraction example (300 lines)
│   └── orders.json         # Clean extracted data
├── tmp/                    # Communication & state files
│   ├── commands.txt        # Command input from Claude Code
│   ├── results.txt         # JSON execution results
│   ├── page_XXX.html       # HTML content snapshots
│   ├── screenshot_XXX.png  # Visual page states
│   └── browser.log         # Detailed execution logs
├── pyproject.toml          # Dependencies & project config
└── README.md               # Comprehensive documentation
```

## 🔧 Development Patterns

### Adding New Commands
1. Add command pattern in `execute_command()` function (main.py:436-502)
2. Implement handler method in `BrowserController` class
3. Update README.md documentation
4. Test with both file and interactive modes

### Data Extraction Best Practices
- Use BeautifulSoup for HTML parsing and data structuring
- Implement deduplication logic (see amazon/extract_order.py:184-217)
- Filter unrealistic data (price ranges, content length validation)
- Score containers to identify relevant content (main.py:78-87)
- Limit results to prevent data overload (products[:20], links[:50])

### Error Handling Approach
- Comprehensive logging to ./tmp/browser.log
- Graceful degradation on element not found
- JSON error responses with actionable messages
- Browser session preservation on command failures

## 🎨 Claude Code Integration Tips

### Sub-Agent Capabilities
Claude Code can spawn sub-agents for specialized tasks:
- **Claude sub-agents**: Use for general automation, web interaction, and data extraction tasks
- **Gemini sub-agents**: Use for long context tasks like analyzing or summarizing large HTML files, processing extensive extracted data, or reviewing large log files
- **Task delegation**: `Task` tool allows spawning concurrent agents for complex multi-step workflows

### Effective Workflow

#### HTTP API Mode (Recommended)
1. **Check server status**: `curl http://localhost:8000/status`
2. **Always capture state** after navigation: `curl -X POST http://localhost:8000/capture`
3. **Use smart extraction** for unknown pages: `curl -X POST http://localhost:8000/extract -d '{"data_type": "auto"}'`
4. **Find elements by text** for reliable clicking: `curl -X POST http://localhost:8000/find -d '{"text": "Login"}'`
5. **Wait for dynamic content** before proceeding: `curl -X POST http://localhost:8000/wait -d '{"selector": "[data-loaded=true]"}'`
6. **Delegate analysis tasks**: Use Gemini sub-agents for processing large HTML files or summarizing extraction results

#### File-Based Mode (Legacy)
1. **Always capture state** after navigation: `echo "capture" > ./tmp/commands.txt`
2. **Use smart extraction** for unknown pages: `echo "extract auto" > ./tmp/commands.txt`
3. **Find elements by text** for reliable clicking: `echo "find Login" > ./tmp/commands.txt`
4. **Wait for dynamic content** before proceeding: `echo "wait [data-loaded='true']" > ./tmp/commands.txt`

### Reading Results
- **HTTP API**: Direct JSON responses with structured data and error handling
- **File Mode**: Check `./tmp/results.txt` for JSON-formatted command results
- Screenshots auto-resized to 800px width for optimal Claude Code analysis
- HTML files contain cleaned page source for efficient token usage
- Logs provide detailed execution context for debugging

### Advanced Automation Patterns
- **Multi-step workflows**: Chain commands with state capture between steps
- **Form automation**: Use `echo "forms" > ./tmp/commands.txt` to analyze form fields
- **Content monitoring**: Regular capture + comparison for change detection
- **E-commerce automation**: Product extraction + cart operations + checkout flows

## 🔍 Dependencies & Requirements

### Core Dependencies (pyproject.toml)
- `playwright>=1.40.0` - Browser automation engine
- `fastapi>=0.104.0` - HTTP API framework for RESTful endpoints
- `uvicorn>=0.24.0` - ASGI server for HTTP API mode
- `pydantic>=2.5.0` - Data validation and serialization
- `pillow>=10.0.0` - Image processing for screenshot optimization
- `pyautogui>=0.9.54` - Additional GUI automation capabilities
- `beautifulsoup4>=4.12.0` - HTML parsing and data extraction

### System Requirements
- Python 3.12+
- Chrome browser installed
- uv package manager (recommended) or pip

## 🛡️ Security & Ethics

- **Defensive automation only** - No malicious or unauthorized access patterns
- **Rate limiting built-in** - Delays and timeouts to respect server resources
- **Local data storage** - All captures and extractions stay on local machine
- **Respect robots.txt** - User responsibility to follow website terms of service

## 💡 Troubleshooting & Debugging

### Common Issues
- **Connection refused**: Ensure HTTP API server is running (`python main.py http`)
- **EOF errors in interactive mode**: Use HTTP API mode instead (`python main.py http`)
- **Port already in use**: Kill existing server or change port in main.py
- **Blank screenshots**: Check Chrome browser installation and permissions
- **Element not found**: Use `find` command to locate elements by text first
- **AJAX content missing**: Use `wait` command with appropriate selector
- **HTTP 503 errors**: Browser not initialized - restart server

### Debug Resources
- `./tmp/browser.log` - Detailed execution logs with timestamps
- `./tmp/page_XXX.html` - Complete HTML source for inspection
- Screenshot sequence for visual debugging workflow
- JSON results with error messages and status codes

---

**🎯 Perfect for**: Web scraping, UI testing, e-commerce automation, research workflows, and any scenario requiring intelligent browser interaction with visual feedback.