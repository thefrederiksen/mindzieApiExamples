#!/usr/bin/env python
"""
Compare multiple action executions to analyze performance and results.

This advanced example demonstrates how to compare multiple executions
of the same action, analyzing differences in performance, results, and status.
"""

import os
import sys
import json
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

class ExecutionComparator:
    """Class to compare multiple action executions."""
    
    def __init__(self, client, project_id: str):
        self.client = client
        self.project_id = project_id
        self.executions = []
    
    def add_execution(self, execution_id: str):
        """Add an execution to the comparison."""
        try:
            execution = self.client.action_executions.get_by_id(self.project_id, execution_id)
            if execution:
                self.executions.append(execution)
                print_success(f"✓ Added execution: {execution_id}")
                return True
            else:
                print_error(f"✗ Execution not found: {execution_id}")
                return False
        except Exception as e:
            print_error(f"✗ Failed to get execution {execution_id}: {e}")
            return False
    
    def add_executions_from_action(self, action_id: str, limit: int = 5):
        """Add recent executions from a specific action."""
        try:
            executions_response = self.client.action_executions.get_by_action(self.project_id, action_id)
            
            if executions_response:
                execution_list = executions_response
                if isinstance(executions_response, dict):
                    execution_list = executions_response.get('executions', [executions_response])
                
                if not isinstance(execution_list, list):
                    execution_list = [execution_list]
                
                # Sort by timestamp (most recent first)
                def get_timestamp(exec):
                    return exec.get('startTime') or exec.get('createdAt') or ''
                
                try:
                    execution_list = sorted(execution_list, key=get_timestamp, reverse=True)
                except:
                    pass  # Use original order if sorting fails
                
                # Add up to 'limit' executions
                added_count = 0
                for execution in execution_list[:limit]:
                    if execution.get('id'):
                        self.executions.append(execution)
                        added_count += 1
                        print_success(f"✓ Added execution: {execution['id']}")
                
                return added_count
            else:
                print_error("No executions found for this action")
                return 0
                
        except Exception as e:
            print_error(f"Failed to get executions for action: {e}")
            return 0
    
    def compare_basic_info(self):
        """Compare basic execution information."""
        print_section("Basic Execution Information")
        
        if not self.executions:
            print_error("No executions to compare")
            return
        
        print(f"Comparing {len(self.executions)} executions:\n")
        
        # Table header
        print(f"{'Index':<5} {'Execution ID':<36} {'Status':<12} {'Start Time':<20}")
        print("-" * 80)
        
        # Table rows
        for i, execution in enumerate(self.executions):
            exec_id = execution.get('id', 'Unknown')[:35]
            status = execution.get('status', 'Unknown')
            start_time = execution.get('startTime') or execution.get('createdAt') or 'Unknown'
            
            # Format start time
            if start_time != 'Unknown':
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    start_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    start_time = start_time[:19]  # Truncate if can't parse
            
            print(f"{i+1:<5} {exec_id:<36} {status:<12} {start_time:<20}")
    
    def compare_performance(self):
        """Compare execution performance metrics."""
        print_section("Performance Comparison")
        
        if not self.executions:
            return
        
        performance_data = []
        
        for i, execution in enumerate(self.executions):
            perf = {'index': i + 1}
            
            # Calculate duration
            start_time = execution.get('startTime') or execution.get('createdAt')
            end_time = execution.get('endTime') or execution.get('completedAt')
            
            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    duration = (end_dt - start_dt).total_seconds()
                    perf['duration'] = duration
                except:
                    perf['duration'] = None
            else:
                perf['duration'] = None
            
            # Resource usage
            perf['cpu_usage'] = execution.get('cpuUsage')
            perf['memory_usage'] = execution.get('memoryUsage')
            perf['status'] = execution.get('status', 'Unknown')
            
            performance_data.append(perf)
        
        # Display performance table
        print(f"{'Index':<5} {'Duration (s)':<12} {'CPU Usage':<12} {'Memory Usage':<15} {'Status':<12}")
        print("-" * 65)
        
        for perf in performance_data:
            duration_str = f"{perf['duration']:.2f}" if perf['duration'] is not None else "N/A"
            cpu_str = str(perf['cpu_usage']) if perf['cpu_usage'] is not None else "N/A"
            memory_str = str(perf['memory_usage']) if perf['memory_usage'] is not None else "N/A"
            
            print(f"{perf['index']:<5} {duration_str:<12} {cpu_str:<12} {memory_str:<15} {perf['status']:<12}")
        
        # Performance statistics
        durations = [p['duration'] for p in performance_data if p['duration'] is not None]
        if durations:
            print(f"\nPerformance Statistics:")
            print(f"  Average duration: {sum(durations) / len(durations):.2f}s")
            print(f"  Fastest execution: {min(durations):.2f}s")
            print(f"  Slowest execution: {max(durations):.2f}s")
            print(f"  Duration variance: {max(durations) - min(durations):.2f}s")
    
    def compare_status_distribution(self):
        """Compare status distribution across executions."""
        print_section("Status Distribution")
        
        if not self.executions:
            return
        
        # Count statuses
        status_counts = {}
        for execution in self.executions:
            status = execution.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total_executions = len(self.executions)
        
        print("Status breakdown:")
        for status, count in status_counts.items():
            percentage = (count / total_executions) * 100
            print(f"  {status}: {count} ({percentage:.1f}%)")
        
        # Success rate
        success_statuses = ['completed', 'finished', 'success']
        success_count = sum(status_counts.get(status, 0) for status in success_statuses)
        success_rate = (success_count / total_executions) * 100
        
        print(f"\nOverall success rate: {success_rate:.1f}% ({success_count}/{total_executions})")
    
    def compare_results(self):
        """Compare execution results and outputs."""
        print_section("Results Comparison")
        
        if not self.executions:
            return
        
        result_fields = ['result', 'output', 'resultData', 'executionResult']
        
        for i, execution in enumerate(self.executions):
            print(f"\nExecution {i+1} ({execution.get('id', 'Unknown')[:8]}...):")
            print(f"  Status: {execution.get('status', 'Unknown')}")
            
            # Look for result data
            found_results = False
            for field in result_fields:
                if field in execution and execution[field] is not None:
                    found_results = True
                    result_data = execution[field]
                    
                    print(f"  {field}:")
                    if isinstance(result_data, (dict, list)):
                        try:
                            result_str = json.dumps(result_data, indent=4)
                            if len(result_str) > 200:
                                print(f"    {result_str[:200]}... [truncated]")
                            else:
                                print(f"    {result_str}")
                        except:
                            result_str = str(result_data)
                            if len(result_str) > 200:
                                print(f"    {result_str[:200]}... [truncated]")
                            else:
                                print(f"    {result_str}")
                    else:
                        result_str = str(result_data)
                        if len(result_str) > 200:
                            print(f"    {result_str[:200]}... [truncated]")
                        else:
                            print(f"    {result_str}")
            
            if not found_results:
                print("  No result data available")
    
    def compare_errors(self):
        """Compare errors across failed executions."""
        print_section("Error Analysis")
        
        if not self.executions:
            return
        
        failed_executions = []
        for execution in self.executions:
            status = execution.get('status', '').lower()
            if status in ['failed', 'error', 'cancelled', 'aborted']:
                failed_executions.append(execution)
        
        if not failed_executions:
            print_success("✓ No failed executions found")
            return
        
        print(f"Found {len(failed_executions)} failed executions:\n")
        
        error_fields = ['error', 'errorMessage', 'exception', 'failureReason', 'message']
        
        for i, execution in enumerate(failed_executions):
            print(f"Failed Execution {i+1} ({execution.get('id', 'Unknown')[:8]}...):")
            print(f"  Status: {execution.get('status', 'Unknown')}")
            
            # Look for error information
            found_error = False
            for field in error_fields:
                if field in execution and execution[field]:
                    found_error = True
                    error_msg = str(execution[field])
                    if len(error_msg) > 300:
                        error_msg = error_msg[:300] + "... [truncated]"
                    print(f"  {field}: {error_msg}")
            
            if not found_error:
                print("  No error details available")
            print()
    
    def generate_comparison_report(self):
        """Generate a comprehensive comparison report."""
        print_section("Execution Comparison Report")
        
        if not self.executions:
            print_error("No executions to compare")
            return
        
        self.compare_basic_info()
        self.compare_performance()
        self.compare_status_distribution()
        self.compare_results()
        self.compare_errors()
        
        # Summary insights
        print_section("Comparison Insights")
        
        # Performance insights
        durations = []
        for execution in self.executions:
            start_time = execution.get('startTime') or execution.get('createdAt')
            end_time = execution.get('endTime') or execution.get('completedAt')
            
            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    duration = (end_dt - start_dt).total_seconds()
                    durations.append(duration)
                except:
                    pass
        
        if durations:
            if max(durations) - min(durations) > 30:  # More than 30 seconds variance
                print_info("⚠ High performance variance detected - investigate execution differences")
            else:
                print_success("✓ Consistent execution performance")
        
        # Status insights
        status_counts = {}
        for execution in self.executions:
            status = execution.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        success_statuses = ['completed', 'finished', 'success']
        success_count = sum(status_counts.get(status, 0) for status in success_statuses)
        success_rate = (success_count / len(self.executions)) * 100
        
        if success_rate < 80:
            print_error(f"⚠ Low success rate ({success_rate:.1f}%) - review action configuration")
        elif success_rate < 95:
            print_info(f"⚠ Moderate success rate ({success_rate:.1f}%) - room for improvement")
        else:
            print_success(f"✓ High success rate ({success_rate:.1f}%)")

def main():
    """Main function to compare action executions."""
    print("mindzie-api Action Execution Comparison Tool")
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
        
        # Create comparator
        comparator = ExecutionComparator(client, project_id)
        
        # Get comparison mode
        print_section("Comparison Mode")
        print("Choose how to select executions to compare:")
        print("  1. Enter specific execution IDs")
        print("  2. Compare recent executions from an action")
        
        try:
            mode_choice = input("Select mode (1 or 2): ").strip()
        except KeyboardInterrupt:
            print_error("Cancelled.")
            return 1
        
        if mode_choice == "1":
            # Manual execution ID entry
            print_section("Execution ID Entry")
            print("Enter execution IDs to compare (press Enter when done):")
            
            while True:
                try:
                    exec_id = input(f"Execution ID #{len(comparator.executions) + 1} (or Enter to finish): ").strip()
                    if not exec_id:
                        break
                    comparator.add_execution(exec_id)
                except KeyboardInterrupt:
                    break
        
        elif mode_choice == "2":
            # Action-based comparison
            print_section("Action-Based Comparison")
            try:
                action_id = input("Enter Action ID: ").strip()
                if not action_id:
                    print_error("Action ID is required.")
                    return 1
                
                limit_input = input("Number of recent executions to compare (default 5): ").strip()
                limit = int(limit_input) if limit_input else 5
                
                added_count = comparator.add_executions_from_action(action_id, limit)
                if added_count == 0:
                    print_error("No executions found to compare.")
                    return 1
                    
            except (ValueError, KeyboardInterrupt):
                print_error("Invalid input or cancelled.")
                return 1
        
        else:
            print_error("Invalid mode selection.")
            return 1
        
        # Check if we have executions to compare
        if len(comparator.executions) < 2:
            print_error("Need at least 2 executions to compare.")
            return 1
        
        # Generate comparison report
        comparator.generate_comparison_report()
        
        print_section("Summary")
        print_success(f"✓ Compared {len(comparator.executions)} executions successfully")
        print_info("Use this analysis to optimize action performance and reliability")
    
    except Exception as e:
        handle_api_error(e, "comparing executions")
        return 1
    
    finally:
        client.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())