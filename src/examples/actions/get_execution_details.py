#!/usr/bin/env python
"""
Get detailed execution information for a specific execution ID.

This example demonstrates how to retrieve comprehensive details about
a specific action execution using its execution ID.
"""

import os
import sys
import json
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

def get_execution_details(client, project_id: str, execution_id: str):
    """Get detailed information for a specific execution."""
    print_section(f"Getting Execution Details for: {execution_id}")
    
    try:
        execution_details = client.action_executions.get_by_id(project_id, execution_id)
        
        if execution_details:
            print_success("✓ Found execution details")
            return execution_details
        else:
            print_error("No execution found with that ID")
            return None
            
    except Exception as e:
        print_error(f"Failed to get execution details: {e}")
        return None

def analyze_execution_timeline(execution):
    """Analyze execution timeline and performance."""
    print_section("Execution Timeline Analysis")
    
    # Extract timestamp fields
    timestamp_fields = [
        ('createdAt', 'Created'),
        ('startTime', 'Started'),
        ('endTime', 'Ended'),
        ('completedAt', 'Completed'),
        ('lastUpdated', 'Last Updated'),
        ('submittedAt', 'Submitted')
    ]
    
    timestamps = {}
    for field, label in timestamp_fields:
        if field in execution and execution[field]:
            try:
                ts = datetime.fromisoformat(execution[field].replace('Z', '+00:00'))
                timestamps[label] = ts
                print(f"{label}: {ts.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            except Exception as e:
                print_info(f"{label}: {execution[field]} (could not parse)")
    
    # Calculate durations
    if len(timestamps) >= 2:
        print("\nDuration Analysis:")
        
        if 'Created' in timestamps and 'Started' in timestamps:
            queue_time = (timestamps['Started'] - timestamps['Created']).total_seconds()
            print(f"Queue time: {queue_time:.2f} seconds")
        
        if 'Started' in timestamps and 'Ended' in timestamps:
            execution_time = (timestamps['Ended'] - timestamps['Started']).total_seconds()
            print(f"Execution time: {execution_time:.2f} seconds")
        
        if 'Created' in timestamps and 'Completed' in timestamps:
            total_time = (timestamps['Completed'] - timestamps['Created']).total_seconds()
            print(f"Total time: {total_time:.2f} seconds")

def analyze_execution_results(execution):
    """Analyze execution results and outputs."""
    print_section("Execution Results Analysis")
    
    status = execution.get('status', 'Unknown')
    print(f"Final Status: {status}")
    
    # Check for success indicators
    if status.lower() in ['completed', 'finished', 'success']:
        print_success("✓ Execution completed successfully")
        
        # Look for result data
        result_fields = ['result', 'output', 'resultData', 'executionResult', 'returnValue']
        for field in result_fields:
            if field in execution and execution[field]:
                result_data = execution[field]
                print(f"\n{field}:")
                
                # Try to pretty-print JSON if it's a dict/list
                if isinstance(result_data, (dict, list)):
                    try:
                        print(json.dumps(result_data, indent=2))
                    except:
                        print(str(result_data))
                else:
                    # Truncate very long strings
                    str_result = str(result_data)
                    if len(str_result) > 500:
                        print(str_result[:500] + "... [truncated]")
                    else:
                        print(str_result)
    
    elif status.lower() in ['failed', 'error', 'cancelled']:
        print_error("✗ Execution failed")
        
        # Look for error information
        error_fields = ['error', 'errorMessage', 'exception', 'failureReason', 'message']
        for field in error_fields:
            if field in execution and execution[field]:
                print_error(f"{field}: {execution[field]}")
    
    else:
        print_info(f"Status: {status}")

def analyze_resource_usage(execution):
    """Analyze resource usage if available."""
    print_section("Resource Usage Analysis")
    
    resource_fields = [
        ('cpuUsage', 'CPU Usage'),
        ('memoryUsage', 'Memory Usage'),
        ('diskUsage', 'Disk Usage'),
        ('networkUsage', 'Network Usage'),
        ('maxMemory', 'Peak Memory'),
        ('avgCpu', 'Average CPU'),
        ('resourceUsage', 'Resource Usage')
    ]
    
    found_resources = False
    for field, label in resource_fields:
        if field in execution and execution[field] is not None:
            found_resources = True
            print(f"{label}: {execution[field]}")
    
    if not found_resources:
        print_info("No resource usage data available")

def display_logs_and_output(execution):
    """Display logs and output information."""
    print_section("Logs and Output")
    
    log_fields = [
        ('logs', 'Execution Logs'),
        ('stdout', 'Standard Output'),
        ('stderr', 'Standard Error'),
        ('debugInfo', 'Debug Information'),
        ('trace', 'Execution Trace')
    ]
    
    found_logs = False
    for field, label in log_fields:
        if field in execution and execution[field]:
            found_logs = True
            log_data = execution[field]
            
            print(f"\n{label}:")
            print("-" * 40)
            
            # Handle different log formats
            if isinstance(log_data, list):
                for i, log_entry in enumerate(log_data):
                    print(f"[{i+1}] {log_entry}")
            elif isinstance(log_data, str):
                # Truncate very long logs
                if len(log_data) > 1000:
                    print(log_data[:1000] + "... [truncated]")
                else:
                    print(log_data)
            else:
                print(str(log_data))
    
    if not found_logs:
        print_info("No log data available")

def display_metadata(execution):
    """Display execution metadata and configuration."""
    print_section("Execution Metadata")
    
    # Skip fields we've already covered
    covered_fields = {
        'id', 'status', 'result', 'output', 'resultData', 'executionResult',
        'error', 'errorMessage', 'logs', 'stdout', 'stderr', 'cpuUsage',
        'memoryUsage', 'createdAt', 'startTime', 'endTime', 'completedAt'
    }
    
    metadata = {k: v for k, v in execution.items() 
               if k not in covered_fields and not k.startswith('_')}
    
    if metadata:
        for key, value in metadata.items():
            # Handle different value types
            if isinstance(value, (dict, list)):
                try:
                    value_str = json.dumps(value, indent=2)
                    if len(value_str) > 200:
                        value_str = value_str[:200] + "... [truncated]"
                except:
                    value_str = str(value)[:200] + "... [truncated]" if len(str(value)) > 200 else str(value)
            else:
                value_str = str(value)
                if len(value_str) > 200:
                    value_str = value_str[:200] + "... [truncated]"
            
            print(f"{key}: {value_str}")
    else:
        print_info("No additional metadata available")

def main():
    """Main function to get and analyze execution details."""
    print("mindzie-api Execution Details Example")
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
        
        # Get execution ID from user
        print_section("Execution Selection")
        print_info("You need to provide an execution ID to get detailed information.")
        print_info("Execution IDs are GUIDs returned when actions are executed.")
        print_info("You can find these using get_action_executions.py or get_last_execution.py")
        
        try:
            execution_id = input("\nEnter the Execution ID: ").strip()
            if not execution_id:
                print_error("Execution ID is required.")
                return 1
        except KeyboardInterrupt:
            print_error("Cancelled.")
            return 1
        
        # Get execution details
        execution = get_execution_details(client, project_id, execution_id)
        
        if execution:
            # Perform various analyses
            analyze_execution_timeline(execution)
            analyze_execution_results(execution)
            analyze_resource_usage(execution)
            display_logs_and_output(execution)
            display_metadata(execution)
            
            print_section("Summary")
            print_success("✓ Successfully retrieved and analyzed execution details")
            print_info("Related commands:")
            print_info("• download_execution_package.py - Download execution results")
            print_info("• compare_executions.py - Compare with other executions")
        else:
            print_section("Summary")
            print_error("Could not retrieve execution details")
            print_info("Please verify the execution ID and try again")
    
    except Exception as e:
        handle_api_error(e, "getting execution details")
        return 1
    
    finally:
        client.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())