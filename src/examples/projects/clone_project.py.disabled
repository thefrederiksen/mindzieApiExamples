"""
Clone an existing project with optional modifications.

This example demonstrates how to:
- Clone a project's structure and configuration
- Modify cloned project settings during creation
- Handle data copying options (copy, reference, or exclude)
- Customize permissions and access control for cloned project
- Validate and resolve naming conflicts

NOTE: This example assumes the clone() method exists in the projects controller.
If the API doesn't support project cloning, this serves as a template for when it's added.
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import json
import re

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


def generate_clone_name(original_name: str, suffix: Optional[str] = None) -> str:
    """
    Generate a name for the cloned project.
    
    Args:
        original_name: Name of the original project
        suffix: Optional suffix to add
        
    Returns:
        Generated name for the clone
    """
    if suffix:
        return f"{original_name} - {suffix}"
    
    # Check if name already has a clone pattern
    clone_pattern = r'(.+) - Copy( \((\d+)\))?$'
    match = re.match(clone_pattern, original_name)
    
    if match:
        base_name = match.group(1)
        existing_number = match.group(3)
        if existing_number:
            new_number = int(existing_number) + 1
            return f"{base_name} - Copy ({new_number})"
        else:
            return f"{base_name} - Copy (2)"
    else:
        return f"{original_name} - Copy"


def clone_project(
    client: MindzieAPIClient,
    source_project_id: str,
    clone_name: Optional[str] = None,
    clone_options: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Clone an existing project.
    
    Args:
        client: The mindzie API client
        source_project_id: ID of the project to clone
        clone_name: Name for the cloned project
        clone_options: Options for cloning (data, settings, etc.)
        
    Returns:
        Dictionary containing cloned project information or None if error
    """
    try:
        print_info(f"Cloning project {source_project_id}")
        
        # Get source project details
        source_project = None
        try:
            if hasattr(client.projects, 'get_by_id'):
                source_project = client.projects.get_by_id(source_project_id)
                print_success("Retrieved source project details")
        except Exception as e:
            print_info(f"Could not retrieve source project: {e}")
        
        # Generate clone name if not provided
        if not clone_name:
            if source_project and source_project.get('project_name'):
                clone_name = generate_clone_name(source_project['project_name'])
            else:
                clone_name = f"Clone of {source_project_id}"
        
        print_info(f"Clone name: {clone_name}")
        
        # Prepare clone configuration
        default_options = {
            "copy_datasets": True,
            "copy_dashboards": True,
            "copy_investigations": False,  # Usually don't copy investigations
            "copy_data": False,  # Copy structure but not actual data by default
            "copy_permissions": False,  # Start with fresh permissions
            "copy_settings": True,
            "preserve_connections": False  # Create new connections to avoid conflicts
        }
        
        final_options = {**default_options, **(clone_options or {})}
        
        print_info("Clone options:")
        for key, value in final_options.items():
            print(f"  • {key}: {value}")
        
        clone_config = {
            "source_project_id": source_project_id,
            "clone_name": clone_name,
            "cloned_at": datetime.now().isoformat(),
            "cloned_by": "api_user",
            "clone_options": final_options
        }
        
        # Attempt to clone
        try:
            if hasattr(client.projects, 'clone'):
                response = client.projects.clone(**clone_config)
                print_success(f"Project cloned successfully!")
                
                if response:
                    print("\nCloned Project Details:")
                    print(f"  • New Project ID: {response.get('project_id', 'N/A')}")
                    print(f"  • Clone Name: {response.get('project_name', clone_name)}")
                    print(f"  • Status: {response.get('status', 'Active')}")
                    print(f"  • Created At: {response.get('created_at', 'N/A')}")
                    
                    if response.get('clone_summary'):
                        summary = response['clone_summary']
                        print("\n  Clone Summary:")
                        print(f"    - Datasets copied: {summary.get('datasets_copied', 0)}")
                        print(f"    - Dashboards copied: {summary.get('dashboards_copied', 0)}")
                        print(f"    - Settings copied: {summary.get('settings_copied', 0)}")
                
                return response
            else:
                # Simulate cloning
                print_info("Note: clone() method not found in projects controller")
                print_info("Simulating project cloning for demonstration...")
                
                # Simulate clone summary
                simulated_summary = {
                    "datasets_copied": 3 if final_options.get('copy_datasets') else 0,
                    "dashboards_copied": 2 if final_options.get('copy_dashboards') else 0,
                    "investigations_copied": 0,
                    "settings_copied": 5 if final_options.get('copy_settings') else 0
                }
                
                simulated_response = {
                    "project_id": f"proj_clone_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "project_name": clone_name,
                    "source_project_id": source_project_id,
                    "status": "Active",
                    "created_at": datetime.now().isoformat(),
                    "clone_summary": simulated_summary,
                    **clone_config
                }
                
                print_success(f"(Simulated) Project would be cloned as '{clone_name}'")
                print("\nSimulated Clone Details:")
                print(json.dumps(simulated_response, indent=2, default=str))
                
                return simulated_response
                
        except AttributeError:
            print_info("Note: Project cloning endpoint not available in current API")
            print_info("This example demonstrates the expected usage pattern")
            return None
            
    except MindzieAPIException as e:
        if "not found" in str(e).lower():
            print_error(f"Source project {source_project_id} not found")
        else:
            print_error(f"API error cloning project: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error cloning project: {e}")
        return None


def validate_clone_options(options: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate clone options and return warnings if any.
    
    Args:
        options: Clone options to validate
        
    Returns:
        Dictionary of validation warnings
    """
    warnings = {}
    
    # Check for potentially expensive operations
    if options.get('copy_data') and options.get('copy_datasets'):
        warnings['data_copy'] = "Copying both dataset structure AND data may be slow for large datasets"
    
    # Check for security implications
    if options.get('copy_permissions'):
        warnings['permissions'] = "Copying permissions may grant unintended access to the cloned project"
    
    # Check for connection conflicts
    if options.get('preserve_connections'):
        warnings['connections'] = "Preserving connections may cause conflicts if external systems don't support multiple connections"
    
    return warnings


def main():
    """Main function to demonstrate project cloning."""
    print_header("Clone Project Example")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Clone an existing project')
    parser.add_argument('--source-project-id', help='Source project ID (optional, will auto-discover if not provided)')
    parser.add_argument('--clone-name', help='Name for the cloned project')
    
    # Clone options
    parser.add_argument('--copy-datasets', action='store_true', default=True, help='Copy dataset structures')
    parser.add_argument('--no-copy-datasets', action='store_true', help='Skip copying datasets')
    parser.add_argument('--copy-dashboards', action='store_true', default=True, help='Copy dashboards')
    parser.add_argument('--no-copy-dashboards', action='store_true', help='Skip copying dashboards')
    parser.add_argument('--copy-data', action='store_true', help='Copy actual data (slow for large datasets)')
    parser.add_argument('--copy-permissions', action='store_true', help='Copy user permissions')
    parser.add_argument('--copy-investigations', action='store_true', help='Copy investigations')
    parser.add_argument('--preserve-connections', action='store_true', help='Keep original external connections')
    
    parser.add_argument('--suffix', help='Suffix to add to clone name instead of "Copy"')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be cloned without cloning')
    
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
        
        # Get or discover source project ID
        if args.source_project_id:
            source_project_id = args.source_project_id
            print_info(f"Using provided source project ID: {source_project_id}")
        else:
            source_project_id = discover_project(client)
            if not source_project_id:
                print_error("No projects available to clone")
                return
        
        # Build clone options
        clone_options = {
            "copy_datasets": args.copy_datasets and not args.no_copy_datasets,
            "copy_dashboards": args.copy_dashboards and not args.no_copy_dashboards,
            "copy_investigations": args.copy_investigations,
            "copy_data": args.copy_data,
            "copy_permissions": args.copy_permissions,
            "preserve_connections": args.preserve_connections
        }
        
        # Validate options and show warnings
        warnings = validate_clone_options(clone_options)
        if warnings:
            print_info("\n⚠️  Clone Option Warnings:")
            for warning_type, message in warnings.items():
                print(f"  • {message}")
        
        # Generate clone name
        clone_name = args.clone_name
        if not clone_name:
            # Get source project name to generate clone name
            try:
                if hasattr(client.projects, 'get_by_id'):
                    source_project = client.projects.get_by_id(source_project_id)
                    if source_project and source_project.get('project_name'):
                        clone_name = generate_clone_name(source_project['project_name'], args.suffix)
            except:
                pass
            
            if not clone_name:
                clone_name = f"Clone of {source_project_id}"
                if args.suffix:
                    clone_name = f"Clone of {source_project_id} - {args.suffix}"
        
        # Dry run mode
        if args.dry_run:
            print_info("DRY RUN MODE - No cloning will be performed")
            print(f"\nSource Project: {source_project_id}")
            print(f"Clone Name: {clone_name}")
            print("\nClone Options:")
            for key, value in clone_options.items():
                print(f"  • {key}: {value}")
            return
        
        # Perform the clone
        result = clone_project(
            client,
            source_project_id,
            clone_name=clone_name,
            clone_options=clone_options
        )
        
        if result:
            print_success(f"\n✅ Project cloning completed!")
            
            print("\n📋 Clone Summary:")
            print(f"  • Source: {source_project_id}")
            print(f"  • Clone: {result.get('project_id', 'N/A')}")
            print(f"  • Name: {clone_name}")
            
            if result.get('clone_summary'):
                summary = result['clone_summary']
                print("\n📋 Resources Cloned:")
                for resource_type, count in summary.items():
                    if count > 0:
                        print(f"  • {resource_type.replace('_', ' ').title()}: {count}")
            
            print("\n📝 Next Steps:")
            print("1. Review cloned project settings")
            print("2. Update any external connections if needed")
            print("3. Configure permissions and access control")
            print("4. Test dashboards and data connections")
            print("5. Rename or reorganize as needed")
        else:
            print_info("\nNote: Project cloning may not be available in the current API version")
            print_info("This example demonstrates the expected usage pattern for future implementation")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to clone project: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()