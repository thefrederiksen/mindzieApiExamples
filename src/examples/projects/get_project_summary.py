#!/usr/bin/env python
"""
Get project summary statistics.

This script retrieves and displays summary statistics for a specific project,
including aggregated metrics, usage data, and performance indicators.

Usage:
    python get_project_summary.py                   # Auto-select first project
    python get_project_summary.py <project_id>      # Use specific project

Examples:
    # Auto-select first available project
    python get_project_summary.py
    
    # Use specific project by ID
    python get_project_summary.py 4315075c-b4d9-48c2-9520-cda63f04da7a
    python get_project_summary.py bc7f6a6d-552d-44bf-b9f7-310adf733dc0
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Import the proper mindzie_api library
from mindzie_api import MindzieAPIClient
from mindzie_api.exceptions import (
    MindzieAPIException, AuthenticationError, NotFoundError,
    ValidationError, TimeoutError
)

# Add parent directory to path for .env loading
sys.path.append(str(Path(__file__).parent.parent))

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

# Import our utility functions
from api_utils import get_project_summary_by_id, discover_projects, show_usage_tip

def format_date(date_str):
    """Format ISO date string to readable format."""
    if not date_str:
        return "N/A"
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except:
        return str(date_str)

def format_size(size_bytes):
    """Format file size in human readable format."""
    if not size_bytes or size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def get_project_summary(project_id):
    """Get project summary by ID using MindzieAPIClient."""
    return get_project_summary_by_id(project_id)

def display_project_summary(summary_data, project_id):
    """Display formatted project summary."""
    if not summary_data:
        return
    
    print("=" * 80)
    print("PROJECT SUMMARY")
    print("=" * 80)
    
    # Project identification
    name = summary_data.get('project_name', 'Unknown Project')
    
    print(f"\n[INFO] PROJECT: {name}")
    print(f"ID: {project_id}")
    print("-" * 80)
    
    # Core Statistics
    print("\n[INFO] CORE STATISTICS")
    print("-" * 40)
    
    # Extract from nested statistics
    stats = summary_data.get('statistics', {})
    dataset_count = stats.get('total_datasets', 0)
    investigation_count = stats.get('total_investigations', 0)
    dashboard_count = stats.get('total_dashboards', 0)
    notebook_count = stats.get('total_notebooks', 0)
    user_count = stats.get('total_users', 0)
    
    print(f"Total Datasets:        {dataset_count:>10}")
    print(f"Total Investigations:  {investigation_count:>10}")
    print(f"Total Dashboards:      {dashboard_count:>10}")
    print(f"Total Notebooks:       {notebook_count:>10}")
    print(f"Active Users:          {user_count:>10}")
    
    # Activity Metrics (if available)
    print("\n[INFO] ACTIVITY METRICS")
    print("-" * 40)
    
    total_executions = summary_data.get('TotalExecutions') or summary_data.get('total_executions')
    if total_executions is not None:
        print(f"Total Executions:      {total_executions:>10}")
    
    recent_executions = summary_data.get('RecentExecutions') or summary_data.get('recent_executions')
    if recent_executions is not None:
        print(f"Recent Executions:     {recent_executions:>10}")
    
    avg_execution_time = summary_data.get('AvgExecutionTime') or summary_data.get('avg_execution_time')
    if avg_execution_time is not None:
        print(f"Avg Execution Time:    {avg_execution_time:>10}s")
    
    # Storage Information (if available)
    print("\n[INFO] STORAGE & DATA")
    print("-" * 40)
    
    total_storage = summary_data.get('TotalStorage') or summary_data.get('total_storage')
    if total_storage is not None:
        print(f"Total Storage Used:    {format_size(total_storage):>15}")
    
    total_records = summary_data.get('TotalRecords') or summary_data.get('total_records')
    if total_records is not None:
        print(f"Total Records:         {total_records:>15,}")
    
    # Performance Metrics (if available)
    print("\n[INFO] PERFORMANCE")
    print("-" * 40)
    
    success_rate = summary_data.get('SuccessRate') or summary_data.get('success_rate')
    if success_rate is not None:
        print(f"Success Rate:          {success_rate:>12.1f}%")
    
    error_rate = summary_data.get('ErrorRate') or summary_data.get('error_rate')
    if error_rate is not None:
        print(f"Error Rate:            {error_rate:>12.1f}%")
    
    # Timestamps
    print("\n[INFO] TIMELINE")
    print("-" * 40)
    
    created = summary_data.get('date_created')
    if created:
        print(f"Created:               {format_date(created)}")
    
    last_activity = summary_data.get('date_modified')
    if last_activity:
        print(f"Last Activity:         {format_date(last_activity)}")
    
    # Summary Insights
    print("\n[INFO] INSIGHTS")
    print("-" * 40)
    
    # Calculate some basic insights
    if dataset_count > 0 and dashboard_count > 0:
        ratio = dashboard_count / dataset_count
        print(f"Dashboard/Dataset Ratio: {ratio:.2f}")
    
    if user_count > 0 and dashboard_count > 0:
        dashboards_per_user = dashboard_count / user_count
        print(f"Dashboards per User:     {dashboards_per_user:.1f}")
    
    # Project maturity indicator based on content
    if dataset_count >= 10 and dashboard_count >= 20:
        maturity = "High"
    elif dataset_count >= 5 and dashboard_count >= 10:
        maturity = "Medium"
    elif dataset_count >= 1 or dashboard_count >= 1 or investigation_count >= 1:
        maturity = "Low"
    else:
        maturity = "Starting"
    
    print(f"Project Maturity:        {maturity}")
    
    print("\n" + "=" * 80)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Get summary statistics for a specific project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Auto-select first available project
    python get_project_summary.py
    
    # Use specific project by ID
    python get_project_summary.py 4315075c-b4d9-48c2-9520-cda63f04da7a
    python get_project_summary.py bc7f6a6d-552d-44bf-b9f7-310adf733dc0
        """
    )
    
    parser.add_argument('project_id', nargs='?',
                       help='Project ID (GUID format) - auto-selected if not provided')
    
    args = parser.parse_args()
    
    if args.project_id:
        # Use provided project ID
        project_id = args.project_id
        
        # Validate project ID format
        if len(project_id) != 36 or project_id.count('-') != 4:
            print(f"[ERROR] Invalid project ID format: {project_id}")
            print("Project ID should be in GUID format")
            return 1
        
        print(f"Fetching summary for project: {project_id}")
    else:
        # Auto-discover project
        projects = discover_projects(1, "project")
        if not projects:
            return 1
        
        project_id = projects[0].get('project_id')
        if not project_id:
            print("[ERROR] No project ID found in selected project")
            return 1
        
        show_usage_tip(Path(__file__).name, "4315075c-b4d9-48c2-9520-cda63f04da7a")
    
    print("-" * 60)
    
    # Try to get project summary using mindzie_api library
    summary_data = get_project_summary(project_id)
    
    if not summary_data:
        print(f"[ERROR] Could not retrieve project summary for {project_id}")
        print("This may be due to:")
        print("  1. Project not found")
        print("  2. Summary endpoint not implemented")
        print("  3. Library bugs with Pydantic validation")
        print("Check the project ID and ensure you have access to it")
        return 1
    
    display_project_summary(summary_data, project_id)
    return 0

if __name__ == "__main__":
    sys.exit(main())