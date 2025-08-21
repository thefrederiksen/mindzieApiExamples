#!/usr/bin/env python
"""
Get detailed information for a specific project.

This script retrieves and displays comprehensive information about a project
including metadata, statistics, configuration, and timestamps.

Usage:
    python get_project_details.py                   # Auto-select first project
    python get_project_details.py <project_id>      # Use specific project

Examples:
    # Auto-select first available project
    python get_project_details.py
    
    # Use specific project by ID
    python get_project_details.py 4315075c-b4d9-48c2-9520-cda63f04da7a
    
    # Other example projects
    python get_project_details.py bc7f6a6d-552d-44bf-b9f7-310adf733dc0
    python get_project_details.py 78b05a9c-aa81-4df5-bc0f-5fc055cc4887
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
from api_utils import get_project_by_id, discover_projects, show_usage_tip

def format_date(date_str):
    """Format ISO date string to readable format."""
    if not date_str:
        return "N/A"
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        return str(date_str)

def get_project_details(project_id):
    """Get detailed project information by ID using MindzieAPIClient."""
    # Use the utility function which handles the API client properly
    return get_project_by_id(project_id)

def display_project_details(project_data):
    """Display formatted project details."""
    if not project_data:
        return
    
    print("=" * 80)
    print("PROJECT DETAILS")
    print("=" * 80)
    
    # Basic Information
    print("\n[INFO] BASIC INFORMATION")
    print("-" * 40)
    
    name = project_data.get('project_name', 'Unknown')
    print(f"Name:              {name}")
    
    project_id = project_data.get('project_id')
    if project_id:
        print(f"ID:                {project_id}")
    
    description = project_data.get('project_description')
    if description:
        print(f"Description:       {description}")
    
    # Timestamps
    print("\n[INFO] TIMESTAMPS")
    print("-" * 40)
    
    created = project_data.get('date_created')
    if created:
        print(f"Created:           {format_date(created)}")
    
    updated = project_data.get('date_modified')
    if updated:
        print(f"Last Updated:      {format_date(updated)}")
    
    # Statistics
    print("\n[INFO] STATISTICS")
    print("-" * 40)
    
    dataset_count = project_data.get('dataset_count', 0)
    investigation_count = project_data.get('investigation_count', 0)
    dashboard_count = project_data.get('dashboard_count', 0)
    user_count = project_data.get('user_count', 0)
    
    print(f"Datasets:          {dataset_count}")
    print(f"Investigations:    {investigation_count}")
    print(f"Dashboards:        {dashboard_count}")
    print(f"Users:             {user_count}")
    
    # Status and Configuration
    print("\n[INFO] STATUS & CONFIGURATION")
    print("-" * 40)
    
    is_active = project_data.get('is_active', True)
    status = 'Active' if is_active else 'Inactive'
    print(f"Status:            {status}")
    print(f"Active:            {'Yes' if is_active else 'No'}")
    
    # Additional metadata if available
    print("\n[INFO] ADDITIONAL INFORMATION")
    print("-" * 40)
    
    for key, value in project_data.items():
        if key not in ['project_name', 'project_id', 'project_description', 
                      'date_created', 'date_modified', 'dataset_count', 
                      'investigation_count', 'dashboard_count', 'user_count',
                      'is_active', 'tenant_id', 'created_by', 'modified_by']:
            if value is not None and value != "":
                # Format the key nicely
                formatted_key = key.replace('_', ' ').title()
                print(f"{formatted_key:<18} {value}")
    
    print("\n" + "=" * 80)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Get detailed information for a specific project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Auto-select first available project
    python get_project_details.py
    
    # Use specific project by ID
    python get_project_details.py 4315075c-b4d9-48c2-9520-cda63f04da7a
    python get_project_details.py bc7f6a6d-552d-44bf-b9f7-310adf733dc0
    python get_project_details.py 78b05a9c-aa81-4df5-bc0f-5fc055cc4887
        """
    )
    
    parser.add_argument('project_id', nargs='?',
                       help='Project ID (GUID format) - auto-selected if not provided')
    
    args = parser.parse_args()
    
    if args.project_id:
        # Use provided project ID
        project_id = args.project_id
        
        # Validate project ID format (basic GUID check)
        if len(project_id) != 36 or project_id.count('-') != 4:
            print(f"[ERROR] Invalid project ID format: {project_id}")
            print("Project ID should be in GUID format (e.g., 12345678-1234-1234-1234-123456789012)")
            return 1
        
        print(f"Fetching details for project: {project_id}")
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
    
    # Get project details
    project_data = get_project_details(project_id)
    
    if project_data:
        display_project_details(project_data)
        return 0
    else:
        print("\nFailed to retrieve project details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())