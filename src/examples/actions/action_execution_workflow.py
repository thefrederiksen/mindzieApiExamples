#!/usr/bin/env python
"""
Complete action execution workflow: Execute → Monitor → Analyze → Download.

This advanced example demonstrates a complete workflow for action execution,
including execution, real-time monitoring, result analysis, and package download.
"""

import os
import sys
import time
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

class ActionWorkflow:
    """Complete action execution workflow manager."""
    
    def __init__(self, client, project_id: str, action_id: str):
        self.client = client
        self.project_id = project_id
        self.action_id = action_id
        self.execution_id = None
        self.workflow_start_time = datetime.now()
        self.execution_history = []
    
    def step_1_execute_action(self):
        """Step 1: Execute the action."""
        print_section("Step 1: Executing Action")
        
        try:
            print_info(f"Executing action: {self.action_id}")
            print_info(f"Project: {self.project_id}")
            
            result = self.client.actions.execute(self.project_id, self.action_id)
            
            if result:
                print_success("✓ Action execution request submitted")
                
                # Extract execution ID if available
                if isinstance(result, dict):
                    self.execution_id = result.get('executionId') or result.get('id')
                    if self.execution_id:
                        print_success(f"✓ Got execution ID: {self.execution_id}")
                    else:
                        print_info("No execution ID returned - action may have completed synchronously")
                        self.execution_id = None
                else:
                    print_info("Action returned direct result (synchronous execution)")
                    self.execution_id = None
                
                return result
            else:
                print_error("✗ No response from action execution")
                return None
                
        except Exception as e:
            print_error(f"✗ Action execution failed: {e}")
            return None
    
    def step_2_find_execution_id(self):
        """Step 2: Find the execution ID if not returned directly."""
        if self.execution_id:
            return True
        
        print_section("Step 2: Finding Execution ID")
        
        try:
            # Get the latest execution for this action
            print_info("Searching for recent executions...")
            last_execution = self.client.action_executions.get_last(self.project_id, self.action_id)
            
            if last_execution:
                self.execution_id = last_execution.get('id')
                if self.execution_id:
                    print_success(f"✓ Found execution ID: {self.execution_id}")
                    return True
                else:
                    print_error("✗ No execution ID in response")
                    return False
            else:
                print_error("✗ No execution found")
                return False
                
        except Exception as e:
            print_error(f"✗ Failed to find execution ID: {e}")
            return False
    
    def step_3_monitor_execution(self, max_wait_time: int = 300):
        """Step 3: Monitor execution progress."""
        if not self.execution_id:
            print_info("Skipping monitoring - no execution ID available")
            return None
        
        print_section("Step 3: Monitoring Execution")
        
        start_time = datetime.now()
        check_interval = 5
        last_status = None
        
        print_info(f"Monitoring execution: {self.execution_id}")
        print_info(f"Check interval: {check_interval} seconds")
        print_info(f"Maximum wait time: {max_wait_time} seconds")
        print("-" * 50)
        
        try:
            while (datetime.now() - start_time).total_seconds() < max_wait_time:
                # Get current execution status
                execution = self.client.action_executions.get_by_id(self.project_id, self.execution_id)
                
                if execution:
                    status = execution.get('status', 'Unknown')
                    progress = execution.get('progress', 'N/A')
                    elapsed = (datetime.now() - start_time).total_seconds()
                    
                    # Show status update
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] Status: {status} | Progress: {progress} | Elapsed: {elapsed:.0f}s")
                    
                    # Record status change
                    if status != last_status:
                        self.execution_history.append({
                            'timestamp': datetime.now(),
                            'status': status,
                            'progress': progress,
                            'elapsed': elapsed
                        })
                    last_status = status
                    
                    # Check if execution is finished
                    if status.lower() in ['completed', 'finished', 'success', 'failed', 'error', 'cancelled']:
                        if status.lower() in ['completed', 'finished', 'success']:
                            print_success(f"\n✓ Execution completed successfully in {elapsed:.1f}s")
                        else:
                            print_error(f"\n✗ Execution failed with status: {status}")
                        
                        return execution
                    
                    # Wait before next check
                    time.sleep(check_interval)
                else:
                    print_error("Failed to get execution status")
                    break
            
            print_error(f"Monitoring timed out after {max_wait_time} seconds")
            return None
            
        except KeyboardInterrupt:
            print_info("\nMonitoring interrupted by user")
            return None
        except Exception as e:
            print_error(f"Monitoring failed: {e}")
            return None
    
    def step_4_analyze_results(self, execution):
        """Step 4: Analyze execution results."""
        print_section("Step 4: Analyzing Results")
        
        if not execution:
            print_error("No execution data to analyze")
            return False
        
        status = execution.get('status', 'Unknown')
        print(f"Final Status: {status}")
        
        # Analyze timing
        if self.execution_history:
            print("\nExecution Timeline:")
            for i, entry in enumerate(self.execution_history):
                timestamp = entry['timestamp'].strftime("%H:%M:%S")
                print(f"  {i+1}. [{timestamp}] {entry['status']} (after {entry['elapsed']:.1f}s)")
        
        # Analyze results
        if status.lower() in ['completed', 'finished', 'success']:
            print_success("\n✓ Execution Analysis: SUCCESS")
            
            # Look for result data
            result_fields = ['result', 'output', 'resultData', 'executionResult']
            for field in result_fields:
                if field in execution and execution[field]:
                    print(f"\n{field} available:")
                    result_data = execution[field]
                    if isinstance(result_data, (dict, list)):
                        try:
                            result_str = json.dumps(result_data, indent=2)
                            if len(result_str) > 300:
                                print(result_str[:300] + "... [truncated]")
                            else:
                                print(result_str)
                        except:
                            print(str(result_data)[:300])
                    else:
                        result_str = str(result_data)
                        if len(result_str) > 300:
                            print(result_str[:300] + "... [truncated]")
                        else:
                            print(result_str)
            
            return True
        
        else:
            print_error("\n✗ Execution Analysis: FAILED")
            
            # Show error details
            error_fields = ['error', 'errorMessage', 'exception', 'message']
            for field in error_fields:
                if field in execution and execution[field]:
                    print_error(f"{field}: {execution[field]}")
            
            return False
    
    def step_5_download_package(self, execution):
        """Step 5: Download execution package if available."""
        if not execution or not self.execution_id:
            print_info("Skipping download - no execution data available")
            return None
        
        status = execution.get('status', 'Unknown')
        if status.lower() not in ['completed', 'finished', 'success']:
            print_info("Skipping download - execution not completed successfully")
            return None
        
        print_section("Step 5: Downloading Results Package")
        
        try:
            # Try to download the package
            package_response = self.client.action_executions.download_package(
                self.project_id, self.execution_id
            )
            
            if package_response:
                # Create downloads directory
                downloads_dir = Path.cwd() / "downloads"
                downloads_dir.mkdir(exist_ok=True)
                
                # Determine file name and extension
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"action_{self.action_id[:8]}_{timestamp}"
                
                # Save package
                if isinstance(package_response, dict):
                    if 'downloadUrl' in package_response:
                        print_info(f"Download URL: {package_response['downloadUrl']}")
                        return package_response['downloadUrl']
                    else:
                        filename += ".json"
                        file_path = downloads_dir / filename
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(package_response, f, indent=2)
                elif isinstance(package_response, (bytes, bytearray)):
                    filename += ".bin"
                    file_path = downloads_dir / filename
                    with open(file_path, 'wb') as f:
                        f.write(package_response)
                else:
                    filename += ".txt"
                    file_path = downloads_dir / filename
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(package_response))
                
                file_size = file_path.stat().st_size
                print_success(f"✓ Package downloaded: {file_path}")
                print_info(f"File size: {file_size:,} bytes")
                return str(file_path)
            
            else:
                print_info("No package data available for download")
                return None
                
        except Exception as e:
            print_error(f"Package download failed: {e}")
            return None
    
    def run_complete_workflow(self, monitor_timeout: int = 300):
        """Run the complete workflow."""
        print("mindzie-api Complete Action Execution Workflow")
        print("=" * 60)
        
        workflow_success = True
        
        # Step 1: Execute action
        execution_result = self.step_1_execute_action()
        if not execution_result:
            return False
        
        # Step 2: Find execution ID if needed
        if not self.step_2_find_execution_id():
            print_info("Continuing without execution monitoring...")
        
        # Step 3: Monitor execution
        final_execution = self.step_3_monitor_execution(monitor_timeout)
        
        # Step 4: Analyze results
        if final_execution:
            analysis_success = self.step_4_analyze_results(final_execution)
            workflow_success = workflow_success and analysis_success
            
            # Step 5: Download package
            downloaded_file = self.step_5_download_package(final_execution)
        else:
            print_info("Skipping analysis and download - no execution data")
            workflow_success = False
        
        # Workflow summary
        self.show_workflow_summary(workflow_success, final_execution)
        
        return workflow_success
    
    def show_workflow_summary(self, success: bool, execution):
        """Show a summary of the complete workflow."""
        print_section("Workflow Summary")
        
        total_time = (datetime.now() - self.workflow_start_time).total_seconds()
        print(f"Total workflow time: {total_time:.1f} seconds")
        
        if success:
            print_success("✓ Workflow completed successfully!")
        else:
            print_error("✗ Workflow completed with issues")
        
        print(f"\nWorkflow steps:")
        print(f"  1. Execute Action: {'✓' if execution else '✗'}")
        print(f"  2. Find Execution ID: {'✓' if self.execution_id else '✗'}")
        print(f"  3. Monitor Progress: {'✓' if execution else '✗'}")
        print(f"  4. Analyze Results: {'✓' if success else '✗'}")
        print(f"  5. Download Package: {'?' if execution else '✗'}")
        
        if execution:
            final_status = execution.get('status', 'Unknown')
            print(f"\nFinal execution status: {final_status}")
        
        if self.execution_id:
            print(f"Execution ID: {self.execution_id}")

def main():
    """Main function to run the complete workflow."""
    print("mindzie-api Complete Action Execution Workflow")
    print("=" * 60)
    
    # Create client
    client = create_client()
    if not client:
        return 1
    
    try:
        # Get available projects
        print_section("Project Selection")
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
        
        print_success(f"Selected project: {project_name}")
        
        # Get action ID
        print_section("Action Selection")
        print_info("Enter the action ID to execute through the complete workflow.")
        
        try:
            action_id = input("Action ID: ").strip()
            if not action_id:
                print_error("Action ID is required.")
                return 1
        except KeyboardInterrupt:
            print_error("Cancelled.")
            return 1
        
        # Get workflow options
        print_section("Workflow Options")
        try:
            timeout_input = input("Monitoring timeout in seconds (default 300): ").strip()
            monitor_timeout = int(timeout_input) if timeout_input else 300
        except (ValueError, KeyboardInterrupt):
            monitor_timeout = 300
        
        # Run the complete workflow
        workflow = ActionWorkflow(client, project_id, action_id)
        success = workflow.run_complete_workflow(monitor_timeout)
        
        return 0 if success else 1
    
    except Exception as e:
        handle_api_error(e, "action workflow")
        return 1
    
    finally:
        client.close()

if __name__ == "__main__":
    sys.exit(main())