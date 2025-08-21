#!/usr/bin/env python
"""
List all projects in your mindzie tenant.

This script demonstrates how to retrieve and display all projects
associated with your tenant using the mindzie-api package.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

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

# Import the mindzie API library
from mindzie_api import MindzieAPIClient
from mindzie_api.exceptions import (
    MindzieAPIException, AuthenticationError, TimeoutError
)

# Import our utility functions
from api_utils import get_client, load_credentials

def format_date(date_str):
    """Format ISO date string to readable format."""
    if not date_str:
        return "N/A"
    try:
        # Handle different date formats
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return str(date_str)[:19] if len(str(date_str)) > 19 else str(date_str)

def main():
    print("=" * 70)
    print("mindzie Project List")
    print("=" * 70)
    
    # Get client using the utility function
    client = get_client()
    if not client:
        print("\n[ERROR] Failed to create API client!")
        print("\nSet environment variables or create .env file with:")
        print("MINDZIE_TENANT_ID=your-tenant-id")
        print("MINDZIE_API_KEY=your-api-key")
        return 1
    
    tenant_id, _, _ = load_credentials()
    print(f"\nTenant ID: {tenant_id}")
    print("-" * 70)
    
    try:
        print("\nFetching projects using mindzie_api library...")
        
        # Use the mindzie library to get projects
        projects_list = client.projects.list_projects()
        total = len(projects_list)
        
        if total == 0:
            print("\nNo projects found in this tenant.")
            return 0
        
        print(f"\nFound {total} project(s):\n")
        print("-" * 70)
        
        # Display each project using the Project model fields
        for i, project in enumerate(projects_list, 1):
            name = project.project_name or 'Unnamed Project'
            
            print(f"\n{i}. {name}")
            print("   " + "=" * 65)
            
            # Project ID
            if project.project_id:
                print(f"   ID:           {project.project_id}")
            
            # Description
            if project.project_description:
                desc = project.project_description
                if len(desc) > 60:
                    desc = desc[:57] + "..."
                print(f"   Description:  {desc}")
            
            # Dates
            if project.date_created:
                print(f"   Created:      {format_date(project.date_created)}")
            
            if project.date_modified:
                print(f"   Updated:      {format_date(project.date_modified)}")
            
            # Statistics
            stats = []
            
            if project.dataset_count > 0:
                stats.append(f"Datasets: {project.dataset_count}")
            
            if hasattr(project, 'investigation_count') and project.investigation_count > 0:
                stats.append(f"Investigations: {project.investigation_count}")
            
            if project.dashboard_count > 0:
                stats.append(f"Dashboards: {project.dashboard_count}")
            
            if project.user_count > 0:
                stats.append(f"Users: {project.user_count}")
            
            if stats:
                print(f"   Stats:        {' | '.join(stats)}")
            
            # Active status
            status = "Active" if project.is_active else "Inactive"
            print(f"   Status:       {status}")
        
        print("\n" + "=" * 70)
        print(f"Total: {total} project(s)")
        print("=" * 70)
        
    except AuthenticationError:
        print("\n[ERROR] Authentication failed - check your credentials")
        return 1
    except TimeoutError:
        print("\n[ERROR] Request timed out")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Failed to retrieve projects: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify your credentials are correct")
        print("3. Ensure you have access to the tenant")
        return 1
    finally:
        client.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())