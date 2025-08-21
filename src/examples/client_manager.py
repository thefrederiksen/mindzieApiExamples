#!/usr/bin/env python
"""
Context manager and improved client management for mindzie API.

This module provides a context manager for the MindzieAPIClient to ensure
proper resource cleanup and connection management.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Any, Dict
from contextlib import contextmanager

# Add parent directory to path for .env loading
sys.path.append(str(Path(__file__).parent.parent))

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

from mindzie_api import MindzieAPIClient
from mindzie_api.exceptions import MindzieAPIException


@contextmanager
def managed_client(
    base_url: Optional[str] = None,
    tenant_id: Optional[str] = None,
    api_key: Optional[str] = None
):
    """Context manager for MindzieAPIClient that ensures proper cleanup.
    
    Usage:
        with managed_client() as client:
            projects = client.projects.list_projects()
            # Client is automatically closed when exiting the context
    
    Args:
        base_url: API base URL (defaults to environment variable or dev URL)
        tenant_id: Tenant ID (defaults to environment variable)
        api_key: API key (defaults to environment variable)
        
    Yields:
        MindzieAPIClient instance
        
    Raises:
        ValueError: If credentials are missing
        MindzieAPIException: If client creation fails
    """
    # Get credentials from environment if not provided
    if not base_url:
        base_url = os.getenv("MINDZIE_API_URL", "https://dev.mindziestudio.com").rstrip("/")
    if not tenant_id:
        tenant_id = os.getenv("MINDZIE_TENANT_ID")
    if not api_key:
        api_key = os.getenv("MINDZIE_API_KEY")
    
    # Validate credentials
    if not all([base_url, tenant_id, api_key]):
        missing = []
        if not tenant_id:
            missing.append("MINDZIE_TENANT_ID")
        if not api_key:
            missing.append("MINDZIE_API_KEY")
        raise ValueError(f"Missing required credentials: {', '.join(missing)}")
    
    client = None
    try:
        # Create the client
        client = MindzieAPIClient(
            base_url=base_url,
            tenant_id=tenant_id,
            api_key=api_key
        )
        yield client
    finally:
        # Ensure cleanup even if an exception occurs
        if client:
            try:
                client.close()
            except Exception as e:
                # Log but don't raise - the original exception is more important
                print(f"Warning: Failed to close client: {e}", file=sys.stderr)


class ManagedMindzieClient:
    """Wrapper class that provides context manager support for MindzieAPIClient.
    
    This class can be used as a drop-in replacement for MindzieAPIClient with
    automatic resource management.
    
    Usage:
        # As a context manager
        with ManagedMindzieClient() as client:
            projects = client.projects.list_projects()
        
        # Or manually managed
        client = ManagedMindzieClient()
        try:
            projects = client.projects.list_projects()
        finally:
            client.close()
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """Initialize the managed client.
        
        Args:
            base_url: API base URL (defaults to environment variable or dev URL)
            tenant_id: Tenant ID (defaults to environment variable)
            api_key: API key (defaults to environment variable)
        """
        # Get credentials from environment if not provided
        if not base_url:
            base_url = os.getenv("MINDZIE_API_URL", "https://dev.mindziestudio.com").rstrip("/")
        if not tenant_id:
            tenant_id = os.getenv("MINDZIE_TENANT_ID")
        if not api_key:
            api_key = os.getenv("MINDZIE_API_KEY")
        
        # Validate credentials
        if not all([base_url, tenant_id, api_key]):
            missing = []
            if not tenant_id:
                missing.append("MINDZIE_TENANT_ID")
            if not api_key:
                missing.append("MINDZIE_API_KEY")
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")
        
        self._client = MindzieAPIClient(
            base_url=base_url,
            tenant_id=tenant_id,
            api_key=api_key
        )
    
    def __enter__(self):
        """Enter the context manager."""
        return self._client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and clean up resources."""
        self.close()
        return False  # Don't suppress exceptions
    
    def close(self):
        """Close the client connection."""
        if self._client:
            try:
                self._client.close()
            except Exception as e:
                print(f"Warning: Failed to close client: {e}", file=sys.stderr)
            finally:
                self._client = None
    
    def __getattr__(self, name):
        """Delegate attribute access to the underlying client."""
        return getattr(self._client, name)


def get_managed_client(
    base_url: Optional[str] = None,
    tenant_id: Optional[str] = None,
    api_key: Optional[str] = None
) -> ManagedMindzieClient:
    """Create a managed MindzieAPIClient instance.
    
    This is a convenience function that creates a ManagedMindzieClient
    with automatic credential loading from environment variables.
    
    Args:
        base_url: API base URL (defaults to environment variable or dev URL)
        tenant_id: Tenant ID (defaults to environment variable)
        api_key: API key (defaults to environment variable)
        
    Returns:
        ManagedMindzieClient instance
        
    Raises:
        ValueError: If credentials are missing
    """
    return ManagedMindzieClient(base_url, tenant_id, api_key)


if __name__ == "__main__":
    print("mindzie API Client Manager")
    print("=" * 50)
    print("\nThis module provides context managers for proper resource management.")
    print("\nUsage examples:")
    print("\n1. Using the context manager function:")
    print("   with managed_client() as client:")
    print("       projects = client.projects.list_projects()")
    print("\n2. Using the ManagedMindzieClient class:")
    print("   with ManagedMindzieClient() as client:")
    print("       projects = client.projects.list_projects()")
    print("\n3. Manual management:")
    print("   client = ManagedMindzieClient()")
    print("   try:")
    print("       projects = client.projects.list_projects()")
    print("   finally:")
    print("       client.close()")
    print("\nTesting client creation...")
    
    try:
        with managed_client() as client:
            print("[SUCCESS] Client created successfully")
            print("Testing API connectivity...")
            projects = client.projects.list_projects()
            print(f"[SUCCESS] Found {len(projects)} project(s)")
    except ValueError as e:
        print(f"[ERROR] {e}")
        print("\nPlease set the following environment variables:")
        print("  MINDZIE_TENANT_ID=your-tenant-id")
        print("  MINDZIE_API_KEY=your-api-key")
    except Exception as e:
        print(f"[ERROR] {e}")