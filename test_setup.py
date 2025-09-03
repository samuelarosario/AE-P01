#!/usr/bin/env python3
"""
Test script for Aviation Edge API client.
Run this after installing Python and the required packages.
"""

import sys
import os

def test_imports():
    """Test if required packages can be imported."""
    try:
        import requests
        print("✓ requests module imported successfully")
    except ImportError:
        print("✗ requests module not found. Run: pip install requests")
        return False
    
    try:
        import dotenv
        print("✓ python-dotenv module imported successfully")
    except ImportError:
        print("✗ python-dotenv module not found. Run: pip install python-dotenv")
        return False
    
    return True

def test_env_file():
    """Test if .env file exists and contains API key."""
    if os.path.exists('.env'):
        print("✓ .env file found")
        with open('.env', 'r') as f:
            content = f.read()
            if 'AVIATION_EDGE_API_KEY' in content:
                print("✓ API key found in .env file")
                return True
            else:
                print("✗ API key not found in .env file")
                return False
    else:
        print("✗ .env file not found")
        return False

def test_client():
    """Test if the Aviation Edge client can be instantiated."""
    try:
        from aviation_edge_client import AviationEdgeClient
        print("✓ AviationEdgeClient imported successfully")
        
        client = AviationEdgeClient()
        print("✓ AviationEdgeClient instantiated successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import AviationEdgeClient: {e}")
        return False
    except ValueError as e:
        print(f"✗ Failed to instantiate AviationEdgeClient: {e}")
        return False

def main():
    """Run all tests."""
    print("Aviation Edge API Client - Setup Test")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()
    
    tests = [
        ("Package imports", test_imports),
        ("Environment file", test_env_file),
        ("Client instantiation", test_client)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"Testing {test_name}:")
        if not test_func():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All tests passed! The setup is ready.")
        print("You can now run: python main.py")
    else:
        print("❌ Some tests failed. Please check the setup instructions.")

if __name__ == "__main__":
    main()
