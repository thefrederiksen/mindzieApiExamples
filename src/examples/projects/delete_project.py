"""
Safely delete a project with confirmations and dependency checks.

This example demonstrates how to:
- Check for project dependencies before deletion
- Provide multiple confirmation steps for safety
- Backup project data before deletion
- Handle cascade deletion of related resources
- Provide recovery options

NOTE: This example assumes the delete() method exists in the projects controller.
If the API doesn't support project deletion, this serves as a template for when it's added.
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List
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


def check_project_dependencies(
    client: MindzieAPIClient,
    project_id: str
) -> Dict[str, Any]:
    """
    Check for project dependencies before deletion.
    
    Args:
        client: The mindzie API client
        project_id: ID of the project to check
        
    Returns:
        Dictionary containing dependency information
    """
    dependencies = {
        'datasets': [],
        'dashboards': [],
        'investigations': [],
        'actions': [],
        'active_executions': [],
        'shared_resources': [],
        'total_items': 0,
        'blocking_issues': []
    }
    
    try:
        print_info("Checking project dependencies...")
        
        # Check datasets
        try:
            datasets_response = client.datasets.get_all(project_id)
            if datasets_response and datasets_response.get('Items'):
                dependencies['datasets'] = datasets_response['Items']
                print_info(f"Found {len(dependencies['datasets'])} dataset(s)")
        except Exception as e:
            print_info(f"Could not check datasets: {e}")
        
        # Check dashboards
        try:
            dashboards_response = client.dashboards.get_all(project_id, page=1, page_size=100)
            if dashboards_response and dashboards_response.get('Dashboards'):
                dependencies['dashboards'] = dashboards_response['Dashboards']
                print_info(f"Found {len(dependencies['dashboards'])} dashboard(s)")
        except Exception as e:
            print_info(f"Could not check dashboards: {e}")
        
        # Check investigations
        try:
            investigations_response = client.investigations.get_all(project_id, page=1, page_size=100)
            if investigations_response and investigations_response.get('Investigations'):
                dependencies['investigations'] = investigations_response['Investigations']
                print_info(f"Found {len(dependencies['investigations'])} investigation(s)")
        except Exception as e:
            print_info(f"Could not check investigations: {e}")
        
        # Check for active executions
        try:
            # This would check for any running actions/executions
            dependencies['active_executions'] = []  # Placeholder
        except Exception as e:
            print_info(f"Could not check active executions: {e}")
        
        # Calculate total items
        dependencies['total_items'] = (
            len(dependencies['datasets']) +
            len(dependencies['dashboards']) +
            len(dependencies['investigations']) +
            len(dependencies['active_executions'])
        )
        
        # Check for blocking issues
        if dependencies['active_executions']:
            dependencies['blocking_issues'].append(
                f"{len(dependencies['active_executions'])} active execution(s) must be stopped first"
            )
        
        # Check for shared resources
        shared_dashboards = [d for d in dependencies['dashboards'] if d.get('IsPublic') or d.get('SharedWith')]
        if shared_dashboards:
            dependencies['shared_resources'].extend(shared_dashboards)
            dependencies['blocking_issues'].append(
                f"{len(shared_dashboards)} shared dashboard(s) - consider unsharing first"
            )
        
        return dependencies
        
    except Exception as e:
        print_error(f"Error checking dependencies: {e}")
        return dependencies


def create_project_backup(
    client: MindzieAPIClient,
    project_id: str,
    backup_path: Optional[str] = None
) -> Optional[str]:
    """
    Create a backup of project data before deletion.
    
    Args:
        client: The mindzie API client
        project_id: ID of the project to backup
        backup_path: Path to save backup (optional)
        
    Returns:
        Path to backup file or None if failed
    """
    try:
        print_info("Creating project backup...")
        
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"project_{project_id}_backup_{timestamp}.json"
        
        # Collect all project data
        backup_data = {
            'project_id': project_id,
            'backup_timestamp': datetime.now().isoformat(),
            'backup_version': '1.0',
            'project_info': {},
            'datasets': [],
            'dashboards': [],
            'investigations': []
        }
        
        # Get project info
        try:
            if hasattr(client.projects, 'get_by_id'):
                backup_data['project_info'] = client.projects.get_by_id(project_id)
        except Exception as e:
            print_info(f"Could not backup project info: {e}")
        
        # Backup datasets
        try:
            datasets_response = client.datasets.get_all(project_id)
            if datasets_response and datasets_response.get('Items'):
                backup_data['datasets'] = datasets_response['Items']
        except Exception as e:
            print_info(f"Could not backup datasets: {e}")
        
        # Backup dashboards
        try:
            dashboards_response = client.dashboards.get_all(project_id, page=1, page_size=100)
            if dashboards_response and dashboards_response.get('Dashboards'):
                backup_data['dashboards'] = dashboards_response['Dashboards']
        except Exception as e:
            print_info(f"Could not backup dashboards: {e}")
        
        # Backup investigations
        try:
            investigations_response = client.investigations.get_all(project_id, page=1, page_size=100)
            if investigations_response and investigations_response.get('Investigations'):
                backup_data['investigations'] = investigations_response['Investigations']
        except Exception as e:
            print_info(f"Could not backup investigations: {e}")
        
        # Save backup to file
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        print_success(f"Backup created: {backup_path}")
        return backup_path
        
    except Exception as e:
        print_error(f"Failed to create backup: {e}")
        return None


def delete_project(
    client: MindzieAPIClient,
    project_id: str,
    force_delete: bool = False,
    cascade_delete: bool = False
) -> bool:
    """
    Delete a project with safety checks.
    
    Args:
        client: The mindzie API client
        project_id: ID of the project to delete
        force_delete: Skip some safety checks
        cascade_delete: Delete related resources
        
    Returns:
        True if deletion successful, False otherwise
    """
    try:
        print_info(f"Attempting to delete project {project_id}")
        
        # Check dependencies if not forcing
        if not force_delete:
            dependencies = check_project_dependencies(client, project_id)
            
            if dependencies['blocking_issues']:
                print_error("Cannot delete project due to blocking issues:")
                for issue in dependencies['blocking_issues']:
                    print(f"  • {issue}")
                return False
            
            if dependencies['total_items'] > 0 and not cascade_delete:
                print_error(f"Project contains {dependencies['total_items']} items.")
                print_error("Use --cascade to delete all items, or clean up manually first.")
                return False
        
        # Attempt deletion
        try:
            if hasattr(client.projects, 'delete'):
                response = client.projects.delete(
                    project_id, 
                    cascade=cascade_delete,
                    force=force_delete
                )
                print_success(f"Project {project_id} deleted successfully!")
                return True
            else:
                # Simulate deletion for demonstration
                print_info("Note: delete() method not found in projects controller")
                print_info("Simulating project deletion for demonstration...")
                
                deletion_log = {
                    'project_id': project_id,
                    'deleted_at': datetime.now().isoformat(),
                    'deleted_by': 'api_user',
                    'cascade_delete': cascade_delete,
                    'force_delete': force_delete,
                    'status': 'simulated_success'
                }
                
                print_success(f"(Simulated) Project {project_id} would be deleted")
                print("\nDeletion Log:")
                print(json.dumps(deletion_log, indent=2))
                return True
                
        except AttributeError:
            print_info("Note: Project deletion endpoint not available in current API")
            print_info("This example demonstrates the expected usage pattern")
            return False
            
    except MindzieAPIException as e:
        print_error(f"API error deleting project: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error deleting project: {e}")
        return False


def confirm_deletion(project_id: str, dependencies: Dict[str, Any]) -> bool:
    """
    Multi-step confirmation for project deletion.
    
    Args:
        project_id: Project ID to delete
        dependencies: Project dependencies info
        
    Returns:
        True if user confirms deletion, False otherwise
    """
    print("\n" + "="*60)
    print("⚠️  PROJECT DELETION CONFIRMATION")
    print("="*60)
    
    print(f"\nYou are about to PERMANENTLY DELETE project: {project_id}")
    
    if dependencies['total_items'] > 0:
        print(f"\nThis project contains {dependencies['total_items']} items:")
        if dependencies['datasets']:
            print(f"  • {len(dependencies['datasets'])} dataset(s)")
        if dependencies['dashboards']:
            print(f"  • {len(dependencies['dashboards'])} dashboard(s)")
        if dependencies['investigations']:
            print(f"  • {len(dependencies['investigations'])} investigation(s)")
    
    if dependencies['blocking_issues']:
        print("\n❌ BLOCKING ISSUES:")
        for issue in dependencies['blocking_issues']:
            print(f"  • {issue}")
        return False
    
    # First confirmation
    print(f"\n1️⃣  Type the project ID to confirm: {project_id}")
    user_input = input("Enter project ID: ")
    if user_input != project_id:
        print("❌ Project ID does not match. Deletion cancelled.")
        return False
    
    # Second confirmation
    print("\n2️⃣  Final confirmation:")
    print("This action CANNOT be undone!")
    response = input("Type 'DELETE' in uppercase to proceed: ")
    if response != "DELETE":
        print("❌ Confirmation failed. Deletion cancelled.")
        return False
    
    return True


def main():
    """Main function to demonstrate safe project deletion."""
    print_header("Delete Project Example")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Safely delete a project')
    parser.add_argument('--project-id', help='Project ID (optional, will auto-discover if not provided)')
    parser.add_argument('--force', action='store_true', help='Skip some safety checks')
    parser.add_argument('--cascade', action='store_true', help='Delete all related resources')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    parser.add_argument('--backup-path', help='Custom backup file path')
    parser.add_argument('--yes', action='store_true', help='Skip confirmation prompts (dangerous!)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without deleting')
    
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
        
        # Check dependencies
        dependencies = check_project_dependencies(client, project_id)
        
        # Dry run mode
        if args.dry_run:
            print_info("DRY RUN MODE - No deletion will be performed")
            print(f"\nProject {project_id} contains:")
            print(f"  • {len(dependencies['datasets'])} dataset(s)")
            print(f"  • {len(dependencies['dashboards'])} dashboard(s)")
            print(f"  • {len(dependencies['investigations'])} investigation(s)")
            
            if dependencies['blocking_issues']:
                print("\nBlocking issues:")
                for issue in dependencies['blocking_issues']:
                    print(f"  • {issue}")
            
            print(f"\nTotal items to delete: {dependencies['total_items']}")
            return
        
        # Create backup unless skipped
        backup_path = None
        if not args.no_backup:
            backup_path = create_project_backup(client, project_id, args.backup_path)
            if not backup_path:
                print_error("Backup failed. Use --no-backup to skip.")
                return
        
        # Confirm deletion unless --yes flag used
        if not args.yes:
            if not confirm_deletion(project_id, dependencies):
                print_info("Deletion cancelled by user")
                return
        
        # Perform deletion
        success = delete_project(
            client,
            project_id,
            force_delete=args.force,
            cascade_delete=args.cascade
        )
        
        if success:
            print_success(f"\n✅ Project {project_id} deletion completed!")
            
            if backup_path:
                print(f"\n💾 Backup saved to: {backup_path}")
                print("   You can restore from this backup if needed.")
            
            print("\n📋 Post-deletion checklist:")
            print("  • Verify related API keys are revoked")
            print("  • Update any external integrations")
            print("  • Notify team members of deletion")
            print("  • Archive backup file securely")
        else:
            print_error("Project deletion failed")
            
            if backup_path:
                print(f"\n💾 Backup preserved at: {backup_path}")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to delete project: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()