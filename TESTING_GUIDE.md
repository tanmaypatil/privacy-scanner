# File Scanner MCP Server - Testing Guide

## Overview
This MCP server provides tools to search, list, and retrieve files with privacy-aware filtering.

## Project Structure
```
/home/claude/
├── file_scanner_mcp.py          # Main MCP server
└── test_documents/              # Sample documents
    ├── team_meeting_notes.txt   # PUBLIC
    ├── api_documentation.txt    # PUBLIC
    ├── project_report_q3.txt    # PUBLIC
    ├── employee_review_2024.txt # SENSITIVE
    └── database_credentials.txt # CONFIDENTIAL
```

## Available Tools

### 1. search_files
Search for files matching a query in filename or content.

**Parameters:**
- `query` (required): Search term to match
- `exclude_sensitive` (default: false): Filter out sensitive/confidential files
- `limit` (default: 10): Maximum results to return

### 2. get_file_content
Retrieve the complete content of a specific file.

**Parameters:**
- `filename` (required): Name of the file to retrieve
- `include_metadata` (default: false): Include file metadata
- `response_format` (default: "markdown"): Output format ("markdown" or "json")

### 3. list_files
List all files in the documents directory with optional filtering.

**Parameters:**
- `pattern` (optional): Glob pattern to filter files (e.g., "*.txt", "report*")
- `privacy_filter` (optional): Filter by privacy level ("public", "sensitive", "confidential")
- `response_format` (default: "markdown"): Output format ("markdown" or "json")

---

## Testing Methods

### Method 1: Using MCP Inspector (Recommended)

The MCP Inspector is an official tool for testing MCP servers interactively.

**Step 1: Install MCP Inspector**
```bash
npm install -g @modelcontextprotocol/inspector
```

**Step 2: Run the Inspector**
```bash
cd /home/claude
~/file_scanner_mcp % npx @modelcontextprotocol/inspector python3.11 file_scanner_mcp.py
```

This will:
1. Start your MCP server
2. Open a web interface (usually at http://localhost:5173)
3. Allow you to test tools interactively

**Step 3: Test the Tools**

In the Inspector web UI, you can:
- View all available tools and their schemas
- Execute tools with custom parameters
- See responses in real-time

**Example Test Cases:**

1. **List all files (public only)**
   ```json
   Tool: list_files
   Parameters: {
     "privacy_filter": "public",
     "response_format": "markdown"
   }
   ```
   Expected: Shows 3 public documents

2. **Search for "payment" (excluding sensitive)**
   ```json
   Tool: search_files
   Parameters: {
     "query": "payment",
     "exclude_sensitive": true,
     "limit": 10
   }
   ```
   Expected: Finds project_report_q3.txt and api_documentation.txt

3. **Get file content**
   ```json
   Tool: get_file_content
   Parameters: {
     "filename": "team_meeting_notes.txt",
     "include_metadata": true,
     "response_format": "markdown"
   }
   ```
   Expected: Returns meeting notes with metadata

4. **Search with privacy filtering OFF**
   ```json
   Tool: search_files
   Parameters: {
     "query": "database",
     "exclude_sensitive": false,
     "limit": 10
   }
   ```
   Expected: Finds database_credentials.txt (confidential)

5. **Search with privacy filtering ON**
   ```json
   Tool: search_files
   Parameters: {
     "query": "database",
     "exclude_sensitive": true,
     "limit": 10
   }
   ```
   Expected: Empty results (filters out confidential file)

---

### Method 2: Manual Testing with Python

You can test individual functions directly.

**Step 1: Create a test script**
```bash
cat > test_mcp.py << 'EOF'
import asyncio
from file_scanner_mcp import search_files, get_file_content, list_files
from file_scanner_mcp import SearchFilesInput, GetFileInput, ListFilesInput

async def test_tools():
    print("=== Testing list_files ===")
    result = await list_files(ListFilesInput())
    print(result)
    print("\n")
    
    print("=== Testing search_files (public only) ===")
    result = await search_files(SearchFilesInput(
        query="payment",
        exclude_sensitive=True
    ))
    print(result)
    print("\n")
    
    print("=== Testing get_file_content ===")
    result = await get_file_content(GetFileInput(
        filename="team_meeting_notes.txt",
        include_metadata=True
    ))
    print(result)

if __name__ == "__main__":
    asyncio.run(test_tools())
EOF
```

**Step 2: Run the test**
```bash
cd /home/claude
python test_mcp.py
```

---

### Method 3: Integration with Claude Desktop

To use this MCP server with Claude Desktop:

**Step 1: Update Claude Desktop Config**

On macOS, edit: `~/Library/Application Support/Claude/claude_desktop_config.json`
On Windows, edit: `%APPDATA%\Claude\claude_desktop_config.json`

Add your server:
```json
{
  "mcpServers": {
    "file-scanner": {
      "command": "python",
      "args": ["/home/claude/file_scanner_mcp.py"],
      "cwd": "/home/claude"
    }
  }
}
```

**Step 2: Restart Claude Desktop**

**Step 3: Test with Natural Language**

You can now ask Claude things like:
- "List all public documents"
- "Search for files about payments, but exclude any sensitive information"
- "Show me the content of team_meeting_notes.txt"
- "Find all files about employees"

---

## Expected Behavior

### Privacy Classification

Files are automatically classified based on content markers:

**CONFIDENTIAL** (highest sensitivity):
- Contains: `[CONFIDENTIAL]`, `SSN:`, `credit card:`, `password:`
- Example: `database_credentials.txt`

**SENSITIVE**:
- Contains: `[SENSITIVE]`, `internal only`, `employee id:`
- Example: `employee_review_2024.txt`

**PUBLIC** (default):
- No sensitive markers
- Examples: `team_meeting_notes.txt`, `api_documentation.txt`, `project_report_q3.txt`

### Privacy Filtering

When `exclude_sensitive=true` in search_files:
- Only PUBLIC files are returned
- SENSITIVE and CONFIDENTIAL files are filtered out

---

## Common Test Scenarios

### Scenario 1: Developer Documentation Search
```
Query: "API"
Exclude Sensitive: true
Expected: Finds api_documentation.txt
```

### Scenario 2: Security Audit
```
Query: "password"
Exclude Sensitive: false
Expected: Finds database_credentials.txt
```

### Scenario 3: List All Documents
```
Tool: list_files
Pattern: "*.txt"
Privacy Filter: null
Expected: Lists all 5 documents with privacy levels
```

### Scenario 4: Sensitive Data Protection
```
Query: "employee"
Exclude Sensitive: true
Expected: No results (employee_review_2024.txt is filtered)
```

---

## Troubleshooting

### Server won't start
```bash
# Check Python syntax
python -m py_compile file_scanner_mcp.py

# Verify dependencies
pip show mcp pydantic

# Check for port conflicts (if using HTTP transport)
lsof -i :8000
```

### No documents found
```bash
# Verify documents exist
ls -la /home/claude/test_documents/

# Check file permissions
chmod 644 /home/claude/test_documents/*.txt
```

### Import errors
```bash
# Reinstall dependencies
pip install --force-reinstall mcp pydantic --break-system-packages
```

---

## Adding Your Own Documents

To test with your own files:

```bash
# Add a new public document
echo "Your content here" > /home/claude/test_documents/my_document.txt

# Add a sensitive document (will auto-classify)
echo "[SENSITIVE] Employee data" > /home/claude/test_documents/sensitive_doc.txt

# Add a confidential document
echo "[CONFIDENTIAL] Password: secret123" > /home/claude/test_documents/secret.txt
```

The privacy classification happens automatically based on content markers.

---

## Next Steps

1. **Extend functionality**: Add tools for file creation, deletion, or updates
2. **Improve search**: Implement fuzzy matching or regex support
3. **Add resources**: Expose frequently accessed files as MCP resources
4. **Production features**: Add caching, indexing, or database storage
5. **Security**: Implement authentication and authorization

---

## Questions?

This is a simple demonstration server. For production use, consider:
- Proper authentication/authorization
- Database-backed file indexing
- Encryption for sensitive data
- Audit logging
- Rate limiting
- Input sanitization

Enjoy testing your MCP server! 🚀
