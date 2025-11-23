#!/usr/bin/env python3
"""
File Scanner MCP Server
A simple MCP server for scanning and retrieving files with privacy filtering.
"""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from pathlib import Path
import json
from enum import Enum

# Initialize MCP server
mcp = FastMCP("file_scanner_mcp")

# Configuration
DOCUMENTS_DIR = Path(__file__).parent/"test_documents"
print(f"Using documents directory: {DOCUMENTS_DIR}")


class PrivacyLevel(str, Enum):
    """Privacy classification for documents."""
    PUBLIC = "public"
    SENSITIVE = "sensitive"
    CONFIDENTIAL = "confidential"


class ResponseFormat(str, Enum):
    """Output format for responses."""
    MARKDOWN = "markdown"
    JSON = "json"


class SearchFilesInput(BaseModel):
    """Input model for file search."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    query: str = Field(
        ...,
        description="Search query to match against file names and content",
        min_length=1,
        max_length=200
    )
    exclude_sensitive: bool = Field(
        default=False,
        description="If true, exclude files marked as sensitive or confidential"
    )
    limit: int = Field(
        default=10,
        description="Maximum number of results to return",
        ge=1,
        le=50
    )


class GetFileInput(BaseModel):
    """Input model for retrieving file content."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    filename: str = Field(
        ...,
        description="Name of the file to retrieve (e.g., 'document1.txt')",
        min_length=1,
        max_length=255
    )
    include_metadata: bool = Field(
        default=False,
        description="If true, include file metadata (size, privacy level)"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )


class ListFilesInput(BaseModel):
    """Input model for listing files."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    pattern: Optional[str] = Field(
        default=None,
        description="Optional glob pattern to filter files (e.g., '*.txt', 'report*')"
    )
    privacy_filter: Optional[PrivacyLevel] = Field(
        default=None,
        description="Filter by privacy level: 'public', 'sensitive', or 'confidential'"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


def _classify_privacy(content: str) -> PrivacyLevel:
    """Classify document privacy level based on content markers."""
    content_lower = content.lower()
    
    # Check for privacy markers in content
    if any(marker in content_lower for marker in ["[confidential]", "ssn:", "credit card:", "password:"]):
        return PrivacyLevel.CONFIDENTIAL
    elif any(marker in content_lower for marker in ["[sensitive]", "internal only", "employee id:"]):
        return PrivacyLevel.SENSITIVE
    else:
        return PrivacyLevel.PUBLIC


def _get_file_metadata(filepath: Path) -> dict:
    """Get metadata for a file."""
    content = filepath.read_text()
    return {
        "filename": filepath.name,
        "size_bytes": filepath.stat().st_size,
        "privacy_level": _classify_privacy(content).value,
        "path": str(filepath)
    }


def _format_file_list(files_metadata: List[dict], format_type: ResponseFormat) -> str:
    """Format file list as markdown or JSON."""
    if format_type == ResponseFormat.JSON:
        return json.dumps({"files": files_metadata, "count": len(files_metadata)}, indent=2)
    
    # Markdown format
    if not files_metadata:
        return "No files found."
    
    result = f"# Found {len(files_metadata)} file(s)\n\n"
    for file_meta in files_metadata:
        result += f"## {file_meta['filename']}\n"
        result += f"- **Privacy Level**: {file_meta['privacy_level']}\n"
        result += f"- **Size**: {file_meta['size_bytes']} bytes\n\n"
    
    return result


@mcp.tool(
    name="search_files",
    annotations={
        "title": "Search Files by Query",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def search_files(params: SearchFilesInput) -> str:
    """Search for files matching a query in filename or content.
    
    This tool searches through all files in the documents directory, matching
    against both filenames and file content. Results can be filtered to exclude
    sensitive information.
    
    Args:
        params (SearchFilesInput): Search parameters containing:
            - query (str): Search term to match
            - exclude_sensitive (bool): Whether to filter out sensitive files
            - limit (int): Maximum results to return
    
    Returns:
        str: JSON-formatted response with matching files and their metadata
    """
    try:
        if not DOCUMENTS_DIR.exists():
            return json.dumps({"error": "Documents directory not found", "files": []}, indent=2)
        
        matches = []
        query_lower = params.query.lower()
        
        for filepath in DOCUMENTS_DIR.glob("*.txt"):
            try:
                content = filepath.read_text()
                privacy_level = _classify_privacy(content)
                
                # Apply privacy filter
                if params.exclude_sensitive and privacy_level != PrivacyLevel.PUBLIC:
                    continue
                
                # Check if query matches filename or content
                if query_lower in filepath.name.lower() or query_lower in content.lower():
                    matches.append({
                        "filename": filepath.name,
                        "privacy_level": privacy_level.value,
                        "size_bytes": filepath.stat().st_size,
                        "match_type": "filename" if query_lower in filepath.name.lower() else "content"
                    })
                    
                    if len(matches) >= params.limit:
                        break
                        
            except Exception as e:
                continue
        
        result = {
            "query": params.query,
            "files_found": len(matches),
            "excluded_sensitive": params.exclude_sensitive,
            "files": matches
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}", "files": []}, indent=2)


@mcp.tool(
    name="get_file_content",
    annotations={
        "title": "Get File Content",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_file_content(params: GetFileInput) -> str:
    """Retrieve the complete content of a specific file.
    
    This tool reads and returns the content of a file by name. It can include
    metadata like file size and privacy classification.
    
    Args:
        params (GetFileInput): Request parameters containing:
            - filename (str): Name of the file to retrieve
            - include_metadata (bool): Whether to include file metadata
            - response_format (ResponseFormat): 'markdown' or 'json'
    
    Returns:
        str: File content in requested format with optional metadata
    """
    try:
        filepath = DOCUMENTS_DIR / params.filename
        
        if not filepath.exists():
            error_msg = f"File '{params.filename}' not found in documents directory"
            if params.response_format == ResponseFormat.JSON:
                return json.dumps({"error": error_msg, "content": None}, indent=2)
            return f"**Error**: {error_msg}"
        
        content = filepath.read_text()
        
        if params.response_format == ResponseFormat.JSON:
            result = {"filename": params.filename, "content": content}
            if params.include_metadata:
                metadata = _get_file_metadata(filepath)
                result["metadata"] = metadata
            return json.dumps(result, indent=2)
        
        # Markdown format
        result = f"# {params.filename}\n\n"
        
        if params.include_metadata:
            metadata = _get_file_metadata(filepath)
            result += f"**Privacy Level**: {metadata['privacy_level']}  \n"
            result += f"**Size**: {metadata['size_bytes']} bytes\n\n"
            result += "---\n\n"
        
        result += content
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to read file: {str(e)}"
        if params.response_format == ResponseFormat.JSON:
            return json.dumps({"error": error_msg, "content": None}, indent=2)
        return f"**Error**: {error_msg}"


@mcp.tool(
    name="list_files",
    annotations={
        "title": "List All Files",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def list_files(params: ListFilesInput) -> str:
    """List all files in the documents directory with optional filtering.
    
    This tool provides a directory listing with metadata including privacy
    classification. Results can be filtered by pattern or privacy level.
    
    Args:
        params (ListFilesInput): Listing parameters containing:
            - pattern (Optional[str]): Glob pattern for filtering
            - privacy_filter (Optional[PrivacyLevel]): Filter by privacy level
            - response_format (ResponseFormat): 'markdown' or 'json'
    
    Returns:
        str: Formatted list of files with metadata
    """
    try:
        if not DOCUMENTS_DIR.exists():
            # DOCUMENTS_DIR.mkdir(parents=True)
            return _format_file_list([], params.response_format)
        
        # Determine glob pattern
        glob_pattern = params.pattern if params.pattern else "*.txt"
        
        files_metadata = []
        for filepath in DOCUMENTS_DIR.glob(glob_pattern):
            if filepath.is_file():
                metadata = _get_file_metadata(filepath)
                
                # Apply privacy filter if specified
                if params.privacy_filter and metadata["privacy_level"] != params.privacy_filter.value:
                    continue
                
                files_metadata.append(metadata)
        
        return _format_file_list(files_metadata, params.response_format)
        
    except Exception as e:
        error_msg = f"Failed to list files: {str(e)}"
        if params.response_format == ResponseFormat.JSON:
            return json.dumps({"error": error_msg, "files": []}, indent=2)
        return f"**Error**: {error_msg}"


if __name__ == "__main__":
    # Run with stdio transport (default for local tools)
    print("Starting File Scanner MCP Server...")
    mcp.run()
