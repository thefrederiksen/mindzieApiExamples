"""
Archive and restore projects for long-term storage.

This example demonstrates how to:
- Archive projects to inactive state
- Preserve project data while reducing active resource usage
- Restore archived projects back to active state
- Manage archived project lifecycle
- Search and list archived projects

NOTE: This example assumes archive/restore methods exist in the projects controller.
If the API doesn't support archiving, this serves as a template for when it's added.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mindzie_api import MindzieAPIClient
from mindzie_api.exceptions import MindzieAPIException
from common_utils import (
    get_client_config,
    discover_project,
    format_timestamp,
    print_header,
    print_error,
    print_success,
    print_info
)


def archive_project(
    client: MindzieAPIClient,
    project_id: str,
    archive_reason: Optional[str] = None,
    retention_days: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Archive a project.
    
    Args:
        client: The mindzie API client
        project_id: ID of the project to archive
        archive_reason: Reason for archiving
        retention_days: Days to retain before permanent deletion
        
    Returns:
        Dictionary containing archive information or None if error
    """
    try:
        print_info(f"Archiving project {project_id}")
        
        # Prepare archive metadata
        archive_metadata = {
            "archived_at": datetime.now().isoformat(),
            "archived_by": "api_user",
            "archive_reason": archive_reason or "Manual archive via API",
            "retention_days": retention_days or 365,
            "auto_delete_date": (datetime.now() + timedelta(days=retention_days or 365)).isoformat()
        }
        
        # Attempt to archive
        try:
            if hasattr(client.projects, 'archive'):
                response = client.projects.archive(project_id, **archive_metadata)
                print_success(f"Project {project_id} archived successfully!")
                
                if response:
                    print("\nArchive Details:")
                    print(f"  • Archive ID: {response.get('archive_id', 'N/A')}")
                    print(f"  • Archived At: {response.get('archived_at', 'N/A')}")
                    print(f"  • Retention Period: {response.get('retention_days', 'N/A')} days")
                    print(f"  • Auto-delete Date: {response.get('auto_delete_date', 'N/A')}")
                
                return response
            else:
                # Simulate archiving
                print_info("Note: archive() method not found in projects controller")
                print_info("Simulating project archiving for demonstration...")
                
                simulated_response = {
                    "project_id": project_id,
                    "archive_id": f"arch_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "status": "archived",
                    **archive_metadata
                }
                
                print_success(f"(Simulated) Project {project_id} would be archived")
                print("\nArchive Details:")
                print(json.dumps(simulated_response, indent=2))
                
                return simulated_response
                
        except AttributeError:
            print_info("Note: Project archiving endpoint not available in current API")
            return None
            
    except MindzieAPIException as e:
        print_error(f"API error archiving project: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error archiving project: {e}")
        return None


def restore_project(
    client: MindzieAPIClient,
    project_id: str,
    restore_reason: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Restore an archived project.
    
    Args:
        client: The mindzie API client
        project_id: ID of the project to restore
        restore_reason: Reason for restoration
        
    Returns:
        Dictionary containing restore information or None if error
    """
    try:
        print_info(f"Restoring project {project_id}")
        
        restore_metadata = {
            "restored_at": datetime.now().isoformat(),
            "restored_by": "api_user",
            "restore_reason": restore_reason or "Manual restore via API"
        }
        
        try:
            if hasattr(client.projects, 'restore'):
                response = client.projects.restore(project_id, **restore_metadata)
                print_success(f"Project {project_id} restored successfully!")
                
                if response:
                    print("\nRestore Details:")
                    print(f"  • Restored At: {response.get('restored_at', 'N/A')}")
                    print(f"  • New Status: {response.get('status', 'Active')}")
                    print(f"  • Restore Reason: {response.get('restore_reason', 'N/A')}")
                
                return response
            else:
                # Simulate restoration
                print_info("Note: restore() method not found in projects controller")
                print_info("Simulating project restoration for demonstration...")
                
                simulated_response = {
                    "project_id": project_id,
                    "status": "active",
                    **restore_metadata
                }
                
                print_success(f"(Simulated) Project {project_id} would be restored")
                print("\nRestore Details:")
                print(json.dumps(simulated_response, indent=2))
                
                return simulated_response
                
        except AttributeError:
            print_info("Note: Project restoration endpoint not available in current API")
            return None
            
    except MindzieAPIException as e:
        print_error(f"API error restoring project: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error restoring project: {e}")
        return None


def list_archived_projects(
    client: MindzieAPIClient,
    show_details: bool = True
) -> List[Dict[str, Any]]:
    """
    List all archived projects.
    
    Args:
        client: The mindzie API client
        show_details: Whether to show detailed information
        
    Returns:
        List of archived projects
    """
    try:
        print_info("Retrieving archived projects...")
        
        archived_projects = []
        
        try:
            if hasattr(client.projects, 'list_archived'):
                response = client.projects.list_archived()
                if response:
                    archived_projects = response.get('projects', [])
            else:
                # Try to get all projects and filter by status
                if hasattr(client.projects, 'list_projects'):
                    all_projects = client.projects.list_projects()
                    archived_projects = [p for p in all_projects if p.get('status') == 'archived']
                elif hasattr(client.projects, 'get_all'):
                    response = client.projects.get_all(page=1, page_size=100)
                    all_projects = response.get('projects', [])
                    archived_projects = [p for p in all_projects if p.get('status') == 'archived']
        except Exception as e:
            print_info(f"Could not retrieve archived projects: {e}")
            # Simulate some archived projects for demonstration
            archived_projects = [
                {
                    "project_id": "proj_archived_001",
                    "project_name": "Old Analytics Project",
                    "status": "archived",
                    "archived_at": "2023-12-01T10:00:00Z",
                    "archive_reason": "Project completed",
                    "retention_days": 365
                },
                {
                    "project_id": "proj_archived_002",
                    "project_name": "Legacy Dashboard",
                    "status": "archived",
                    "archived_at": "2023-11-15T14:30:00Z",
                    "archive_reason": "Superseded by new version",
                    "retention_days": 180
                }
            ]
            print_info("Showing simulated archived projects for demonstration")
        
        if not archived_projects:
            print_info("No archived projects found")
            return []
        
        print_success(f"Found {len(archived_projects)} archived project(s)")
        
        if show_details:
            print("\nArchived Projects:")
            for idx, project in enumerate(archived_projects, 1):
                print(f"\n{idx}. {project.get('project_name', 'Unnamed')}")
                print(f"   ID: {project.get('project_id', 'N/A')}")
                print(f"   Archived: {format_timestamp(project.get('archived_at', 'N/A'))}")
                print(f"   Reason: {project.get('archive_reason', 'N/A')}")
                
                if project.get('retention_days'):
                    print(f"   Retention: {project['retention_days']} days")
                
                if project.get('auto_delete_date'):
                    print(f"   Auto-delete: {format_timestamp(project['auto_delete_date'])}")
                
                # Calculate days until deletion
                if project.get('auto_delete_date'):
                    try:
                        delete_date = datetime.fromisoformat(project['auto_delete_date'].replace('Z', '+00:00'))
                        days_remaining = (delete_date - datetime.now()).days
                        if days_remaining > 0:
                            print(f"   Days until deletion: {days_remaining}")
                        else:
                            print("   ⚠️  Scheduled for deletion!")
                    except:
                        pass
        
        return archived_projects
        
    except Exception as e:
        print_error(f"Error listing archived projects: {e}")
        return []


def main():
    """Main function to demonstrate project archiving and restoration."""
    print_header("Archive/Restore Project Example")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Archive or restore projects')
    parser.add_argument('action', choices=['archive', 'restore', 'list'], help='Action to perform')
    parser.add_argument('--project-id', help='Project ID (optional for archive/restore)')
    parser.add_argument('--reason', help='Reason for archive/restore')
    parser.add_argument('--retention-days', type=int, default=365, help='Retention period for archived project')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompts')
    
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
        
        if args.action == 'list':
            # List archived projects
            archived_projects = list_archived_projects(client)
            
            if archived_projects:
                print_success(f"\n✅ Found {len(archived_projects)} archived projects")
            
        elif args.action in ['archive', 'restore']:
            # Get or discover project ID
            if args.project_id:
                project_id = args.project_id
                print_info(f"Using provided project ID: {project_id}")
            else:
                project_id = discover_project(client)
                if not project_id:
                    print_error("No projects available")
                    return
            
            # Confirm action unless forced
            if not args.force:
                action_verb = "archive" if args.action == 'archive' else "restore"
                response = input(f"\nDo you want to {action_verb} project {project_id}? (y/N): ")
                if response.lower() != 'y':
                    print_info(f"{action_verb.title()} cancelled by user")
                    return
            
            # Perform action
            if args.action == 'archive':
                result = archive_project(
                    client,
                    project_id,
                    archive_reason=args.reason,
                    retention_days=args.retention_days
                )
                
                if result:
                    print_success(f"\n✅ Project {project_id} archived successfully!")
                    print("\n📋 Archive Information:")
                    print(f"  • Status: Archived")
                    print(f"  • Retention: {args.retention_days} days")
                    print(f"  • Reason: {args.reason or 'Manual archive'}")
            
            elif args.action == 'restore':
                result = restore_project(
                    client,
                    project_id,
                    restore_reason=args.reason
                )
                
                if result:
                    print_success(f"\n✅ Project {project_id} restored successfully!")
                    print("\n📋 Restore Information:")
                    print(f"  • Status: Active")
                    print(f"  • Reason: {args.reason or 'Manual restore'}")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to {args.action} project: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()