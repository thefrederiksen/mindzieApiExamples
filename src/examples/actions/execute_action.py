#!/usr/bin/env python
"""
Execute actions in mindzie Studio projects.

This example demonstrates how to execute actions and retrieve the results.
It shows basic action execution and error handling.
"""

import os
import sys
import time
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
sys.path.append(str(Path(__file__).parent.parent))
from common_utils import create_client, handle_api_error, print_section, print_success, print_error, print_info

def get_project_actions(client, project_id: str):
    """Get available actions for a project (placeholder - would need actual API endpoint)."""
    print_info("Note: This example assumes you know the action ID.")
    print_info("In a real scenario, you would first list available actions.")
    print_info("For now, please provide an action ID when prompted.")
    return []

def execute_action_with_monitoring(client, project_id: str, action_id: str):
    """Execute an action and monitor its progress."""
    print_section(f"Executing Action: {action_id}")
    
    try:
        # Execute the action
        print_info(f"Executing action {action_id} in project {project_id}...")
        execution_result = client.actions.execute(project_id, action_id)
        
        print_success("✓ Action execution request submitted successfully!")
        print(f"Execution result: {execution_result}")
        
        # If the action returns an execution ID, we can monitor it
        if isinstance(execution_result, dict) and 'executionId' in execution_result:
            execution_id = execution_result['executionId']
            print_info(f"Got execution ID: {execution_id}")
            
            # Monitor the execution
            print_section("Monitoring Execution Progress")
            return monitor_execution(client, project_id, execution_id)
        else:
            print_info("Action completed synchronously or no execution ID returned.")
            return execution_result
            
    except Exception as e:
        print_error(f"Failed to execute action: {e}")
        return None

def monitor_execution(client, project_id: str, execution_id: str, max_wait_time: int = 300):
    """Monitor an action execution until completion."""
    start_time = time.time()
    check_interval = 5  # Check every 5 seconds
    
    while time.time() - start_time < max_wait_time:
        try:
            # Get execution details
            execution_details = client.action_executions.get_by_id(project_id, execution_id)
            
            if execution_details:
                status = execution_details.get('status', 'Unknown')
                progress = execution_details.get('progress', 'N/A')
                
                print_info(f"Status: {status}, Progress: {progress}")
                
                # Check if execution is complete
                if status.lower() in ['completed', 'finished', 'success', 'failed', 'error']:
                    if status.lower() in ['completed', 'finished', 'success']:
                        print_success(f"✓ Execution completed successfully! Final status: {status}")
                    else:
                        print_error(f"✗ Execution failed with status: {status}")
                    
                    return execution_details
                
                # Wait before next check
                time.sleep(check_interval)
            else:
                print_error("Failed to get execution details")
                break
                
        except Exception as e:
            print_error(f"Error monitoring execution: {e}")
            break
    
    print_error(f"Execution monitoring timed out after {max_wait_time} seconds")
    return None

def main():
    """Main function to demonstrate action execution."""
    print("mindzie-api Action Execution Example")
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
        
        # Get action ID from user
        print_section("Action Selection")
        print_info("You need to provide an action ID to execute.")
        print_info("Action IDs are GUIDs that identify specific actions in your project.")
        print_info("You can find these in mindzieStudio under your project's Actions section.")
        
        try:
            action_id = input("\nEnter the Action ID to execute: ").strip()
            if not action_id:
                print_error("Action ID is required.")
                return 1
        except KeyboardInterrupt:
            print_error("Cancelled.")
            return 1
        
        # Execute the action
        result = execute_action_with_monitoring(client, project_id, action_id)
        
        if result:
            print_section("Execution Summary")
            print_success("Action execution completed!")
            print("Final result details:")
            
            # Pretty print the result
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  Result: {result}")
        else:
            print_section("Execution Summary")
            print_error("Action execution failed or was incomplete.")
            return 1
    
    except Exception as e:
        handle_api_error(e, "action execution")
        return 1
    
    finally:
        client.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())