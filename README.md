# 🚗 Claude Driver

**AI-driven browser automation for web data extraction**

## Usage

1. Run `claude code` in this folder
2. Ask Claude to start your extraction process
3. Claude handles everything automatically

All code in this project is maintained by Claude and optimized for AI automation.

## Project Structure

```
claude-driver/
├── CLAUDE.md                   # Claude's workflow guide (Claude reads this first)
├── core/
│   └── driver.py              # Browser automation engine
├── sites/
│   ├── amazon/extractor.py    # Amazon order extraction
│   └── templates/             # Templates for new sites  
├── tools/                     # Analysis tools (page analyzer, selector tester, etc.)
├── sessions/                  # Organized capture data
└── tmp/                      # Browser captures and screenshots
```

## How It Works

- **Claude reads CLAUDE.md** first to understand the mandatory workflow
- **Browser automation** via HTTP API for page capture and navigation
- **Intelligent extraction** using site-specific patterns and validation
- **Self-documenting tools** that guide Claude through each step

Perfect for extracting e-commerce orders, product catalogs, or any structured web data.
