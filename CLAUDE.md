# 🚗 CLAUDE.md - Claude Driver Usage Guide

**CLAUDE: This is your mandatory workflow guide. Read this FIRST in every session!**

## 🎯 What is Claude Driver?

Claude Driver is a browser automation toolkit designed for **AI-human collaboration**. You (Claude) drive the browser while the human provides guidance and validation. The tool is optimized for **your workflow** and helps you extract data from websites efficiently.

## 🚨 MANDATORY WORKFLOW - NEVER SKIP THESE STEPS

### 1. **Start the Driver** (Human usually does this)
```bash
source .venv/bin/activate  # Activate virtual environment
# Start HTTP API server
python core/driver.py http
```

### 2. **Navigate to Target Page** (You help guide this)
```bash
# Check status and get guidance
curl http://localhost:8000/status

# Navigate to target URL
curl -X POST http://localhost:8000/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://target-site.com/page"}'
```

### 3. **ALWAYS Capture Before Extraction**
```bash
# Capture current page state
curl -X POST http://localhost:8000/capture
```
**This returns HTML file path, analysis file, and workflow guidance!**

### 4. **ALWAYS Analyze Page Structure First**
```bash
# Read the captured HTML
# Use Read tool on the HTML file returned from capture

# Run page analyzer
python tools/page_analyzer.py path/to/captured.html
```

### 5. **Plan Your Extraction**
- Identify target data fields
- Find container selectors
- Estimate expected item count
- Plan validation criteria

### 6. **Build/Run Extractor**
```bash
# Use existing site extractor
cd sites/amazon && python extractor.py

# Or create new site extractor
cp sites/templates/basic_extractor.py sites/newsite/extractor.py
# Then customize it
```

### 7. **ALWAYS Test on Small Samples First**
- Extract 2-3 items first
- Validate field quality
- Check for missing data
- Iterate and improve

### 8. **Scale Up & Validate**
- Process all pages/items
- Validate final results
- Save intermediate checkpoints

## 🛠️ Available Tools for Claude

### **Analysis Tools** (Use these frequently!)
- **`tools/page_analyzer.py`** - Understand page structure
- **`tools/selector_tester.py`** - Test CSS selectors quickly
- **`tools/extraction_validator.py`** - Validate extraction results

### **Site Extractors**
- **`sites/amazon/extractor.py`** - Amazon-specific extraction
- **`sites/templates/basic_extractor.py`** - Template for new sites

### **Session Management**
- **`sessions/`** - Organized capture data by date/site
- **`tools/session_manager.py`** - Session utilities

## 📁 Project Structure You Should Know

```
claude-driver/
├── core/driver.py              # Main browser automation
├── sites/
│   ├── amazon/extractor.py     # Amazon extraction logic
│   ├── templates/              # Templates for new sites
│   └── newsite/                # Your new extractors go here
├── sessions/                   # Captured data organized by date/site
├── tools/                      # Analysis tools for you
└── CLAUDE.md                   # This file - READ IT FIRST!
```

## 🎯 Common Workflows

### **Extracting E-commerce Orders**
1. Navigate to orders page
2. Capture current page
3. Analyze page structure
4. Identify order containers
5. Extract: order_id, date, price, products
6. Handle pagination if needed
7. Validate and save results

### **Extracting Product Listings**
1. Navigate to category/search page
2. Capture and analyze
3. Find product containers
4. Extract: title, price, rating, url
5. Handle infinite scroll/pagination
6. Validate and deduplicate

### **Adding a New Site**
1. Copy `sites/templates/basic_extractor.py`
2. Create `sites/SITENAME/` directory
3. Customize extraction logic
4. Test on captured pages
5. Document successful patterns

## ⚠️ COMMON MISTAKES TO AVOID

❌ **Don't skip page analysis** - Always run `page_analyzer.py` first  
❌ **Don't extract everything at once** - Test small samples first  
❌ **Don't ignore validation** - Always check data quality  
❌ **Don't lose progress** - Save intermediate results frequently  
❌ **Don't hardcode selectors** - Make them adaptable  

## 🔍 Debugging When Things Go Wrong

### **Extraction Returns Empty Results**
1. Check if page loaded correctly (screenshot)
2. Verify selectors with `selector_tester.py`
3. Look for dynamic content loading
4. Check for anti-bot measures

### **Missing Data Fields**
1. Inspect HTML structure manually
2. Look for alternative selectors
3. Check if data is in JSON-LD or data attributes
4. Consider regex fallback patterns

### **Rate Limiting/Blocking**
1. Add delays between requests
2. Check for CAPTCHA requirements
3. Verify user agent settings
4. Consider session/cookie management

## 💡 Best Practices for Claude

### **Be Methodical**
- Always follow the workflow steps
- Document what works
- Save progress frequently
- Test incrementally

### **Be Adaptive**
- Try multiple selector strategies
- Have fallback approaches
- Handle edge cases gracefully
- Learn from failures

### **Communicate Clearly**
- Describe what you're doing
- Explain any issues found
- Show sample extracted data
- Ask for guidance when stuck

## 🚀 Quick Reference Commands

```bash
# Essential workflow commands
python core/driver.py http                    # Start driver
curl -X POST http://localhost:8000/capture   # Capture page
python tools/page_analyzer.py latest.html    # Analyze structure
python sites/amazon/extractor.py             # Run extraction
python tools/extraction_validator.py         # Validate results

# Check project status
curl http://localhost:8000/status            # Driver status
ls sessions/                                 # Recent sessions
ls sites/                                    # Available extractors
```

## 📝 Session Documentation

**CLAUDE: Always document your progress!**

Create session notes like:
```markdown
## Session: 2024-07-03 Amazon Orders
**Goal**: Extract 2024 order history  
**Pages**: 8 pages, ~10 orders each  
**Status**: Completed successfully  

### What Worked
- Container: `.a-box-group.order`
- Order ID: `[data-order-id]`
- Date: `.order-date-invoice-item`

### Issues Encountered
- Some orders missing price (¥0 items)
- Pagination timeout workaround needed

### Final Results
- 74 orders extracted
- Saved to: sites/amazon/outputs/orders_2024.csv
```

---

**🎯 Remember Claude: Follow this workflow every time for successful extraction!**
