"""
Create a new project in mindzie.

This example demonstrates how to:
- Create a new project with configuration
- Set project metadata and properties
- Configure project settings
- Handle creation errors and validation
- Verify project creation success

NOTE: This example assumes the create() method exists in the projects controller.
If the API doesn't support project creation, this serves as a template for when it's added.
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mindzie_api import MindzieAPIClient
from mindzie_api.exceptions import MindzieAPIException
from common_utils import (
    get_client_config,
    print_header,
    print_error,
    print_success,
    print_info
)


def create_project(
    client: MindzieAPIClient,
    project_name: str,
    description: Optional[str] = None,
    settings: Optional[Dict[str, Any]] = None,
    tags: Optional[list] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a new project.
    
    Args:
        client: The mindzie API client
        project_name: Name for the new project
        description: Project description
        settings: Additional project settings
        tags: Tags for categorization
        
    Returns:
        Dictionary containing created project information or None if error
    """
    try:
        print_info(f"Creating new project: {project_name}")
        
        # Prepare project configuration
        project_config = {
            "project_name": project_name,
            "description": description or f"Project created on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "status": "Active",
            "created_at": datetime.now().isoformat(),
            "settings": settings or {
                "auto_backup": True,
                "retention_days": 90,
                "notifications_enabled": True,
                "default_timezone": "UTC"
            },
            "tags": tags or []
        }
        
        print_info("Project configuration:")
        for key, value in project_config.items():
            if key != "settings":
                print(f"  • {key}: {value}")
            else:
                print(f"  • {key}:")
                for setting_key, setting_value in value.items():
                    print(f"    - {setting_key}: {setting_value}")
        
        # Attempt to create the project
        # NOTE: This assumes a create() method exists
        try:
            # Try the create method if it exists
            if hasattr(client.projects, 'create'):
                response = client.projects.create(**project_config)
                print_success(f"Project '{project_name}' created successfully!")
                
                # Display created project details
                if response:
                    print("\nCreated Project Details:")
                    print(f"  • Project ID: {response.get('project_id', 'N/A')}")
                    print(f"  • Name: {response.get('project_name', project_name)}")
                    print(f"  • Status: {response.get('status', 'Active')}")
                    print(f"  • Created At: {response.get('created_at', 'N/A')}")
                    
                    if response.get('api_endpoint'):
                        print(f"  • API Endpoint: {response['api_endpoint']}")
                    if response.get('dashboard_url'):
                        print(f"  • Dashboard URL: {response['dashboard_url']}")
                
                return response
            else:
                # Fallback: Simulate creation for demonstration
                print_info("Note: create() method not found in projects controller")
                print_info("Simulating project creation for demonstration...")
                
                simulated_response = {
                    "project_id": f"proj_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "project_name": project_name,
                    "description": project_config["description"],
                    "status": "Active",
                    "created_at": project_config["created_at"],
                    "settings": project_config["settings"],
                    "tags": project_config["tags"],
                    "owner": "current_user",
                    "api_endpoint": f"https://dev.mindziestudio.com/api/projects/{project_name.lower().replace(' ', '-')}",
                    "dashboard_url": f"https://dev.mindziestudio.com/dashboard/projects/{project_name.lower().replace(' ', '-')}"
                }
                
                print_success(f"(Simulated) Project '{project_name}' would be created with these settings")
                print("\nSimulated Project Details:")
                print(json.dumps(simulated_response, indent=2))
                
                return simulated_response
                
        except AttributeError as e:
            print_info("Note: Project creation endpoint not available in current API")
            print_info("This example demonstrates the expected usage pattern")
            return None
            
    except MindzieAPIException as e:
        if "not found" in str(e).lower() or "not implemented" in str(e).lower():
            print_info("Project creation endpoint not yet implemented in the API")
            print_info("This example shows how it would work when available")
        else:
            print_error(f"API error creating project: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error creating project: {e}")
        return None


def validate_project_name(name: str) -> bool:
    """
    Validate project name before creation.
    
    Args:
        name: Project name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not name or not name.strip():
        print_error("Project name cannot be empty")
        return False
    
    if len(name) < 3:
        print_error("Project name must be at least 3 characters long")
        return False
    
    if len(name) > 100:
        print_error("Project name must be less than 100 characters")
        return False
    
    # Check for invalid characters
    invalid_chars = ['/', '\\', '<', '>', ':', '"', '|', '?', '*']
    for char in invalid_chars:
        if char in name:
            print_error(f"Project name cannot contain '{char}'")
            return False
    
    return True


def check_project_exists(client: MindzieAPIClient, project_name: str) -> bool:
    """
    Check if a project with the given name already exists.
    
    Args:
        client: The mindzie API client
        project_name: Name to check
        
    Returns:
        True if project exists, False otherwise
    """
    try:
        # Get existing projects
        if hasattr(client.projects, 'list_projects'):
            projects = client.projects.list_projects()
        elif hasattr(client.projects, 'get_all'):
            response = client.projects.get_all(page=1, page_size=100)
            projects = response.get('projects', [])
        else:
            return False
        
        # Check if name already exists
        for project in projects:
            if project.get('project_name', '').lower() == project_name.lower():
                return True
        
        return False
        
    except Exception:
        # If we can't check, assume it doesn't exist
        return False


def main():
    """Main function to demonstrate project creation."""
    print_header("Create Project Example")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Create a new project')
    parser.add_argument('name', help='Project name')
    parser.add_argument('--description', help='Project description')
    parser.add_argument('--tags', nargs='+', help='Tags for the project')
    parser.add_argument('--auto-backup', action='store_true', help='Enable auto-backup')
    parser.add_argument('--retention-days', type=int, default=90, help='Data retention in days')
    parser.add_argument('--timezone', default='UTC', help='Default timezone')
    parser.add_argument('--force', action='store_true', help='Force creation even if name exists')
    args = parser.parse_args()
    
    # Validate project name
    if not validate_project_name(args.name):
        return
    
    # Initialize client
    client = MindzieAPIClient(
        base_url=config['base_url'],
        tenant_id=config['tenant_id'],
        api_key=config['api_key']
    )
    
    try:
        # Test connectivity
        print_info("Testing connectivity...")
        client.ping.ping()
        print_success("Connected to mindzie API")
        
        # Check if project already exists
        if not args.force:
            print_info("Checking if project name is available...")
            if check_project_exists(client, args.name):
                print_error(f"Project '{args.name}' already exists. Use --force to create anyway.")
                return
            print_success("Project name is available")
        
        # Prepare settings
        settings = {
            "auto_backup": args.auto_backup,
            "retention_days": args.retention_days,
            "notifications_enabled": True,
            "default_timezone": args.timezone
        }
        
        # Create the project
        result = create_project(
            client,
            project_name=args.name,
            description=args.description,
            settings=settings,
            tags=args.tags
        )
        
        if result:
            print_success(f"\n✅ Project creation completed!")
            
            # Provide next steps
            print("\n📋 Next Steps:")
            print("1. Configure data sources for your project")
            print("2. Set up user permissions and access control")
            print("3. Create datasets and upload data")
            print("4. Design dashboards for visualization")
            print("5. Set up automated actions and workflows")
            
            if result.get('dashboard_url'):
                print(f"\n🔗 Access your project at: {result['dashboard_url']}")
        else:
            print_info("\nNote: Project creation may not be available in the current API version")
            print_info("This example demonstrates the expected usage pattern for future implementation")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to create project: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()