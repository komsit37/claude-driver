# Browser Interactive Control with Claude Code

A Python-based browser automation system that allows Claude Code to see, analyze, and control web pages interactively through both file-based commands and HTTP API, with comprehensive HTML/screenshot analysis.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
uv sync
uv run playwright install
```

### 2. Choose Your Mode

#### File Mode (Traditional)
```bash
uv run python main.py file
```
Claude Code sends commands through `./tmp/commands.txt` and views results in `./tmp/results.txt`.

#### HTTP API Mode (Recommended)
```bash
uv run python main.py http
```
Interact via HTTP endpoints at `http://localhost:8000` with auto-generated docs at `/docs`.

### 3. Start Controlling
Choose file mode for simple automation or HTTP API mode for clearer responses and better error handling.

## 🔄 How Interactive Control Works

### File Mode Architecture
```
Claude Code   writes  > ./tmp/commands.txt
     |                         |
reads results            Browser executes  
     |                         |
./tmp/results.txt <  updates   Browser Script
./tmp/page_XXX.html <  saves   HTML Content
./tmp/screenshot_XXX.png <     Screenshots
```

### HTTP API Mode Architecture
```
Claude Code   HTTP POST > http://localhost:8000/navigate
     |                         |
JSON response           Browser executes  
     |                         |
Structured data   <     HTTP Response
./tmp/page_XXX.html <  saves   HTML Content
./tmp/screenshot_XXX.png <     Screenshots
```

## 📡 HTTP API Mode

### Starting the Server
```bash
uv run python main.py http
```
Server runs on `http://localhost:8000` with interactive docs at `/docs`.

### API Endpoints

#### Navigation & Interaction
- **POST /navigate** - Navigate to URL
  ```bash
  curl -X POST http://localhost:8000/navigate \
    -H "Content-Type: application/json" \
    -d '{"url": "https://amazon.co.jp"}'
  ```

- **POST /click** - Click at coordinates
  ```bash
  curl -X POST http://localhost:8000/click \
    -H "Content-Type: application/json" \
    -d '{"x": 100, "y": 200}'
  ```

- **POST /type** - Type text
  ```bash
  curl -X POST http://localhost:8000/type \
    -H "Content-Type: application/json" \
    -d '{"text": "hello world"}'
  ```

- **POST /key** - Press keys
  ```bash
  curl -X POST http://localhost:8000/key \
    -H "Content-Type: application/json" \
    -d '{"key": "Enter"}'
  ```

- **POST /scroll** - Scroll page
  ```bash
  curl -X POST http://localhost:8000/scroll \
    -H "Content-Type: application/json" \
    -d '{"direction": "down", "amount": 5}'
  ```

#### Page Analysis
- **POST /capture** - Take screenshot and save HTML
  ```bash
  curl -X POST http://localhost:8000/capture
  ```

- **POST /wait** - Wait for element
  ```bash
  curl -X POST http://localhost:8000/wait \
    -H "Content-Type: application/json" \
    -d '{"selector": ".product-list", "timeout": 10000}'
  ```

- **POST /find** - Find elements by text
  ```bash
  curl -X POST http://localhost:8000/find \
    -H "Content-Type: application/json" \
    -d '{"text": "Add to Cart"}'
  ```

- **POST /extract** - Smart data extraction
  ```bash
  curl -X POST http://localhost:8000/extract \
    -H "Content-Type: application/json" \
    -d '{"data_type": "products"}'
  ```

#### Information Endpoints
- **GET /links** - Extract all links
- **GET /forms** - Extract all forms
- **GET /structure** - Get page structure

#### Command Interface
- **POST /command** - Execute file-mode commands via API
  ```bash
  curl -X POST http://localhost:8000/command \
    -H "Content-Type: application/json" \
    -d '{"command": "navigate https://example.com"}'
  ```

### HTTP API Benefits
- **Structured Responses**: JSON responses with clear success/error states
- **Better Error Handling**: Detailed error messages and HTTP status codes
- **Interactive Documentation**: Auto-generated API docs at `/docs`
- **Real-time Results**: Immediate JSON responses without file polling
- **Type Safety**: Request/response validation with Pydantic models

### Available Commands (File Mode)

#### Basic Navigation
- `navigate <url>` - Navigate to a website
- `click <x> <y>` - Click at specific coordinates  
- `type <text>` - Type text at current focus
- `key <key_name>` - Press keys (Enter, Tab, Escape, etc.)
- `capture` - Take fresh screenshot and save HTML
- `scroll <direction> <amount>` - Scroll page (up/down/left/right)

#### Advanced Scraping
- `wait <selector>` - Wait for element to appear (CSS selector)
- `find <text>` - Find elements containing specific text with coordinates
- `links` - Extract all links from current page
- `forms` - Extract all forms and their input fields
- `structure` - Get semantic page structure (headings, nav, content)
- `extract <type>` - Smart extraction (auto/products/tables/contacts)

#### Control
- `quit` - Exit browser

### Example Workflows

#### Basic Navigation (File Mode)
```bash
# Navigate to a page
echo "navigate https://amazon.co.jp" > ./tmp/commands.txt

# Wait for specific element to load
echo "wait .product-list" > ./tmp/commands.txt

# Scroll to load more content
echo "scroll down 5" > ./tmp/commands.txt
```

#### Basic Navigation (HTTP API)
```bash
# Navigate to a page
curl -X POST http://localhost:8000/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://amazon.co.jp"}'

# Wait for specific element to load
curl -X POST http://localhost:8000/wait \
  -H "Content-Type: application/json" \
  -d '{"selector": ".product-list", "timeout": 10000}'

# Scroll to load more content
curl -X POST http://localhost:8000/scroll \
  -H "Content-Type: application/json" \
  -d '{"direction": "down", "amount": 5}'
```

#### Smart Data Extraction (File Mode)
```bash
# Extract all links on page
echo "links" > ./tmp/commands.txt

# Find elements containing specific text
echo "find Add to Cart" > ./tmp/commands.txt

# Smart extraction of products/tables/contacts
echo "extract products" > ./tmp/commands.txt
echo "extract tables" > ./tmp/commands.txt
echo "extract contacts" > ./tmp/commands.txt

# Get page structure overview
echo "structure" > ./tmp/commands.txt
```

#### Smart Data Extraction (HTTP API)
```bash
# Extract all links on page
curl http://localhost:8000/links

# Find elements containing specific text
curl -X POST http://localhost:8000/find \
  -H "Content-Type: application/json" \
  -d '{"text": "Add to Cart"}'

# Smart extraction of products/tables/contacts
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"data_type": "products"}'

curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"data_type": "tables"}'

# Get page structure overview
curl http://localhost:8000/structure
```

#### Results Format
```json
{
  "status": "success",
  "message": "Smart extraction complete - 15 products, 2 tables",
  "products": [
    {
      "title": "MacBook Air M2",
      "price": "¥110,589",
      "description": "Apple MacBook Air with M2 chip..."
    }
  ],
  "tables": [
    {
      "index": 0,
      "rows": 5,
      "columns": 3,
      "data": [["Header1", "Header2", "Header3"], ["Row1Col1", "Row1Col2", "Row1Col3"]]
    }
  ]
}
```

## 🎯 What Claude Code Can Do

### Web Analysis Tasks
- **Page Content Analysis**: Read and understand webpage structure, text, and layout
- **Smart Data Extraction**: Auto-detect and extract products, tables, contact info
- **Element Location**: Find clickable elements by text content with coordinates
- **Form Analysis**: Extract all forms with field types, names, and requirements
- **Link Discovery**: Extract all links with full URLs and categorization
- **Structure Mapping**: Get semantic page layout (headings, nav, main content)
- **Wait Conditions**: Smart waiting for dynamic content to load
- **Visual Inspection**: Analyze page layouts, UI elements, and visual state

### E-commerce Automation
- **Order Management**: Navigate order history, extract purchase details with smart parsing
- **Product Discovery**: Auto-extract product titles, prices, descriptions from listings
- **Comparison Shopping**: Extract product data from multiple pages for analysis
- **Cart Operations**: Find and interact with cart buttons using text search
- **Form Automation**: Auto-detect checkout forms and required fields
- **Account Management**: Navigate account pages using semantic structure analysis

### Content Interaction
- **Social Media**: Post content, interact with feeds, manage profiles
- **Documentation**: Navigate wikis, help systems, technical documentation
- **Search & Research**: Perform complex searches across multiple sites
- **File Operations**: Upload/download files, manage cloud storage

### Testing & Monitoring
- **UI Testing**: Verify page functionality, layout, and behavior
- **Accessibility Checks**: Analyze page accessibility and usability
- **Performance Monitoring**: Check page load times and responsiveness
- **Cross-page Workflows**: Test complete user journeys

## 📁 Project Structure

```
browser-script/
 main.py                 # Main browser control script
 amazon/
    extract_order.py    # Amazon order extraction example
    orders.json         # Extracted order data
 tmp/                    # Communication files
    commands.txt        # Commands from Claude Code
    results.txt         # Execution results
    page_XXX.html       # Saved HTML content
    screenshot_XXX.png  # Page screenshots
    browser.log         # Detailed execution logs
 README.md              # This file
```

## ⚙️ Technical Features

### Smart State Capture
- **Dual Format**: Both HTML and screenshots for comprehensive analysis
- **Intelligent Extraction**: Auto-detect products, tables, forms, links, contacts
- **Element Location**: Find elements by text with precise click coordinates
- **Semantic Analysis**: Extract page structure (headings, navigation, content areas)
- **Wait Conditions**: Smart waiting for dynamic content and AJAX loads
- **Automatic Resizing**: Screenshots optimized for Claude Code analysis
- **Metadata Rich**: URLs, titles, timestamps for complete context

### Robust Command Processing
- **Dual Interface**: File-based communication OR HTTP API for flexibility
- **Error Handling**: Comprehensive logging and graceful failure recovery
- **Real-time Feedback**: Immediate results after each command
- **API Documentation**: Auto-generated OpenAPI docs at `/docs` for HTTP mode
- **Structured Responses**: JSON responses with consistent error/success format

### Browser Integration
- **Chrome Support**: Uses your installed Chrome browser
- **Full Automation**: Complete Playwright integration for advanced interactions
- **Network Control**: Handle complex web apps, SPAs, and dynamic content

## 📋 Example Use Cases

### 1. E-commerce Order Analysis
```python
# Extract all Amazon orders with full product details
uv run python amazon/extract_order.py

# Results: Clean JSON with 10 unique orders, ¥179,151 total value
# Handles: Deduplication, product extraction, price analysis
```

### 2. Multi-step Authentication (File Mode)
```bash
# Claude Code can handle complex login flows:
# 1. Navigate to login page
# 2. Fill username/password
# 3. Handle 2FA prompts
# 4. Navigate to protected content
# 5. Extract authenticated data
```

#### Multi-step Authentication (HTTP API)
```bash
# 1. Navigate to login page
curl -X POST http://localhost:8000/navigate \
  -d '{"url": "https://example.com/login"}'

# 2. Fill username field
curl -X POST http://localhost:8000/click -d '{"x": 200, "y": 100}'
curl -X POST http://localhost:8000/type -d '{"text": "username"}'

# 3. Fill password and submit
curl -X POST http://localhost:8000/key -d '{"key": "Tab"}'
curl -X POST http://localhost:8000/type -d '{"text": "password"}'
curl -X POST http://localhost:8000/key -d '{"key": "Enter"}'

# 4. Wait for protected content
curl -X POST http://localhost:8000/wait \
  -d '{"selector": ".dashboard", "timeout": 5000}'

# 5. Extract authenticated data
curl -X POST http://localhost:8000/extract -d '{"data_type": "auto"}'
```

### 3. Dynamic Content Monitoring (File Mode)
```bash
# Monitor pages for changes:
# 1. Take baseline screenshot
# 2. Refresh page periodically  
# 3. Compare visual/content changes
# 4. Alert on significant updates
```

#### Dynamic Content Monitoring (HTTP API)
```bash
# 1. Take baseline screenshot
curl -X POST http://localhost:8000/capture

# 2. Refresh and capture periodically
curl -X POST http://localhost:8000/key -d '{"key": "F5"}'
curl -X POST http://localhost:8000/wait -d '{"selector": "body", "timeout": 5000}'
curl -X POST http://localhost:8000/capture

# 3. Extract current data for comparison
curl -X POST http://localhost:8000/extract -d '{"data_type": "auto"}'
```

## =' Configuration

### Browser Settings
- **Headless Mode**: `headless=False` for visual debugging
- **Chrome Channel**: Uses system Chrome installation
- **Network Waiting**: `wait_until='networkidle'` for SPA compatibility

### File Locations
- **Commands**: `./tmp/commands.txt` - Claude Code writes here (File Mode)
- **Results**: `./tmp/results.txt` - Browser updates here (File Mode)
- **HTML**: `./tmp/page_XXX.html` - Full page content (Both modes)
- **Screenshots**: `./tmp/screenshot_XXX.png` - Visual state (Both modes)
- **Logs**: `./tmp/browser.log` - Detailed execution logs (Both modes)

### HTTP API Configuration
- **Server**: `http://localhost:8000` - Main API endpoint
- **Documentation**: `http://localhost:8000/docs` - Interactive API docs
- **Health Check**: `http://localhost:8000/health` - Server status
- **Content Types**: JSON requests/responses with automatic validation

## ⚠️ Important Notes

### Security & Ethics
- **Defensive Use Only**: Designed for legitimate automation and analysis
- **Respect Terms of Service**: Always follow website ToS and robots.txt
- **Rate Limiting**: Built-in delays to avoid overwhelming servers
- **Data Privacy**: All data stays local, no external transmission

### Limitations
- **Single Browser Instance**: One browser window at a time
- **Coordinate-based Clicking**: Requires valid screen coordinates
- **File Polling**: 200ms polling interval for command detection
- **Chrome Dependency**: Requires Chrome browser installation

## 🛠 Development

### Adding New Commands
1. Add command pattern in `execute_command()` function
2. Implement command handler in `BrowserController` class
3. Update command documentation in this README

### Extending Data Extraction
1. Create new extraction scripts in dedicated folders
2. Use BeautifulSoup for HTML parsing
3. Follow deduplication patterns from `amazon/extract_order.py`

### Integration Tips
- **Always capture state** after each action for Claude Code analysis
- **Use descriptive logging** for debugging complex workflows  
- **Handle errors gracefully** to maintain browser session
- **Test with actual websites** to ensure real-world compatibility

---

**<� Perfect for**: Web scraping, UI testing, e-commerce automation, research tasks, and any scenario where Claude Code needs to see and interact with web content intelligently.

## 🔍 Advanced Scraping Features

### Smart Data Detection
- **Auto Product Recognition**: Detects product listings, prices, titles, descriptions
- **Table Extraction**: Finds and structures tabular data automatically  
- **Contact Mining**: Extracts emails, phone numbers, addresses from any page
- **Form Analysis**: Complete form mapping with field types and validation rules

### Element Intelligence
- **Text-based Finding**: Locate any element by its visible text content
- **Coordinate Precision**: Get exact click coordinates for found elements
- **Dynamic Waiting**: Wait for specific elements to appear before proceeding
- **Semantic Structure**: Understand page hierarchy and content organization

### Content Processing
- **Link Harvesting**: Extract all links with domain categorization
- **Content Filtering**: Smart filtering to avoid navigation noise
- **Multi-format Support**: Handle products, tables, forms, contacts automatically
- **Scalable Limits**: Configurable limits to prevent data overload

### Performance Optimizations
- **Selective Extraction**: Choose specific data types (products/tables/contacts)
- **Batch Processing**: Process multiple elements efficiently
- **Smart Timeouts**: Configurable wait times for different scenarios
- **Memory Efficient**: Limits and filtering to handle large pages

### Advanced Scraping Commands (File Mode)
```bash
# Scroll to load infinite scroll content
echo "scroll down 10" > ./tmp/commands.txt

# Wait for AJAX content to load
echo "wait [data-testid='product-grid']" > ./tmp/commands.txt

# Find buttons by text and get coordinates
echo "find Add to Cart" > ./tmp/commands.txt

# Extract structured data automatically
echo "extract auto" > ./tmp/commands.txt       # Auto-detect all types
echo "extract products" > ./tmp/commands.txt   # Focus on products
echo "extract tables" > ./tmp/commands.txt     # Focus on tables
echo "extract contacts" > ./tmp/commands.txt   # Focus on contact info

# Get complete page structure
echo "structure" > ./tmp/commands.txt

# Extract all navigation links
echo "links" > ./tmp/commands.txt

# Analyze all forms on page
echo "forms" > ./tmp/commands.txt
```

### Advanced Scraping Commands (HTTP API)
```bash
# Scroll to load infinite scroll content
curl -X POST http://localhost:8000/scroll \
  -H "Content-Type: application/json" \
  -d '{"direction": "down", "amount": 10}'

# Wait for AJAX content to load
curl -X POST http://localhost:8000/wait \
  -H "Content-Type: application/json" \
  -d '{"selector": "[data-testid=\"product-grid\"]", "timeout": 10000}'

# Find buttons by text and get coordinates
curl -X POST http://localhost:8000/find \
  -H "Content-Type: application/json" \
  -d '{"text": "Add to Cart"}'

# Extract structured data automatically
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"data_type": "auto"}'        # Auto-detect all types

curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"data_type": "products"}'    # Focus on products

curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"data_type": "tables"}'      # Focus on tables

# Get complete page structure
curl http://localhost:8000/structure

# Extract all navigation links
curl http://localhost:8000/links

# Analyze all forms on page
curl http://localhost:8000/forms
```

---

**🎯 Enhanced for**: Advanced web scraping, automated data extraction, e-commerce intelligence, competitive analysis, content research, and sophisticated web content understanding.
