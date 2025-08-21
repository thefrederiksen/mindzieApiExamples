#!/usr/bin/env python
"""
Get action execution history for mindzie Studio actions.

This example demonstrates how to retrieve execution history for actions,
including filtering and analysis of execution data.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

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

def get_executions_for_action(client, project_id: str, action_id: str):
    """Get all executions for a specific action."""
    print_section(f"Getting Executions for Action: {action_id}")
    
    try:
        executions = client.action_executions.get_by_action(project_id, action_id)
        
        if executions:
            print_success(f"✓ Found execution data for action {action_id}")
            return executions
        else:
            print_info("No executions found for this action")
            return None
            
    except Exception as e:
        print_error(f"Failed to get executions: {e}")
        return None

def analyze_execution_data(executions):
    """Analyze execution data and provide insights."""
    print_section("Execution Analysis")
    
    if not executions:
        print_info("No execution data to analyze")
        return
    
    # Handle different response formats
    execution_list = executions
    if isinstance(executions, dict):
        execution_list = executions.get('executions', executions.get('data', [executions]))
    
    if not isinstance(execution_list, list):
        execution_list = [execution_list]
    
    total_executions = len(execution_list)
    print_info(f"Total executions found: {total_executions}")
    
    if total_executions == 0:
        return
    
    # Analyze execution statuses
    status_counts = {}
    execution_times = []
    
    for execution in execution_list:
        # Count statuses
        status = execution.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Collect execution times if available
        start_time = execution.get('startTime') or execution.get('createdAt')
        end_time = execution.get('endTime') or execution.get('completedAt')
        
        if start_time and end_time:
            try:
                # Try to parse timestamps (format may vary)
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration = (end_dt - start_dt).total_seconds()
                execution_times.append(duration)
            except:
                pass  # Skip if timestamp parsing fails
    
    # Print status summary
    print("\nExecution Status Summary:")
    for status, count in status_counts.items():
        percentage = (count / total_executions) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    # Print timing analysis
    if execution_times:
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        print(f"\nExecution Time Analysis:")
        print(f"  Average duration: {avg_time:.2f} seconds")
        print(f"  Fastest execution: {min_time:.2f} seconds")
        print(f"  Slowest execution: {max_time:.2f} seconds")

def display_execution_details(executions, limit: int = 5):
    """Display detailed information for recent executions."""
    print_section(f"Recent Execution Details (showing up to {limit})")
    
    if not executions:
        print_info("No executions to display")
        return
    
    # Handle different response formats
    execution_list = executions
    if isinstance(executions, dict):
        execution_list = executions.get('executions', executions.get('data', [executions]))
    
    if not isinstance(execution_list, list):
        execution_list = [execution_list]
    
    # Sort by timestamp if available (most recent first)
    def get_timestamp(execution):
        return execution.get('startTime') or execution.get('createdAt') or ''
    
    try:
        execution_list = sorted(execution_list, key=get_timestamp, reverse=True)
    except:
        pass  # Use original order if sorting fails
    
    # Display up to 'limit' executions
    for i, execution in enumerate(execution_list[:limit]):
        print(f"\nExecution {i+1}:")
        
        # Display key fields
        key_fields = ['id', 'status', 'startTime', 'endTime', 'createdAt', 'completedAt', 'progress', 'message', 'error']
        
        for field in key_fields:
            if field in execution:
                value = execution[field]
                print(f"  {field}: {value}")
        
        # Display any other interesting fields
        other_fields = {k: v for k, v in execution.items() if k not in key_fields and not k.startswith('_')}
        if other_fields:
            print("  Other fields:")
            for key, value in other_fields.items():
                # Truncate long values
                str_value = str(value)
                if len(str_value) > 100:
                    str_value = str_value[:100] + "..."
                print(f"    {key}: {str_value}")

def main():
    """Main function to get and analyze action executions."""
    print("mindzie-api Action Executions Example")
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
        print_info("You need to provide an action ID to get execution history.")
        print_info("Action IDs are GUIDs that identify specific actions in your project.")
        
        try:
            action_id = input("\nEnter the Action ID: ").strip()
            if not action_id:
                print_error("Action ID is required.")
                return 1
        except KeyboardInterrupt:
            print_error("Cancelled.")
            return 1
        
        # Get executions for the action
        executions = get_executions_for_action(client, project_id, action_id)
        
        if executions:
            # Analyze the execution data
            analyze_execution_data(executions)
            
            # Display detailed information
            display_execution_details(executions)
            
            print_section("Summary")
            print_success("✓ Successfully retrieved and analyzed action execution history")
            print_info("Use get_execution_details.py to get more details about specific executions")
            print_info("Use monitor_action_execution.py to watch real-time execution progress")
        else:
            print_section("Summary")
            print_info("No execution history found for this action")
            print_info("Try executing the action first using execute_action.py")
    
    except Exception as e:
        handle_api_error(e, "getting action executions")
        return 1
    
    finally:
        client.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())