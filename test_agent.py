#!/usr/bin/env python3
"""
Test script for the YouTube Analysis Agent.
This script demonstrates how to use the agent programmatically.
"""

import asyncio
import argparse
import sys
from main import run_youtube_analysis_agent

async def test_youtube_analysis_agent(youtube_url):
    """Test the YouTube Analysis Agent with a YouTube URL."""
    print(f"\n=== Testing YouTube Analysis Agent ===")
    print(f"YouTube URL: {youtube_url}")
    
    try:
        # Run the agent
        result = await run_youtube_analysis_agent(youtube_url)
        
        # Check if we got all the expected components in the result
        if not all(key in result for key in ["metadata", "summary", "reflection"]):
            print("Error: Missing expected components in the result")
            return False
        
        print("\n=== Test completed successfully! ===")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

async def main():
    parser = argparse.ArgumentParser(description="Test the YouTube Analysis Agent")
    parser.add_argument("--url", type=str, help="YouTube URL to analyze", 
                        default="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    args = parser.parse_args()
    
    # Test the agent
    success = await test_youtube_analysis_agent(args.url)
    
    if not success:
        print("Test failed.")
        sys.exit(1)
    
    print("\n=== All tests passed successfully! ===")

if __name__ == "__main__":
    asyncio.run(main())
