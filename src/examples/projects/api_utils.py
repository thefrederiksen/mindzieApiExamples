#!/usr/bin/env python
"""
Shared utility functions for mindzie API examples.

This module provides common functionality used across multiple example scripts
including credential management, API URL configuration, and error handling.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

# Add parent directory to path for .env loading
sys.path.append(str(Path(__file__).parent.parent))

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

# Import the proper mindzie_api library
from mindzie_api import MindzieAPIClient
from mindzie_api.exceptions import (
    MindzieAPIException, AuthenticationError, NotFoundError,
    ValidationError, ServerError, TimeoutError
)

def load_credentials() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Load and validate API credentials from environment variables.
    
    Returns:
        tuple: (tenant_id, api_key, base_url) or (None, None, None) if invalid
    """
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY") 
    base_url = os.getenv("MINDZIE_API_URL", "https://dev.mindziestudio.com").rstrip("/")
    
    if not tenant_id or not api_key:
        return None, None, None
    
    return tenant_id, api_key, base_url

def print_credential_error() -> None:
    """Print helpful error message for missing credentials."""
    print("[ERROR] Missing credentials!")
    print("Set MINDZIE_TENANT_ID and MINDZIE_API_KEY environment variables")
    print("Optionally set MINDZIE_API_URL (defaults to https://dev.mindziestudio.com)")

def get_client() -> Optional[MindzieAPIClient]:
    """Get a configured MindzieAPIClient instance.
    
    Returns:
        MindzieAPIClient instance or None if credentials are missing
    """
    tenant_id, api_key, base_url = load_credentials()
    if not all([tenant_id, api_key, base_url]):
        print_credential_error()
        return None
    
    try:
        return MindzieAPIClient(
            base_url=base_url,
            tenant_id=tenant_id,
            api_key=api_key
        )
    except Exception as e:
        print(f"[ERROR] Failed to create API client: {e}")
        return None

def get_all_projects() -> Optional[List[Dict[str, Any]]]:
    """Get all projects from the API using MindzieAPIClient.
    
    Returns:
        list: List of projects as dictionaries or None on error
    """
    client = get_client()
    if not client:
        return None
    
    try:
        projects = client.projects.list_projects()
        # Convert Pydantic models to dictionaries for backward compatibility
        return [project.model_dump() for project in projects]
        
    except AuthenticationError:
        print("[ERROR] Authentication failed - check your credentials")
        return None
    except TimeoutError:
        print("[ERROR] Request timed out")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to retrieve projects: {e}")
        return None
    finally:
        try:
            client.close()
        except Exception as e:
            # Log the error but don't raise - we already have our result
            print(f"Warning: Failed to close client connection: {e}", file=sys.stderr)

def get_project_by_id(project_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific project by ID using MindzieAPIClient.
    
    Args:
        project_id: Project ID (GUID format)
    
    Returns:
        dict: Project data or None on error
    """
    client = get_client()
    if not client:
        return None
    
    try:
        project = client.projects.get_by_id(project_id)
        # Convert Pydantic model to dictionary for backward compatibility
        return project.model_dump()
        
    except NotFoundError:
        print(f"[ERROR] Project not found: {project_id}")
        return None
    except ValidationError as e:
        print(f"[ERROR] Invalid project ID format: {project_id}")
        return None
    except AuthenticationError:
        print("[ERROR] Authentication failed - check your credentials")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to retrieve project: {e}")
        return None
    finally:
        try:
            client.close()
        except Exception as e:
            # Log the error but don't raise - we already have our result
            print(f"Warning: Failed to close client connection: {e}", file=sys.stderr)

def get_project_summary_by_id(project_id: str) -> Optional[Dict[str, Any]]:
    """Get project summary by ID using MindzieAPIClient.
    
    Args:
        project_id: Project ID (GUID format)
    
    Returns:
        dict: Project summary data or None on error
    """
    client = get_client()
    if not client:
        return None
    
    try:
        summary = client.projects.get_summary(project_id)
        return summary.model_dump()
        
    except NotFoundError:
        print(f"[ERROR] Project summary not found: {project_id}")
        print("Note: The summary endpoint may not be implemented in the current API")
        return None
    except ValidationError as e:
        print(f"[ERROR] Invalid project ID format: {project_id}")
        return None
    except AuthenticationError:
        print("[ERROR] Authentication failed - check your credentials")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to retrieve project summary: {e}")
        return None
    finally:
        try:
            client.close()
        except Exception as e:
            # Log the error but don't raise - we already have our result
            print(f"Warning: Failed to close client connection: {e}", file=sys.stderr)

def discover_projects(needed_count: int = 1, message_prefix: str = "project") -> Optional[List[Dict[str, Any]]]:
    """Smart project discovery with user-friendly messages using MindzieAPIClient.
    
    Args:
        needed_count: Number of projects needed
        message_prefix: Descriptive term for what we're finding
    
    Returns:
        list: Selected projects as dictionaries or None if insufficient projects available
    """
    # Show discovery message
    if needed_count == 1:
        print(f"[INFO] Finding {message_prefix}, please wait...")
    else:
        print(f"[INFO] Finding {needed_count} {message_prefix}s for comparison, please wait...")
    
    projects = get_all_projects()
    if not projects:
        print("[ERROR] No projects found.")
        print("        Create a project in mindzieStudio first.")
        print("        Visit https://dev.mindziestudio.com to create a project.")
        return None
    
    if len(projects) < needed_count:
        if len(projects) == 1 and needed_count > 1:
            print(f"[WARNING] Only 1 project found, need {needed_count} for comparison.")
            print("          Create more projects in mindzieStudio to enable comparison.")
        else:
            print(f"[WARNING] Only {len(projects)} project(s) found, need {needed_count}")
        return projects[:needed_count]  # Return what we have
    
    # Select projects (first N for consistency)
    selected = projects[:needed_count]
    
    # Show what we picked
    if needed_count == 1:
        # Use consistent field naming from the model_dump
        project_name = selected[0].get('project_name', 'Unknown')
        project_id = selected[0].get('project_id', 'Unknown')
        print(f"[SUCCESS] Using project: '{project_name}' (auto-selected)")
        print(f"          ID: {project_id}")
    else:
        names = []
        for p in selected:
            name = p.get('project_name', 'Unknown')
            names.append(f"'{name}'")
        print(f"[SUCCESS] Using projects: {', '.join(names)} (auto-selected)")
    
    return selected

def get_random_projects(count: int = 2) -> Optional[List[Dict[str, Any]]]:
    """Get random sample projects for testing/comparison using MindzieAPIClient.
    
    Args:
        count: Number of random projects to return
    
    Returns:
        list: Random selection of projects as dictionaries
    """
    import random
    
    projects = get_all_projects()
    if not projects:
        return None
    
    if len(projects) <= count:
        return projects
    
    return random.sample(projects, count)

def show_usage_tip(script_name: str, example_id: Optional[str] = None) -> None:
    """Show helpful tip about customizing the script.
    
    Args:
        script_name: Name of the script file
        example_id: Optional example ID to show in the tip
    """
    if example_id:
        print(f"[TIP] To use a different project, run: python {script_name} {example_id}")
    else:
        print(f"[TIP] To use a different project, run: python {script_name} <project_id>")

def format_project_list(projects: List[Dict[str, Any]], max_display: int = 10) -> str:
    """Format project list for display.
    
    Args:
        projects: List of project objects
        max_display: Maximum projects to display
    
    Returns:
        str: Formatted project list
    """
    if not projects:
        return "No projects found"
    
    output = []
    for i, project in enumerate(projects[:max_display]):
        name = project.get('project_name', 'Unknown')
        project_id = project.get('project_id', 'Unknown')
        datasets = project.get('dataset_count', 'N/A')
        status = "Active" if project.get('is_active', True) else "Inactive"
        
        output.append(f"  {i+1}. {name}")
        output.append(f"     ID: {project_id}")
        output.append(f"     Datasets: {datasets} | Status: {status}")
    
    if len(projects) > max_display:
        output.append(f"  ... and {len(projects) - max_display} more projects")
    
    return "\n".join(output)

def main() -> int:
    """Main function to explain what api_utils.py does when run directly."""
    print("=" * 60)
    print("mindzie API Utilities (api_utils.py)")
    print("=" * 60)
    print()
    print("This file provides shared utility functions for mindzie API examples.")
    print("It's meant to be imported by other scripts, not run directly.")
    print()
    print("Functions provided:")
    print("  - get_client() - Get configured MindzieAPIClient instance")
    print("  - load_credentials() - Load API credentials from environment")
    print("  - get_all_projects() - Fetch all projects using proper API client")
    print("  - get_project_by_id() - Fetch specific project details with type safety")
    print("  - get_project_summary_by_id() - Fetch project summary statistics")
    print("  - discover_projects() - Smart project auto-selection")
    print("  - show_usage_tip() - Display helpful usage tips")
    print()
    print("Uses the official mindzie_api Python library!")
    print("  - Type-safe operations with Pydantic models")
    print("  - Automatic retries and error handling")
    print("  - Built-in authentication and connection management")
    print()
    print("Library Status:")
    print("  - All models fixed to match API response format")
    print("  - No known validation issues")
    print()
    print("Quick test:")
    
    # Test client creation
    client = get_client()
    if not client:
        return 1
    
    tenant_id, api_key, base_url = load_credentials()
    print("[SUCCESS] MindzieAPIClient created successfully")
    print(f"   Tenant: {tenant_id}")
    print(f"   API URL: {base_url}")
    
    # Test project access
    print()
    print("[INFO] Testing project access with mindzie_api library...")
    
    try:
        projects = client.projects.list_projects()
        print(f"[SUCCESS] Found {len(projects)} project(s) using mindzie_api library")
        print()
        print("Available projects:")
        project_dicts = [p.model_dump() for p in projects[:5]]
        print(format_project_list(project_dicts, 5))
    except Exception as e:
        print(f"[ERROR] Failed to access projects: {e}")
    finally:
        client.close()
    
    print()
    print("[TIP] To use these utilities in your scripts:")
    print("   from api_utils import get_client, discover_projects")
    print("   client = get_client()")
    print("   projects = client.projects.list_projects()  # Now working correctly!")
    print()
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())