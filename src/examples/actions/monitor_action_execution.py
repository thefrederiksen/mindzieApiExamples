#!/usr/bin/env python
"""
Monitor action execution progress in real-time.

This example demonstrates how to monitor a running action execution,
polling for status updates and displaying progress information.
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

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

class ExecutionMonitor:
    """Class to monitor action execution progress."""
    
    def __init__(self, client, project_id: str, execution_id: str):
        self.client = client
        self.project_id = project_id
        self.execution_id = execution_id
        self.start_time = datetime.now()
        self.last_status = None
        self.last_progress = None
        self.status_history = []
    
    def get_current_status(self):
        """Get current execution status."""
        try:
            execution = self.client.action_executions.get_by_id(self.project_id, self.execution_id)
            if execution:
                status = execution.get('status', 'Unknown')
                progress = execution.get('progress', 'N/A')
                return execution, status, progress
            return None, 'Not Found', 'N/A'
        except Exception as e:
            return None, f'Error: {e}', 'N/A'
    
    def is_terminal_status(self, status: str) -> bool:
        """Check if status indicates execution is finished."""
        terminal_statuses = [
            'completed', 'finished', 'success', 'failed', 
            'error', 'cancelled', 'aborted', 'timeout'
        ]
        return status.lower() in terminal_statuses
    
    def format_duration(self, seconds: float) -> str:
        """Format duration in a human-readable way."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    def display_status_update(self, execution, status: str, progress, elapsed_time: float):
        """Display a status update."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        duration_str = self.format_duration(elapsed_time)
        
        print(f"[{timestamp}] Status: {status} | Progress: {progress} | Elapsed: {duration_str}")
        
        # Show additional info if status changed
        if status != self.last_status:
            print_info(f"Status changed: {self.last_status} → {status}")
            
            # Record status change
            self.status_history.append({
                'timestamp': datetime.now(),
                'status': status,
                'progress': progress,
                'elapsed': elapsed_time
            })
        
        # Show progress change
        elif progress != self.last_progress and progress != 'N/A':
            print_info(f"Progress updated: {self.last_progress} → {progress}")
        
        self.last_status = status
        self.last_progress = progress
    
    def monitor(self, check_interval: int = 5, max_duration: int = 1800, show_details: bool = False):
        """Monitor execution until completion or timeout."""
        print_section(f"Monitoring Execution: {self.execution_id}")
        print_info(f"Check interval: {check_interval} seconds")
        print_info(f"Maximum duration: {max_duration} seconds ({max_duration/60:.0f} minutes)")
        print_info("Press Ctrl+C to stop monitoring")
        print("-" * 60)
        
        try:
            while True:
                current_time = datetime.now()
                elapsed_time = (current_time - self.start_time).total_seconds()
                
                # Check for timeout
                if elapsed_time > max_duration:
                    print_error(f"\nMonitoring timed out after {max_duration} seconds")
                    break
                
                # Get current status
                execution, status, progress = self.get_current_status()
                
                # Display update
                self.display_status_update(execution, status, progress, elapsed_time)
                
                # Show additional details if requested
                if show_details and execution:
                    self.show_execution_details(execution)
                
                # Check if execution is finished
                if self.is_terminal_status(status):
                    if status.lower() in ['completed', 'finished', 'success']:
                        print_success(f"\n✓ Execution completed successfully!")
                    else:
                        print_error(f"\n✗ Execution finished with status: {status}")
                        
                        # Show error details if available
                        if execution:
                            error_msg = execution.get('error') or execution.get('errorMessage')
                            if error_msg:
                                print_error(f"Error: {error_msg}")
                    
                    break
                
                # Wait before next check
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print_info("\nMonitoring stopped by user")
        
        # Show summary
        self.show_monitoring_summary(elapsed_time)
        
        return execution, status, progress
    
    def show_execution_details(self, execution):
        """Show additional execution details."""
        details = []
        
        # Resource usage
        if 'cpuUsage' in execution:
            details.append(f"CPU: {execution['cpuUsage']}")
        if 'memoryUsage' in execution:
            details.append(f"Memory: {execution['memoryUsage']}")
        
        # Timing info
        if 'startTime' in execution:
            try:
                start_dt = datetime.fromisoformat(execution['startTime'].replace('Z', '+00:00'))
                running_time = (datetime.now(start_dt.tzinfo) - start_dt).total_seconds()
                details.append(f"Running: {self.format_duration(running_time)}")
            except:
                pass
        
        if details:
            print(f"    Details: {' | '.join(details)}")
    
    def show_monitoring_summary(self, total_elapsed: float):
        """Show a summary of the monitoring session."""
        print_section("Monitoring Summary")
        
        print(f"Total monitoring time: {self.format_duration(total_elapsed)}")
        print(f"Status changes: {len(self.status_history)}")
        
        if self.status_history:
            print("\nStatus Timeline:")
            for i, entry in enumerate(self.status_history):
                timestamp = entry['timestamp'].strftime("%H:%M:%S")
                elapsed = self.format_duration(entry['elapsed'])
                print(f"  {i+1}. [{timestamp}] {entry['status']} (after {elapsed})")

def find_running_execution(client, project_id: str, action_id: str = None):
    """Find a running execution to monitor."""
    print_section("Finding Running Execution")
    
    if action_id:
        try:
            # Get executions for specific action
            executions_response = client.action_executions.get_by_action(project_id, action_id)
            
            if executions_response:
                execution_list = executions_response
                if isinstance(executions_response, dict):
                    execution_list = executions_response.get('executions', [executions_response])
                
                if not isinstance(execution_list, list):
                    execution_list = [execution_list]
                
                # Look for running executions
                for execution in execution_list:
                    status = execution.get('status', '').lower()
                    if status in ['running', 'in_progress', 'executing', 'pending', 'queued']:
                        print_success(f"✓ Found running execution: {execution['id']}")
                        return execution['id']
                
                print_info("No running executions found for this action")
            else:
                print_info("No executions found for this action")
                
        except Exception as e:
            print_error(f"Error searching for executions: {e}")
    
    return None

def main():
    """Main function to monitor action execution."""
    print("mindzie-api Action Execution Monitor")
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
        
        # Get execution ID to monitor
        print_section("Execution Selection")
        print_info("You can either:")
        print("  1. Provide a specific execution ID to monitor")
        print("  2. Provide an action ID to find running executions")
        print("  3. Use execute_action.py to start a new execution, then monitor it")
        
        try:
            choice = input("\nEnter execution ID or action ID: ").strip()
            if not choice:
                print_error("ID is required.")
                return 1
        except KeyboardInterrupt:
            print_error("Cancelled.")
            return 1
        
        # Determine if it's an execution ID or action ID
        execution_id = choice
        
        # Check if it's a running execution by trying to get its details
        try:
            test_execution = client.action_executions.get_by_id(project_id, choice)
            if test_execution:
                print_success(f"✓ Found execution: {choice}")
            else:
                # Might be an action ID - try to find running executions
                print_info("Not found as execution ID, trying as action ID...")
                found_execution_id = find_running_execution(client, project_id, choice)
                if found_execution_id:
                    execution_id = found_execution_id
                else:
                    print_error("No running executions found for that action ID")
                    return 1
        except:
            # Try as action ID
            print_info("Trying as action ID...")
            found_execution_id = find_running_execution(client, project_id, choice)
            if found_execution_id:
                execution_id = found_execution_id
            else:
                print_error("Could not find execution or running executions for that ID")
                return 1
        
        # Get monitoring options
        print_section("Monitoring Options")
        try:
            interval_input = input("Check interval in seconds (default 5): ").strip()
            check_interval = int(interval_input) if interval_input else 5
            
            max_input = input("Maximum monitoring time in minutes (default 30): ").strip()
            max_duration = (int(max_input) if max_input else 30) * 60
            
            details_input = input("Show detailed info? (y/N): ").strip().lower()
            show_details = details_input in ['y', 'yes']
            
        except KeyboardInterrupt:
            print_error("Cancelled.")
            return 1
        except ValueError:
            print_error("Invalid input, using defaults.")
            check_interval = 5
            max_duration = 1800
            show_details = False
        
        # Start monitoring
        monitor = ExecutionMonitor(client, project_id, execution_id)
        final_execution, final_status, final_progress = monitor.monitor(
            check_interval=check_interval,
            max_duration=max_duration,
            show_details=show_details
        )
        
        # Show final results
        print_section("Final Status")
        if final_execution:
            print(f"Final status: {final_status}")
            print(f"Final progress: {final_progress}")
            
            # Suggest next actions
            if final_status.lower() in ['completed', 'finished', 'success']:
                print_info("Suggested next steps:")
                print_info("• Use download_execution_package.py to download results")
                print_info("• Use get_execution_details.py for detailed analysis")
            elif final_status.lower() in ['failed', 'error']:
                print_info("Suggested next steps:")
                print_info("• Use get_execution_details.py to analyze the failure")
                print_info("• Check action configuration in mindzieStudio")
        
    except Exception as e:
        handle_api_error(e, "monitoring execution")
        return 1
    
    finally:
        client.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())