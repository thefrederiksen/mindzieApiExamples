#!/usr/bin/env python
"""
Test project controller connectivity endpoints.

This script tests both authenticated and unauthenticated ping endpoints
to verify API connectivity and authentication status.

Usage:
    python test_project_connectivity.py
"""

import os
import sys
import time
from pathlib import Path

# Import the proper mindzie_api library
from mindzie_api import MindzieAPIClient
from mindzie_api.exceptions import (
    MindzieAPIException, AuthenticationError, NotFoundError,
    TimeoutError, ConnectionError
)

# Add parent directory to path for .env loading
sys.path.append(str(Path(__file__).parent.parent))

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded credentials from {env_file}")
except ImportError:
    pass

# Import our utility functions
from api_utils import get_client, load_credentials

def test_unauthenticated_ping():
    """Test the unauthenticated ping endpoint using MindzieAPIClient."""
    print("\n" + "=" * 60)
    print("Testing Unauthenticated Project Ping")
    print("=" * 60)
    
    # Get credentials for base URL but create client without auth for this test
    tenant_id, api_key, base_url = load_credentials()
    if not base_url:
        base_url = "https://dev.mindziestudio.com"
    
    print(f"URL: {base_url}/api/project/unauthorized-ping")
    
    try:
        start_time = time.time()
        
        # Create client without authentication for unauthorized ping
        client = MindzieAPIClient(base_url=base_url)
        
        # Use the project controller's ping_unauthorized method
        response = client.projects.ping_unauthorized()
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        print(f"Response Time: {response_time:.2f}ms")
        print(f"Response: {response}")
        
        print("\n[SUCCESS] Unauthenticated ping works using mindzie_api library!")
        return True
        
    except Exception as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        print(f"Response Time: {response_time:.2f}ms")
        print(f"\n[ERROR] Request failed: {e}")
        return False
    finally:
        try:
            client.close()
        except:
            pass

def test_authenticated_ping():
    """Test the authenticated ping endpoint."""
    print("\n" + "=" * 60)
    print("Testing Authenticated Project Ping")
    print("=" * 60)
    
    client = get_client()
    if not client:
        return False
    
    tenant_id, _, base_url = load_credentials()
    print(f"URL: {base_url}/api/{tenant_id}/project/ping")
    print(f"Headers: Authorization: Bearer *** (using MindzieAPIClient)")
    
    try:
        start_time = time.time()
        
        # Use the project controller's authenticated ping method
        response = client.projects.ping()
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        print(f"Response Time: {response_time:.2f}ms")
        print(f"Response: {response}")
        
        print("\n[SUCCESS] Authenticated ping works using mindzie_api library!")
        return True
        
    except AuthenticationError:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        print(f"Response Time: {response_time:.2f}ms")
        print("\n[ERROR] Authentication failed - check your credentials")
        return False
    except TimeoutError:
        print("\n[ERROR] Request timed out")
        return False
    except Exception as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        print(f"Response Time: {response_time:.2f}ms")
        print(f"\n[ERROR] Request failed: {e}")
        return False
    finally:
        client.close()

def main():
    """Main test function."""
    print("=" * 70)
    print("mindzie Project Controller Connectivity Test")
    print("=" * 70)
    
    # Test results
    results = []
    
    # Test 1: Unauthenticated ping
    results.append(("Unauthenticated Ping", test_unauthenticated_ping()))
    
    # Test 2: Authenticated ping
    results.append(("Authenticated Ping", test_authenticated_ping()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    total = len(results)
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All connectivity tests passed!")
        print("The project controller is working correctly.")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        print("Check your network connection and credentials.")
    
    print("=" * 70)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())