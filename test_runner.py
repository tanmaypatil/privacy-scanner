#!/usr/bin/env python3
"""
Simple test script to verify MCP server tools work correctly.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from file_scanner_mcp import search_files, get_file_content, list_files
from file_scanner_mcp import SearchFilesInput, GetFileInput, ListFilesInput


async def run_tests():
    """Run basic tests on all MCP tools."""
    
    print("=" * 70)
    print("FILE SCANNER MCP SERVER - BASIC TESTS")
    print("=" * 70)
    print()
    
    # Test 1: List all files
    print("TEST 1: List all files")
    print("-" * 70)
    result = await list_files(ListFilesInput(response_format="markdown"))
    print(result)
    print()
    
    # Test 2: Search for 'payment' (exclude sensitive)
    print("TEST 2: Search for 'payment' (excluding sensitive files)")
    print("-" * 70)
    result = await search_files(SearchFilesInput(
        query="payment",
        exclude_sensitive=True,
        limit=5
    ))
    print(result)
    print()
    
    # Test 3: Search for 'employee' (include sensitive)
    print("TEST 3: Search for 'employee' (including sensitive files)")
    print("-" * 70)
    result = await search_files(SearchFilesInput(
        query="employee",
        exclude_sensitive=False,
        limit=5
    ))
    print(result)
    print()
    
    # Test 4: Get specific file content
    print("TEST 4: Get content of team_meeting_notes.txt")
    print("-" * 70)
    result = await get_file_content(GetFileInput(
        filename="team_meeting_notes.txt",
        include_metadata=True,
        response_format="markdown"
    ))
    print(result[:500] + "..." if len(result) > 500 else result)
    print()
    
    # Test 5: List only public files
    print("TEST 5: List only PUBLIC files")
    print("-" * 70)
    result = await list_files(ListFilesInput(
        privacy_filter="public",
        response_format="markdown"
    ))
    print(result)
    print()
    
    # Test 6: Privacy filtering demonstration
    print("TEST 6: Privacy Filtering - Search 'password'")
    print("-" * 70)
    print("WITH exclude_sensitive=True:")
    result = await search_files(SearchFilesInput(
        query="password",
        exclude_sensitive=True,
        limit=5
    ))
    print(result)
    print()
    print("WITH exclude_sensitive=False:")
    result = await search_files(SearchFilesInput(
        query="password",
        exclude_sensitive=False,
        limit=5
    ))
    print(result)
    print()
    
    print("=" * 70)
    print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_tests())
