#!/usr/bin/env python
"""
Get the last execution for a specific action in mindzie Studio.

This example demonstrates how to retrieve the most recent execution
for an action and analyze its status and results.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

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

def get_last_execution(client, project_id: str, action_id: str):
    """Get the last execution for a specific action."""
    print_section(f"Getting Last Execution for Action: {action_id}")
    
    try:
        last_execution = client.action_executions.get_last(project_id, action_id)
        
        if last_execution:
            print_success("✓ Found last execution data")
            return last_execution
        else:
            print_info("No execution history found for this action")
            return None
            
    except Exception as e:
        print_error(f"Failed to get last execution: {e}")
        return None

def analyze_execution_status(execution):
    """Analyze the execution status and provide insights."""
    print_section("Execution Status Analysis")
    
    if not execution:
        print_info("No execution data to analyze")
        return
    
    # Get key status information
    status = execution.get('status', 'Unknown')
    progress = execution.get('progress', 'N/A')
    start_time = execution.get('startTime') or execution.get('createdAt')
    end_time = execution.get('endTime') or execution.get('completedAt')
    
    print(f"Status: {status}")
    print(f"Progress: {progress}")
    
    # Analyze status
    if status.lower() in ['completed', 'finished', 'success']:
        print_success("✓ Execution completed successfully")
    elif status.lower() in ['failed', 'error', 'cancelled']:
        print_error("✗ Execution failed or was cancelled")
        
        # Look for error information
        error_msg = execution.get('error') or execution.get('errorMessage') or execution.get('message')
        if error_msg:
            print_error(f"Error details: {error_msg}")
    elif status.lower() in ['running', 'in_progress', 'executing']:
        print_info("⚡ Execution is currently running")
    elif status.lower() in ['pending', 'queued', 'waiting']:
        print_info("⏳ Execution is pending/queued")
    else:
        print_info(f"? Unknown status: {status}")
    
    # Calculate duration if times are available
    if start_time and end_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration = (end_dt - start_dt).total_seconds()
            print(f"Execution duration: {duration:.2f} seconds")
        except Exception as e:
            print_info(f"Could not calculate duration: {e}")
    elif start_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            now = datetime.now(start_dt.tzinfo)
            running_time = (now - start_dt).total_seconds()
            print(f"Running time: {running_time:.2f} seconds")
        except Exception as e:
            print_info(f"Could not calculate running time: {e}")

def display_execution_details(execution):
    """Display detailed execution information."""
    print_section("Execution Details")
    
    if not execution:
        print_info("No execution details to display")
        return
    
    # Core execution fields
    core_fields = [
        'id', 'status', 'progress', 'startTime', 'endTime', 
        'createdAt', 'completedAt', 'message', 'error', 'errorMessage'
    ]
    
    print("Core Information:")
    for field in core_fields:
        if field in execution:
            value = execution[field]
            print(f"  {field}: {value}")
    
    # Results and output information
    result_fields = [
        'result', 'output', 'logs', 'packageUrl', 'downloadUrl',
        'resultData', 'executionResult'
    ]
    
    result_info = {k: v for k, v in execution.items() if k in result_fields}
    if result_info:
        print("\nResult Information:")
        for key, value in result_info.items():
            # Truncate long values for display
            str_value = str(value)
            if len(str_value) > 200:
                str_value = str_value[:200] + "... [truncated]"
            print(f"  {key}: {str_value}")
    
    # Performance and resource information
    perf_fields = [
        'cpuUsage', 'memoryUsage', 'duration', 'resourceUsage',
        'executionTime', 'processingTime'
    ]
    
    perf_info = {k: v for k, v in execution.items() if k in perf_fields}
    if perf_info:
        print("\nPerformance Information:")
        for key, value in perf_info.items():
            print(f"  {key}: {value}")
    
    # Any other fields
    displayed_fields = set(core_fields + result_fields + perf_fields)
    other_fields = {k: v for k, v in execution.items() 
                   if k not in displayed_fields and not k.startswith('_')}
    
    if other_fields:
        print("\nAdditional Information:")
        for key, value in other_fields.items():
            str_value = str(value)
            if len(str_value) > 100:
                str_value = str_value[:100] + "... [truncated]"
            print(f"  {key}: {str_value}")

def suggest_next_actions(execution):
    """Suggest next actions based on execution status."""
    print_section("Suggested Next Actions")
    
    if not execution:
        print_info("• Use execute_action.py to run this action")
        return
    
    status = execution.get('status', '').lower()
    execution_id = execution.get('id')
    
    if status in ['completed', 'finished', 'success']:
        print_info("• Use download_execution_package.py to download results")
        if execution_id:
            print_info(f"• Use get_execution_details.py with execution ID: {execution_id}")
        print_info("• Compare with previous executions using compare_executions.py")
        
    elif status in ['failed', 'error', 'cancelled']:
        print_info("• Check error details above")
        print_info("• Review action configuration in mindzieStudio")
        print_info("• Try re-executing the action with execute_action.py")
        
    elif status in ['running', 'in_progress', 'executing']:
        print_info("• Use monitor_action_execution.py to watch progress")
        if execution_id:
            print_info(f"• Monitor execution ID: {execution_id}")
            
    elif status in ['pending', 'queued', 'waiting']:
        print_info("• Wait for execution to start")
        print_info("• Use monitor_action_execution.py to watch for status changes")
        
    else:
        print_info("• Use get_action_executions.py to see full execution history")
        print_info("• Check action status in mindzieStudio")

def main():
    """Main function to get and analyze the last execution."""
    print("mindzie-api Last Action Execution Example")
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
        print_info("You need to provide an action ID to get the last execution.")
        print_info("Action IDs are GUIDs that identify specific actions in your project.")
        
        try:
            action_id = input("\nEnter the Action ID: ").strip()
            if not action_id:
                print_error("Action ID is required.")
                return 1
        except KeyboardInterrupt:
            print_error("Cancelled.")
            return 1
        
        # Get the last execution
        last_execution = get_last_execution(client, project_id, action_id)
        
        if last_execution:
            # Analyze the execution
            analyze_execution_status(last_execution)
            
            # Display detailed information
            display_execution_details(last_execution)
            
            # Suggest next actions
            suggest_next_actions(last_execution)
            
            print_section("Summary")
            print_success("✓ Successfully retrieved last execution details")
        else:
            print_section("Summary")
            print_info("No execution history found for this action")
            suggest_next_actions(None)
    
    except Exception as e:
        handle_api_error(e, "getting last execution")
        return 1
    
    finally:
        client.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())