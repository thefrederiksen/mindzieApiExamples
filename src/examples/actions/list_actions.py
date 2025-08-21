#!/usr/bin/env python
"""
List and explore actions in mindzie Studio projects.

This example demonstrates how to work with project actions, though note that
the current ActionController API primarily focuses on execution rather than listing.
This serves as a template for when action listing endpoints become available.
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
from common_utils import create_client, handle_api_error, print_section, print_success, print_error, print_info

def test_action_endpoints(client, project_id: str):
    """Test available action endpoints to understand what actions exist."""
    print_section("Testing Action Endpoints")
    
    # Test connectivity first
    try:
        ping_result = client.actions.ping(project_id)
        print_success(f"✓ Action controller is accessible: {ping_result}")
    except Exception as e:
        print_error(f"✗ Cannot access action controller: {e}")
        return False
    
    return True

def demonstrate_action_workflow(client, project_id: str):
    """Demonstrate the typical action workflow."""
    print_section("Action Workflow Information")
    
    print_info("Current ActionController API provides:")
    print("  • ping_unauthorized(project_id) - Test unauthenticated connectivity")
    print("  • ping(project_id) - Test authenticated connectivity")
    print("  • execute(project_id, action_id) - Execute a specific action")
    
    print_info("\nTo use actions, you typically need to:")
    print("  1. Know the action ID (GUID) from mindzieStudio")
    print("  2. Use execute() to run the action")
    print("  3. Monitor execution status using ActionExecutionController")
    
    print_info("\nNote: Action listing/discovery endpoints may be added in future API versions.")

def show_project_context(client, project_id: str):
    """Show project context for understanding actions."""
    print_section("Project Context")
    
    try:
        # Get project details
        projects_response = client.projects.get_projects()
        projects = projects_response.get('projects', [])
        
        current_project = None
        for project in projects:
            if project['id'] == project_id:
                current_project = project
                break
        
        if current_project:
            print_success(f"Project: {current_project.get('name', 'Unknown')}")
            print(f"  ID: {current_project['id']}")
            print(f"  Description: {current_project.get('description', 'No description')}")
            
            # Show any other relevant project info
            for key, value in current_project.items():
                if key not in ['id', 'name', 'description']:
                    print(f"  {key}: {value}")
        else:
            print_error("Could not find project details")
            
    except Exception as e:
        print_error(f"Error getting project details: {e}")

def provide_action_guidance(client, project_id: str):
    """Provide guidance on finding and using actions."""
    print_section("Finding Actions in mindzieStudio")
    
    print_info("To find action IDs for use with this API:")
    print("  1. Open mindzieStudio in your web browser")
    print("  2. Navigate to your project")
    print("  3. Go to the Actions section")
    print("  4. Note the action IDs (GUIDs) for actions you want to execute")
    
    print_info("\nAction IDs are typically in GUID format, like:")
    print("  'a1b2c3d4-e5f6-7890-abcd-ef1234567890'")
    
    print_info("\nOnce you have an action ID, you can:")
    print("  • Use execute_action.py to run it")
    print("  • Use get_action_executions.py to see execution history")
    print("  • Use monitor_action_execution.py to watch progress")

def main():
    """Main function to demonstrate action listing concepts."""
    print("mindzie-api Action Listing Example")
    print("=" * 50)
    
    # Create client
    client = create_client()
    if not client:
        return 1
    
    try:
        # Get available projects
        print_section("Getting Available Projects")
        projects_response = client.projects.get_projects()
        projects = projects_response.get('projects', [])
        
        if not projects:
            print_error("No projects found. Please create a project first.")
            return 1
        
        # Show available projects
        print("Available projects:")
        for i, project in enumerate(projects):
            print(f"  {i+1}. {project.get('name', 'Unknown')} (ID: {project['id']})")
        
        # Get user's project choice
        if len(projects) == 1:
            selected_project = projects[0]
            print_info(f"Using only available project: {selected_project.get('name', 'Unknown')}")
        else:
            try:
                choice = input(f"\nSelect a project (1-{len(projects)}): ").strip()
                project_index = int(choice) - 1
                if 0 <= project_index < len(projects):
                    selected_project = projects[project_index]
                else:
                    print_error("Invalid project selection.")
                    return 1
            except (ValueError, KeyboardInterrupt):
                print_error("Invalid input or cancelled.")
                return 1
        
        project_id = selected_project['id']
        project_name = selected_project.get('name', 'Unknown')
        
        print_success(f"Selected project: {project_name} (ID: {project_id})")
        
        # Test action endpoints
        if not test_action_endpoints(client, project_id):
            return 1
        
        # Show project context
        show_project_context(client, project_id)
        
        # Demonstrate workflow
        demonstrate_action_workflow(client, project_id)
        
        # Provide guidance
        provide_action_guidance(client, project_id)
        
        print_section("Summary")
        print_success("✓ Action endpoints are accessible for this project")
        print_info("Use other examples in this directory to execute and monitor actions:")
        print("  • execute_action.py - Execute a specific action")
        print("  • get_action_executions.py - View execution history")
        print("  • monitor_action_execution.py - Monitor execution progress")
    
    except Exception as e:
        handle_api_error(e, "action listing")
        return 1
    
    finally:
        client.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())