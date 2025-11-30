# File Scanner MCP Server

A simple Model Context Protocol (MCP) server for scanning and retrieving files with privacy-aware filtering.

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Install dependencies
pip3.11 install "git+https://github.com/modelcontextprotocol/python-sdk.git" pydantic

# Verify installation
python -m py_compile file_scanner_mcp.py
```

### Running the Server

**Option 1: With MCP Inspector (Recommended for testing)**
```bash
npx @modelcontextprotocol/inspector python3 file_scanner_mcp.py
```

**Option 2: Standalone (stdio transport)**
```bash
python file_scanner_mcp.py
```

**Option 3: With Claude Desktop**
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "file-scanner": {
      "command": "python3.11",
      "args": ["/Users/tanmaypatil/file_scanner_mcp/file_scanner_mcp.py"]
    }
  }
}
```

## What It Does

This MCP server provides three tools:

1. **search_files** - Search for files by filename or content with privacy filtering
2. **get_file_content** - Retrieve complete file content with optional metadata
3. **list_files** - List all files with filtering by pattern or privacy level

### Privacy Levels

Files are automatically classified:
- **PUBLIC** - No sensitive markers (default)
- **SENSITIVE** - Contains `[SENSITIVE]`, `internal only`, or `employee id:`
- **CONFIDENTIAL** - Contains `[CONFIDENTIAL]`, `SSN:`, `password:`, or `credit card:`

## Sample Documents

5 test documents are included in `test_documents/`:
- ✅ `team_meeting_notes.txt` (PUBLIC)
- ✅ `api_documentation.txt` (PUBLIC)
- ✅ `project_report_q3.txt` (PUBLIC)
- ⚠️  `employee_review_2024.txt` (SENSITIVE)
- 🔒 `database_credentials.txt` (CONFIDENTIAL)

## Example Queries

When using with Claude Desktop, you can ask:
- "List all public documents"
- "Search for files about payments, excluding sensitive info"
- "Show me team_meeting_notes.txt"
- "Find files containing 'API' documentation"

## Testing

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for comprehensive testing instructions.

## Project Structure

```
.
├── file_scanner_mcp.py     # Main MCP server
├── test_documents/         # Sample documents (5 files)
├── TESTING_GUIDE.md        # Detailed testing instructions
└── README.md              # This file
```

## Tools Details

### search_files
```json
{
  "query": "payment",
  "exclude_sensitive": true,
  "limit": 10
}
```

### get_file_content
```json
{
  "filename": "team_meeting_notes.txt",
  "include_metadata": true,
  "response_format": "markdown"
}
```

### list_files
```json
{
  "pattern": "*.txt",
  "privacy_filter": "public",
  "response_format": "json"
}
```

## Limitations (By Design)

This is a **simple demonstration** server, not production-ready:
- No caching or indexing
- No authentication
- No encryption
- Simple pattern matching (not fuzzy search)
- File-based only (no database)

## Next Steps

To make this production-ready, consider adding:
- User authentication and authorization
- Full-text search indexing (e.g., Elasticsearch)
- Encrypted storage for sensitive files
- Audit logging
- Rate limiting
- Database backend

## License

MIT - This is a demonstration project

## Support

For MCP documentation: https://modelcontextprotocol.io
For FastMCP docs: https://github.com/modelcontextprotocol/python-sdk
