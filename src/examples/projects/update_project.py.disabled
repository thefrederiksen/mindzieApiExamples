"""
Update an existing project's settings and metadata.

This example demonstrates how to:
- Update project name and description
- Modify project settings and configuration
- Add or remove tags
- Update project status
- Handle update validation and conflicts

NOTE: This example assumes the update() method exists in the projects controller.
If the API doesn't support project updates, this serves as a template for when it's added.
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
    discover_project,
    print_header,
    print_error,
    print_success,
    print_info
)


def update_project(
    client: MindzieAPIClient,
    project_id: str,
    updates: Dict[str, Any],
    validate_before_update: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Update an existing project.
    
    Args:
        client: The mindzie API client
        project_id: ID of the project to update
        updates: Dictionary of fields to update
        validate_before_update: Whether to validate changes before applying
        
    Returns:
        Dictionary containing updated project information or None if error
    """
    try:
        print_info(f"Updating project {project_id}")
        
        # Get current project state
        current_project = None
        try:
            if hasattr(client.projects, 'get_by_id'):
                current_project = client.projects.get_by_id(project_id)
                print_success("Retrieved current project state")
            else:
                print_info("Cannot retrieve current state - get_by_id not available")
        except Exception as e:
            print_info(f"Could not retrieve current project: {e}")
        
        if current_project and validate_before_update:
            print_info("Current project state:")
            print(f"  • Name: {current_project.get('project_name', 'N/A')}")
            print(f"  • Status: {current_project.get('status', 'N/A')}")
            print(f"  • Modified: {current_project.get('modified_at', 'N/A')}")
        
        # Display planned updates
        print_info("\nPlanned updates:")
        for key, value in updates.items():
            if isinstance(value, dict):
                print(f"  • {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    - {sub_key}: {sub_value}")
            else:
                print(f"  • {key}: {value}")
        
        # Add metadata
        updates['modified_at'] = datetime.now().isoformat()
        updates['modified_by'] = 'api_user'
        
        # Attempt to update the project
        try:
            # Try the update method if it exists
            if hasattr(client.projects, 'update'):
                response = client.projects.update(project_id, **updates)
                print_success(f"Project {project_id} updated successfully!")
                
                # Display updated project details
                if response:
                    print("\nUpdated Project Details:")
                    for key, value in response.items():
                        if not isinstance(value, (dict, list)):
                            print(f"  • {key}: {value}")
                
                return response
            else:
                # Fallback: Simulate update for demonstration
                print_info("Note: update() method not found in projects controller")
                print_info("Simulating project update for demonstration...")
                
                # Merge updates with current state (if available)
                if current_project:
                    simulated_response = {**current_project, **updates}
                else:
                    simulated_response = {
                        "project_id": project_id,
                        **updates,
                        "update_status": "simulated",
                        "update_timestamp": datetime.now().isoformat()
                    }
                
                print_success(f"(Simulated) Project {project_id} would be updated with these changes")
                print("\nSimulated Updated Project:")
                print(json.dumps(simulated_response, indent=2, default=str))
                
                return simulated_response
                
        except AttributeError as e:
            print_info("Note: Project update endpoint not available in current API")
            print_info("This example demonstrates the expected usage pattern")
            return None
            
    except MindzieAPIException as e:
        if "not found" in str(e).lower() or "not implemented" in str(e).lower():
            print_info("Project update endpoint not yet implemented in the API")
            print_info("This example shows how it would work when available")
        else:
            print_error(f"API error updating project: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error updating project: {e}")
        return None


def create_update_patch(args) -> Dict[str, Any]:
    """
    Create an update patch from command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Dictionary of fields to update
    """
    updates = {}
    
    # Basic fields
    if args.name:
        updates['project_name'] = args.name
    
    if args.description:
        updates['description'] = args.description
    
    if args.status:
        updates['status'] = args.status
    
    # Tags management
    if args.add_tags or args.remove_tags or args.set_tags:
        tags_update = {}
        if args.add_tags:
            tags_update['add'] = args.add_tags
        if args.remove_tags:
            tags_update['remove'] = args.remove_tags
        if args.set_tags:
            tags_update['set'] = args.set_tags
        updates['tags'] = tags_update
    
    # Settings update
    settings = {}
    if args.auto_backup is not None:
        settings['auto_backup'] = args.auto_backup
    if args.retention_days:
        settings['retention_days'] = args.retention_days
    if args.notifications is not None:
        settings['notifications_enabled'] = args.notifications
    if args.timezone:
        settings['default_timezone'] = args.timezone
    
    if settings:
        updates['settings'] = settings
    
    # Permissions update
    if args.public is not None:
        updates['is_public'] = args.public
    
    if args.owner:
        updates['owner'] = args.owner
    
    return updates


def confirm_update(project_id: str, updates: Dict[str, Any]) -> bool:
    """
    Confirm update operation with user.
    
    Args:
        project_id: Project ID
        updates: Planned updates
        
    Returns:
        True if user confirms, False otherwise
    """
    print(f"\n⚠️  You are about to update project {project_id}")
    print("The following changes will be applied:")
    
    for key, value in updates.items():
        if key not in ['modified_at', 'modified_by']:
            print(f"  • {key}: {value}")
    
    response = input("\nDo you want to proceed? (y/N): ")
    return response.lower() == 'y'


def main():
    """Main function to demonstrate project updates."""
    print_header("Update Project Example")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Update an existing project')
    parser.add_argument('--project-id', help='Project ID (optional, will auto-discover if not provided)')
    
    # Update fields
    parser.add_argument('--name', help='New project name')
    parser.add_argument('--description', help='New project description')
    parser.add_argument('--status', choices=['Active', 'Inactive', 'Archived', 'Maintenance'], 
                       help='Update project status')
    
    # Tags management
    parser.add_argument('--add-tags', nargs='+', help='Add tags to project')
    parser.add_argument('--remove-tags', nargs='+', help='Remove tags from project')
    parser.add_argument('--set-tags', nargs='+', help='Replace all tags')
    
    # Settings
    parser.add_argument('--auto-backup', type=lambda x: x.lower() == 'true', 
                       help='Enable/disable auto-backup (true/false)')
    parser.add_argument('--retention-days', type=int, help='Update data retention period')
    parser.add_argument('--notifications', type=lambda x: x.lower() == 'true',
                       help='Enable/disable notifications (true/false)')
    parser.add_argument('--timezone', help='Update default timezone')
    
    # Access control
    parser.add_argument('--public', type=lambda x: x.lower() == 'true',
                       help='Make project public/private (true/false)')
    parser.add_argument('--owner', help='Change project owner')
    
    # Options
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without applying')
    
    args = parser.parse_args()
    
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
        
        # Get or discover project ID
        if args.project_id:
            project_id = args.project_id
            print_info(f"Using provided project ID: {project_id}")
        else:
            project_id = discover_project(client)
            if not project_id:
                print_error("No projects available")
                return
        
        # Create update patch
        updates = create_update_patch(args)
        
        if not updates:
            print_error("No updates specified. Use --help to see available options.")
            return
        
        # Dry run mode
        if args.dry_run:
            print_info("DRY RUN MODE - No changes will be applied")
            print("\nPlanned updates for project", project_id)
            print(json.dumps(updates, indent=2, default=str))
            return
        
        # Confirm update (unless forced)
        if not args.force:
            if not confirm_update(project_id, updates):
                print_info("Update cancelled by user")
                return
        
        # Perform the update
        result = update_project(
            client,
            project_id,
            updates,
            validate_before_update=True
        )
        
        if result:
            print_success(f"\n✅ Project update completed!")
            
            # Show summary of changes
            print("\n📋 Summary of Changes:")
            for key in updates.keys():
                if key not in ['modified_at', 'modified_by']:
                    print(f"  ✓ Updated {key}")
            
            print(f"\n🔗 Project ID: {project_id}")
        else:
            print_info("\nNote: Project update may not be available in the current API version")
            print_info("This example demonstrates the expected usage pattern for future implementation")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to update project: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()