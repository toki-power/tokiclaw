#!/usr/bin/env python3
"""
Download an exported BigQuery file from the MCP server.
Usage: python download_export.py <download_url> [output_file]
"""

import sys
import requests

def download_export(url, output_file=None):
    """Download an exported file from the MCP server."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    # Extract filename from URL if not provided
    if not output_file:
        output_file = url.split('/')[-1]
    
    # Download the file
    with open(output_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_export.py <download_url> [output_file]")
        print("Example: python download_export.py http://localhost:5001/exports/export_abc123.csv")
        sys.exit(1)
    
    url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        downloaded_file = download_export(url, output_file)
        print(f"✓ Downloaded to: {downloaded_file}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
