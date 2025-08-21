#!/usr/bin/env python
"""
Generate comprehensive statistics and analytics for action executions.

This advanced example demonstrates how to generate detailed statistics,
performance analytics, and trends for action executions across projects.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Any, Optional

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

class ActionStatisticsAnalyzer:
    """Comprehensive action execution statistics analyzer."""
    
    def __init__(self, client, project_id: str):
        self.client = client
        self.project_id = project_id
        self.all_executions = []
        self.action_executions = defaultdict(list)
        self.analysis_date = datetime.now()
    
    def collect_execution_data(self, action_ids: List[str] = None, days_back: int = 30):
        """Collect execution data for analysis."""
        print_section("Collecting Execution Data")
        
        if action_ids:
            # Collect data for specific actions
            for action_id in action_ids:
                print_info(f"Collecting data for action: {action_id}")
                try:
                    executions_response = self.client.action_executions.get_by_action(
                        self.project_id, action_id
                    )
                    
                    if executions_response:
                        execution_list = executions_response
                        if isinstance(executions_response, dict):
                            execution_list = executions_response.get('executions', [executions_response])
                        
                        if not isinstance(execution_list, list):
                            execution_list = [execution_list]
                        
                        # Filter by date if specified
                        filtered_executions = self.filter_by_date(execution_list, days_back)
                        
                        self.action_executions[action_id].extend(filtered_executions)
                        self.all_executions.extend(filtered_executions)
                        
                        print_success(f"✓ Collected {len(filtered_executions)} executions for {action_id}")
                    else:
                        print_info(f"No executions found for action: {action_id}")
                        
                except Exception as e:
                    print_error(f"Failed to collect data for action {action_id}: {e}")
        else:
            print_info("Note: Without specific action IDs, this example shows how to analyze collected data")
            print_info("In a real scenario, you would collect executions from known action IDs")
        
        total_executions = len(self.all_executions)
        print_success(f"✓ Total executions collected: {total_executions}")
        
        return total_executions > 0
    
    def filter_by_date(self, executions: List[Dict], days_back: int) -> List[Dict]:
        """Filter executions by date range."""
        if days_back <= 0:
            return executions
        
        cutoff_date = self.analysis_date - timedelta(days=days_back)
        filtered = []
        
        for execution in executions:
            exec_date = execution.get('startTime') or execution.get('createdAt')
            if exec_date:
                try:
                    exec_dt = datetime.fromisoformat(exec_date.replace('Z', '+00:00'))
                    if exec_dt >= cutoff_date:
                        filtered.append(execution)
                except:
                    # Include executions with unparseable dates
                    filtered.append(execution)
            else:
                # Include executions without dates
                filtered.append(execution)
        
        return filtered
    
    def analyze_overall_statistics(self):
        """Generate overall execution statistics."""
        print_section("Overall Execution Statistics")
        
        if not self.all_executions:
            print_error("No execution data available")
            return
        
        total_executions = len(self.all_executions)
        print(f"Total Executions Analyzed: {total_executions}")
        print(f"Analysis Period: {self.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Unique Actions: {len(self.action_executions)}")
        
        # Status distribution
        status_counts = Counter()
        for execution in self.all_executions:
            status = execution.get('status', 'Unknown')
            status_counts[status] += 1
        
        print(f"\nStatus Distribution:")
        for status, count in status_counts.most_common():
            percentage = (count / total_executions) * 100
            print(f"  {status}: {count} ({percentage:.1f}%)")
        
        # Success rate
        success_statuses = ['completed', 'finished', 'success']
        success_count = sum(status_counts.get(status, 0) for status in success_statuses)
        success_rate = (success_count / total_executions) * 100
        
        print(f"\nOverall Success Rate: {success_rate:.1f}% ({success_count}/{total_executions})")
        
        if success_rate >= 95:
            print_success("✓ Excellent success rate")
        elif success_rate >= 85:
            print_info("⚠ Good success rate, some room for improvement")
        elif success_rate >= 70:
            print_error("⚠ Moderate success rate, needs attention")
        else:
            print_error("✗ Low success rate, requires immediate attention")
    
    def analyze_performance_metrics(self):
        """Analyze performance metrics across executions."""
        print_section("Performance Analysis")
        
        if not self.all_executions:
            return
        
        # Duration analysis
        durations = []
        for execution in self.all_executions:
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
            print(f"Execution Duration Statistics ({len(durations)} completed executions):")
            print(f"  Average: {sum(durations) / len(durations):.2f} seconds")
            print(f"  Minimum: {min(durations):.2f} seconds")
            print(f"  Maximum: {max(durations):.2f} seconds")
            print(f"  Median: {sorted(durations)[len(durations)//2]:.2f} seconds")
            
            # Duration categories
            quick_count = sum(1 for d in durations if d < 30)
            medium_count = sum(1 for d in durations if 30 <= d < 300)
            slow_count = sum(1 for d in durations if d >= 300)
            
            print(f"\nDuration Categories:")
            print(f"  Quick (< 30s): {quick_count} ({quick_count/len(durations)*100:.1f}%)")
            print(f"  Medium (30s-5m): {medium_count} ({medium_count/len(durations)*100:.1f}%)")
            print(f"  Slow (> 5m): {slow_count} ({slow_count/len(durations)*100:.1f}%)")
        else:
            print("No duration data available for analysis")
        
        # Resource usage analysis
        cpu_values = [e.get('cpuUsage') for e in self.all_executions if e.get('cpuUsage') is not None]
        memory_values = [e.get('memoryUsage') for e in self.all_executions if e.get('memoryUsage') is not None]
        
        if cpu_values:
            print(f"\nCPU Usage Statistics ({len(cpu_values)} executions):")
            print(f"  Average: {sum(cpu_values) / len(cpu_values):.2f}")
            print(f"  Minimum: {min(cpu_values):.2f}")
            print(f"  Maximum: {max(cpu_values):.2f}")
        
        if memory_values:
            print(f"\nMemory Usage Statistics ({len(memory_values)} executions):")
            print(f"  Average: {sum(memory_values) / len(memory_values):.2f}")
            print(f"  Minimum: {min(memory_values):.2f}")
            print(f"  Maximum: {max(memory_values):.2f}")
    
    def analyze_action_breakdown(self):
        """Analyze statistics by individual actions."""
        print_section("Per-Action Analysis")
        
        if not self.action_executions:
            print_info("No action-specific data available")
            return
        
        for action_id, executions in self.action_executions.items():
            print(f"\nAction: {action_id}")
            print(f"  Total executions: {len(executions)}")
            
            # Status breakdown
            status_counts = Counter()
            for execution in executions:
                status = execution.get('status', 'Unknown')
                status_counts[status] += 1
            
            # Success rate
            success_statuses = ['completed', 'finished', 'success']
            success_count = sum(status_counts.get(status, 0) for status in success_statuses)
            success_rate = (success_count / len(executions)) * 100 if executions else 0
            
            print(f"  Success rate: {success_rate:.1f}% ({success_count}/{len(executions)})")
            
            # Performance for this action
            durations = []
            for execution in executions:
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
                print(f"  Average duration: {sum(durations) / len(durations):.2f}s")
                print(f"  Duration range: {min(durations):.2f}s - {max(durations):.2f}s")
            
            # Recent trends (if enough data)
            if len(executions) >= 5:
                recent_executions = sorted(executions, 
                    key=lambda x: x.get('startTime') or x.get('createdAt') or '', 
                    reverse=True)[:5]
                recent_success = sum(1 for e in recent_executions 
                                   if e.get('status', '').lower() in success_statuses)
                recent_rate = (recent_success / 5) * 100
                print(f"  Recent trend (last 5): {recent_rate:.0f}% success")
    
    def analyze_temporal_trends(self):
        """Analyze execution trends over time."""
        print_section("Temporal Trends Analysis")
        
        if not self.all_executions:
            return
        
        # Group executions by day
        daily_stats = defaultdict(lambda: {'count': 0, 'success': 0, 'durations': []})
        
        for execution in self.all_executions:
            exec_date = execution.get('startTime') or execution.get('createdAt')
            if exec_date:
                try:
                    exec_dt = datetime.fromisoformat(exec_date.replace('Z', '+00:00'))
                    day_key = exec_dt.strftime('%Y-%m-%d')
                    
                    daily_stats[day_key]['count'] += 1
                    
                    status = execution.get('status', '').lower()
                    if status in ['completed', 'finished', 'success']:
                        daily_stats[day_key]['success'] += 1
                    
                    # Calculate duration if available
                    end_time = execution.get('endTime') or execution.get('completedAt')
                    if end_time:
                        try:
                            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                            duration = (end_dt - exec_dt).total_seconds()
                            daily_stats[day_key]['durations'].append(duration)
                        except:
                            pass
                except:
                    pass
        
        if daily_stats:
            print("Daily execution trends:")
            print(f"{'Date':<12} {'Count':<8} {'Success Rate':<12} {'Avg Duration':<15}")
            print("-" * 50)
            
            for day in sorted(daily_stats.keys()):
                stats = daily_stats[day]
                success_rate = (stats['success'] / stats['count']) * 100 if stats['count'] > 0 else 0
                avg_duration = sum(stats['durations']) / len(stats['durations']) if stats['durations'] else 0
                
                print(f"{day:<12} {stats['count']:<8} {success_rate:<11.1f}% {avg_duration:<14.1f}s")
        else:
            print("No temporal data available for trend analysis")
    
    def analyze_failure_patterns(self):
        """Analyze patterns in failed executions."""
        print_section("Failure Pattern Analysis")
        
        # Get failed executions
        failed_executions = []
        for execution in self.all_executions:
            status = execution.get('status', '').lower()
            if status in ['failed', 'error', 'cancelled', 'aborted', 'timeout']:
                failed_executions.append(execution)
        
        if not failed_executions:
            print_success("✓ No failed executions found")
            return
        
        print(f"Failed Executions: {len(failed_executions)}")
        
        # Failure reasons
        error_types = Counter()
        for execution in failed_executions:
            error_msg = execution.get('error') or execution.get('errorMessage') or execution.get('message')
            if error_msg:
                # Extract error type (first few words)
                error_type = ' '.join(str(error_msg).split()[:3])
                error_types[error_type] += 1
            else:
                error_types['Unknown Error'] += 1
        
        print(f"\nCommon Error Types:")
        for error_type, count in error_types.most_common(5):
            percentage = (count / len(failed_executions)) * 100
            print(f"  {error_type}: {count} ({percentage:.1f}%)")
        
        # Failure by action
        if self.action_executions:
            action_failures = {}
            for action_id, executions in self.action_executions.items():
                failed_count = sum(1 for e in executions 
                                 if e.get('status', '').lower() in ['failed', 'error', 'cancelled'])
                if failed_count > 0:
                    failure_rate = (failed_count / len(executions)) * 100
                    action_failures[action_id] = (failed_count, failure_rate)
            
            if action_failures:
                print(f"\nFailure Rate by Action:")
                for action_id, (count, rate) in sorted(action_failures.items(), 
                                                      key=lambda x: x[1][1], reverse=True):
                    print(f"  {action_id[:30]}: {count} failures ({rate:.1f}%)")
    
    def generate_recommendations(self):
        """Generate actionable recommendations based on analysis."""
        print_section("Recommendations")
        
        if not self.all_executions:
            print_info("No data available for recommendations")
            return
        
        recommendations = []
        
        # Success rate recommendations
        total_executions = len(self.all_executions)
        success_statuses = ['completed', 'finished', 'success']
        success_count = sum(1 for e in self.all_executions 
                           if e.get('status', '').lower() in success_statuses)
        success_rate = (success_count / total_executions) * 100
        
        if success_rate < 90:
            recommendations.append(
                f"🔴 CRITICAL: Success rate is {success_rate:.1f}%. "
                "Review failed executions and improve action reliability."
            )
        elif success_rate < 95:
            recommendations.append(
                f"🟡 MODERATE: Success rate is {success_rate:.1f}%. "
                "Consider investigating occasional failures."
            )
        
        # Performance recommendations
        durations = []
        for execution in self.all_executions:
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
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            
            if avg_duration > 300:  # 5 minutes
                recommendations.append(
                    f"🟡 PERFORMANCE: Average execution time is {avg_duration:.1f}s. "
                    "Consider optimizing action performance."
                )
            
            if max_duration > 1800:  # 30 minutes
                recommendations.append(
                    f"🟡 PERFORMANCE: Maximum execution time is {max_duration:.1f}s. "
                    "Review long-running executions for optimization opportunities."
                )
        
        # Action-specific recommendations
        if self.action_executions:
            for action_id, executions in self.action_executions.items():
                if len(executions) >= 10:  # Only for actions with sufficient data
                    action_success = sum(1 for e in executions 
                                       if e.get('status', '').lower() in success_statuses)
                    action_rate = (action_success / len(executions)) * 100
                    
                    if action_rate < 80:
                        recommendations.append(
                            f"🔴 ACTION: {action_id[:30]} has {action_rate:.1f}% success rate. "
                            "Requires immediate attention."
                        )
        
        # Display recommendations
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print_success("✓ No critical issues found. System performance looks good!")
        
        print(f"\nGeneral recommendations:")
        print(f"• Monitor execution trends regularly")
        print(f"• Set up alerting for success rate drops below 95%")
        print(f"• Review and optimize actions with >5 minute average execution time")
        print(f"• Investigate and fix recurring error patterns")
    
    def generate_full_report(self):
        """Generate a comprehensive statistics report."""
        print("mindzie-api Action Execution Statistics Report")
        print("=" * 70)
        print(f"Generated: {self.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.analyze_overall_statistics()
        self.analyze_performance_metrics()
        self.analyze_action_breakdown()
        self.analyze_temporal_trends()
        self.analyze_failure_patterns()
        self.generate_recommendations()

def main():
    """Main function to generate action execution statistics."""
    print("mindzie-api Action Execution Statistics Generator")
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
        
        # Create analyzer
        analyzer = ActionStatisticsAnalyzer(client, project_id)
        
        # Get analysis parameters
        print_section("Analysis Parameters")
        print("You can analyze:")
        print("  1. Specific action IDs")
        print("  2. Generate example statistics (demonstration)")
        
        try:
            mode_choice = input("Select mode (1 or 2): ").strip()
        except KeyboardInterrupt:
            print_error("Cancelled.")
            return 1
        
        if mode_choice == "1":
            # Collect specific action data
            print_section("Action ID Collection")
            action_ids = []
            print("Enter action IDs to analyze (press Enter when done):")
            
            while True:
                try:
                    action_id = input(f"Action ID #{len(action_ids) + 1} (or Enter to finish): ").strip()
                    if not action_id:
                        break
                    action_ids.append(action_id)
                except KeyboardInterrupt:
                    break
            
            if not action_ids:
                print_error("No action IDs provided.")
                return 1
            
            # Get time range
            try:
                days_input = input("Number of days to analyze (default 30): ").strip()
                days_back = int(days_input) if days_input else 30
            except (ValueError, KeyboardInterrupt):
                days_back = 30
            
            # Collect data
            if analyzer.collect_execution_data(action_ids, days_back):
                analyzer.generate_full_report()
            else:
                print_error("No execution data found for analysis.")
                return 1
        
        elif mode_choice == "2":
            # Demonstration mode
            print_section("Demonstration Mode")
            print_info("This mode shows how the statistics would look with sample data.")
            print_info("In a real scenario, you would provide actual action IDs.")
            
            # Generate sample data for demonstration
            print_info("Generating sample execution data for demonstration...")
            
            # Create some sample executions
            sample_executions = [
                {
                    'id': 'sample-exec-1',
                    'status': 'completed',
                    'startTime': '2024-01-15T10:00:00Z',
                    'endTime': '2024-01-15T10:02:30Z'
                },
                {
                    'id': 'sample-exec-2', 
                    'status': 'completed',
                    'startTime': '2024-01-15T11:00:00Z',
                    'endTime': '2024-01-15T11:01:45Z'
                },
                {
                    'id': 'sample-exec-3',
                    'status': 'failed',
                    'startTime': '2024-01-15T12:00:00Z',
                    'endTime': '2024-01-15T12:00:30Z',
                    'error': 'Connection timeout'
                }
            ]
            
            analyzer.all_executions = sample_executions
            analyzer.action_executions['sample-action-1'] = sample_executions
            
            print_success("✓ Sample data generated")
            analyzer.generate_full_report()
        
        else:
            print_error("Invalid mode selection.")
            return 1
        
        print_section("Analysis Complete")
        print_success("✓ Action execution statistics analysis completed")
        print_info("Use this analysis to:")
        print_info("• Identify performance bottlenecks")
        print_info("• Monitor success rates and trends")  
        print_info("• Plan action improvements and optimizations")
        print_info("• Set up monitoring and alerting thresholds")
    
    except Exception as e:
        handle_api_error(e, "generating action statistics")
        return 1
    
    finally:
        client.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())