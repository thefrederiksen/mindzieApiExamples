#!/usr/bin/env python
"""
List all datasets for a project.

This example demonstrates how to:
- List all datasets for a specific project
- Display dataset metadata and properties
- Auto-discover projects when no ID is provided
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

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

# Import utility functions from projects directory
sys.path.append(str(Path(__file__).parent.parent / 'projects'))
from api_utils import get_client, load_credentials


def format_timestamp(timestamp_str):
    """Format ISO timestamp to readable format."""
    if not timestamp_str:
        return "N/A"
    try:
        if 'T' in timestamp_str:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return str(timestamp_str)[:19] if len(str(timestamp_str)) > 19 else str(timestamp_str)


def format_size_mb(size_mb):
    """Format size in MB to human readable format."""
    if size_mb is None:
        return "N/A"
    if size_mb < 1:
        return f"{size_mb * 1024:.1f} KB"
    elif size_mb < 1024:
        return f"{size_mb:.1f} MB"
    else:
        return f"{size_mb / 1024:.1f} GB"


def main():
    """Main function to demonstrate dataset listing."""
    print("=" * 70)
    print("mindzie Dataset List")
    print("=" * 70)
    
    # Load credentials
    credentials = load_credentials()
    if not credentials:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='List datasets for a project')
    parser.add_argument('--project-id', help='Project ID (optional, will auto-discover if not provided)')
    parser.add_argument('--brief', action='store_true', help='Show brief output only')
    args = parser.parse_args()
    
    # Initialize client
    client = get_client()
    if not client:
        return
    
    try:
        # Test connectivity
        print("Testing connectivity...")
        client.ping.ping()
        print("Connected to mindzie API")
        
        # Get project ID
        if args.project_id:
            project_id = args.project_id
            print(f"Using provided project ID: {project_id}")
        else:
            # Auto-discover project (simplified version)
            try:
                projects = client.projects.list_projects()
                if not projects:
                    print("No projects available")
                    return
                project_id = projects[0].get('project_id')
                print(f"Using discovered project ID: {project_id}")
            except Exception as e:
                print(f"Could not discover projects: {e}")
                return
        
        # List datasets
        print(f"\\nFetching datasets for project {project_id}...")
        
        try:
            response = client.datasets.get_all(project_id)
            
            if not response:
                print("No response received from API")
                return
                
            datasets = response.get("Items", [])
            total_count = len(datasets)
            
            if total_count == 0:
                print("No datasets found for this project")
                return
                
            print(f"Found {total_count} dataset(s)")
            
            # Display dataset information
            for idx, dataset in enumerate(datasets, 1):
                print(f"\\n{idx}. Dataset: {dataset.get('DatasetName', 'Unnamed')}")
                
                if not args.brief:
                    print(f"   - Dataset ID: {dataset.get('DatasetId', 'N/A')}")
                    print(f"   - Type: {dataset.get('DatasetType', 'Unknown')}")
                    print(f"   - Status: {dataset.get('Status', 'Unknown')}")
                    
                    if dataset.get('SizeMB'):
                        print(f"   - Size: {format_size_mb(dataset['SizeMB'])}")
                    if dataset.get('RowCount'):
                        print(f"   - Rows: {dataset['RowCount']:,}")
                    if dataset.get('CreatedAt'):
                        print(f"   - Created: {format_timestamp(dataset['CreatedAt'])}")
            
            print("\\nDataset listing completed successfully!")
            
        except MindzieAPIException as e:
            print(f"API error: {e}")
        except Exception as e:
            print(f"Error listing datasets: {e}")
        
    except KeyboardInterrupt:
        print("\\nOperation cancelled by user")
    except Exception as e:
        print(f"Failed to list datasets: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()