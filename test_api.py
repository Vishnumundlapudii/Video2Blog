#!/usr/bin/env python3
"""
Test script for the FastAPI LangGraph Application.
This script demonstrates how to interact with the API endpoints.
"""

import requests
import json
import argparse
import sys

BASE_URL = "http://localhost:8000"

def test_root_endpoint():
    """Test the root endpoint."""
    response = requests.get(f"{BASE_URL}/")
    print("\n=== Root Endpoint ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_summarize_endpoint(youtube_url):
    """Test the summarize endpoint with a YouTube URL."""
    payload = {"url": youtube_url}
    print("\n=== Summarize Endpoint ===")
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/summarize", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.json().get("summary"), True
        else:
            print(f"Error: {response.text}")
            return None, False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None, False

def test_reflect_endpoint(summary):
    """Test the reflect endpoint with a summary."""
    payload = {"summary": summary}
    print("\n=== Reflect Endpoint ===")
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/reflect", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test the FastAPI LangGraph Application API")
    parser.add_argument("--url", type=str, help="YouTube URL to summarize", 
                        default="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    parser.add_argument("--summary-only", action="store_true", 
                        help="Only test the summarize endpoint")
    args = parser.parse_args()
    
    # Test root endpoint
    if not test_root_endpoint():
        print("Root endpoint test failed. Is the server running?")
        sys.exit(1)
    
    # Test summarize endpoint
    summary, success = test_summarize_endpoint(args.url)
    if not success:
        print("Summarize endpoint test failed.")
        sys.exit(1)
    
    # Test reflect endpoint if not summary-only mode
    if not args.summary_only and summary:
        if not test_reflect_endpoint(summary):
            print("Reflect endpoint test failed.")
            sys.exit(1)
    
    print("\n=== All tests passed successfully! ===")

if __name__ == "__main__":
    main()
