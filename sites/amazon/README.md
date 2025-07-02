# Amazon Order Scraping Process Summary

## Project Structure
```
amazon/
├── extract_order.py          # Main extraction script
├── append_orders.py           # CSV append utility
├── outputs/
│   ├── orders.json           # Raw extracted order data with metadata
│   └── amazon_orders_2024_formatted.csv  # Final formatted CSV output
└── README.md                 # This documentation
```

## Initial Setup
1. **Browser Automation Server Setup**
   - Added missing dependencies (FastAPI, uvicorn, pydantic) to `pyproject.toml`
   - Installed dependencies with `uv sync`
   - Started HTTP API server in background mode: `uv run python main.py http`
   - Server ran on `http://localhost:8000` with RESTful endpoints

2. **Fixed Extraction Script**
   - Original script was hardcoded to look for `page_003.html`
   - Created dynamic file detection to automatically find latest HTML capture
   - Script now uses modification time to identify most recent page data

## Data Extraction Process
**8 Pages Processed** (Pages 1-8, covering full 2024 order history)

### Page Navigation Pattern:
1. **Navigate to page URL** using HTTP POST to `/navigate` endpoint
   - Used background process with timeout due to navigation endpoint hanging
   - URLs: `startIndex=10,20,30,40,50,60,70` for pages 2-8

2. **Capture page state** using HTTP POST to `/capture` endpoint
   - Generated HTML file (`page_XXX.html`) and screenshot
   - HTML cleaned and optimized for token efficiency

3. **Extract orders** using `cd amazon && uv run python extract_order.py`
   - Analyzed HTML containers using BeautifulSoup
   - Extracted: Order ID, Date, Price, Products, Status
   - Applied deduplication and data validation

4. **Append to CSV** using `cd amazon && python append_orders.py`
   - Checked for existing orders to avoid duplicates
   - Formatted data consistently with existing CSV structure
   - Handled edge cases (missing products, malformed data)

## Results Summary
- **74 unique orders** extracted from 2024
- **Date range**: January 11, 2024 → December 3, 2024
- **Output format**: CSV with columns: No., Order#, Date, Price (JPY), Product Title
- **Data quality**: Cleaned, deduplicated, formatted consistently

## Technical Challenges Solved
1. **Navigation timeout issue**: Used background processes with `pkill` after 5 seconds
2. **Missing product data**: Added defensive programming with `.get()` methods
3. **Dynamic file detection**: Script automatically finds latest HTML capture
4. **Duplicate prevention**: CSV append logic checks existing Order IDs

## Automation Tools Used
- **Browser Control**: Playwright with Chrome integration
- **HTTP API**: FastAPI server for reliable command execution
- **Data Extraction**: BeautifulSoup for HTML parsing
- **File Management**: Automatic HTML/screenshot capture with timestamps

The process successfully automated the complete extraction of a full year's Amazon order history through intelligent web automation and robust data processing.

## Files Generated
- `outputs/orders.json` - Raw extracted order data with metadata
- `outputs/amazon_orders_2024_formatted.csv` - Final formatted CSV output
- `../tmp/page_*.html` - Captured HTML pages for each pagination step
- `../tmp/screenshot_*.png` - Visual snapshots of each page state

## Usage Instructions
1. **Start the browser automation server** (from project root):
   ```bash
   uv run python main.py http
   ```

2. **Navigate to Amazon orders page in browser** and capture the page

3. **Extract orders** (from amazon directory):
   ```bash
   cd amazon
   uv run python extract_order.py
   ```

4. **Append to CSV** (from amazon directory):
   ```bash
   python append_orders.py
   ```

5. **Repeat for additional pages** as needed

## Output Files
- `outputs/orders.json` - Contains raw extraction data with full metadata
- `outputs/amazon_orders_2024_formatted.csv` - Clean CSV format ready for analysis