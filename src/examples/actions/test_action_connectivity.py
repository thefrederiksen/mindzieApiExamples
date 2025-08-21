#!/usr/bin/env python
"""
Test connectivity to mindzie Studio Action endpoints.

This example demonstrates how to test both authenticated and unauthenticated
connectivity to the Action and ActionExecution controllers.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for shared utilities
sys.path.append(str(Path(__file__).parent.parent))

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

# Import from parent directory utilities
from common_utils import create_client, handle_api_error, print_section, print_success, print_error

def test_unauthenticated_connectivity(client, project_id: str):
    """Test unauthenticated connectivity to action endpoints."""
    print_section("Testing Unauthenticated Action Connectivity")
    
    try:
        # Test Action controller unauthenticated ping
        response = client.actions.ping_unauthorized(project_id)
        print_success(f"✓ Action ping (unauthorized): {response}")
    except Exception as e:
        print_error(f"✗ Action ping (unauthorized) failed: {e}")
    
    try:
        # Test ActionExecution controller unauthenticated ping
        response = client.action_executions.ping_unauthorized(project_id)
        print_success(f"✓ ActionExecution ping (unauthorized): {response}")
    except Exception as e:
        print_error(f"✗ ActionExecution ping (unauthorized) failed: {e}")

def test_authenticated_connectivity(client, project_id: str):
    """Test authenticated connectivity to action endpoints."""
    print_section("Testing Authenticated Action Connectivity")
    
    try:
        # Test Action controller authenticated ping
        response = client.actions.ping(project_id)
        print_success(f"✓ Action ping (authenticated): {response}")
    except Exception as e:
        print_error(f"✗ Action ping (authenticated) failed: {e}")
        return False
    
    try:
        # Test ActionExecution controller authenticated ping
        response = client.action_executions.ping(project_id)
        print_success(f"✓ ActionExecution ping (authenticated): {response}")
        return True
    except Exception as e:
        print_error(f"✗ ActionExecution ping (authenticated) failed: {e}")
        return False

def main():
    """Main function to test action connectivity."""
    print("mindzie-api Action Connectivity Test")
    print("=" * 50)
    
    # Get credentials
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    
    if not tenant_id or not api_key:
        print_error("Missing required credentials!")
        print("\nPlease set the following environment variables:")
        print("  MINDZIE_TENANT_ID=your-tenant-id")
        print("  MINDZIE_API_KEY=your-api-key")
        print("\nOr create a .env file in the examples directory.")
        return 1
    
    # Create client
    client = create_client()
    if not client:
        return 1
    
    try:
        # First, let's get a project to test with
        print_section("Getting Available Projects")
        projects_response = client.projects.get_projects()
        projects = projects_response.get('projects', [])
        
        if not projects:
            print_error("No projects found. Please create a project first.")
            return 1
        
        # Use the first project for testing
        project = projects[0]
        project_id = project['id']
        project_name = project.get('name', 'Unknown')
        
        print_success(f"Using project: {project_name} (ID: {project_id})")
        
        # Test unauthenticated connectivity
        test_unauthenticated_connectivity(client, project_id)
        
        # Test authenticated connectivity
        auth_success = test_authenticated_connectivity(client, project_id)
        
        if auth_success:
            print_section("Connectivity Test Summary")
            print_success("✓ All connectivity tests passed!")
            print("Action endpoints are accessible and authentication is working.")
        else:
            print_section("Connectivity Test Summary")
            print_error("✗ Some connectivity tests failed.")
            print("Check your credentials and network connectivity.")
            return 1
    
    except Exception as e:
        handle_api_error(e, "connectivity testing")
        return 1
    
    finally:
        client.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())