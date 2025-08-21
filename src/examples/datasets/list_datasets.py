"""
List all datasets for a project.

This example demonstrates how to:
- List all datasets for a specific project
- Handle pagination for large dataset collections
- Display dataset metadata and properties
- Auto-discover projects when no ID is provided
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mindzie_api import MindzieAPIClient
from mindzie_api.exceptions import MindzieAPIException
from common_utils import (
    get_client_config,
    discover_project,
    format_timestamp,
    format_size_mb,
    print_header,
    print_error,
    print_success,
    print_info
)


def list_datasets(
    client: MindzieAPIClient,
    project_id: str,
    show_details: bool = True
) -> Optional[Dict[str, Any]]:
    """
    List all datasets for a project.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        show_details: Whether to show detailed information
        
    Returns:
        Dictionary containing dataset information or None if error
    """
    try:
        print_info(f"Fetching datasets for project {project_id}...")
        
        # Get datasets from the API
        response = client.datasets.get_all(project_id)
        
        if not response:
            print_info("No response received from API")
            return None
            
        # Check if we have datasets
        datasets = response.get("Items", [])
        total_count = len(datasets)
        
        if total_count == 0:
            print_info("No datasets found for this project")
            return response
            
        print_success(f"Found {total_count} dataset(s)")
        
        # Display dataset information
        for idx, dataset in enumerate(datasets, 1):
            print(f"\n{idx}. Dataset: {dataset.get('DatasetName', 'Unnamed')}")
            
            if show_details:
                # Basic Information
                print("   Basic Information:")
                print(f"   - Dataset ID: {dataset.get('DatasetId', 'N/A')}")
                print(f"   - Type: {dataset.get('DatasetType', 'Unknown')}")
                print(f"   - Status: {dataset.get('Status', 'Unknown')}")
                
                # Size and Statistics
                if dataset.get('SizeMB'):
                    print(f"   - Size: {format_size_mb(dataset['SizeMB'])}")
                if dataset.get('RowCount'):
                    print(f"   - Rows: {dataset['RowCount']:,}")
                if dataset.get('ColumnCount'):
                    print(f"   - Columns: {dataset['ColumnCount']}")
                
                # Timestamps
                if dataset.get('CreatedAt'):
                    print(f"   - Created: {format_timestamp(dataset['CreatedAt'])}")
                if dataset.get('ModifiedAt'):
                    print(f"   - Modified: {format_timestamp(dataset['ModifiedAt'])}")
                if dataset.get('LastAccessedAt'):
                    print(f"   - Last Accessed: {format_timestamp(dataset['LastAccessedAt'])}")
                
                # Description
                if dataset.get('Description'):
                    print(f"   - Description: {dataset['Description']}")
                
                # Tags
                if dataset.get('Tags'):
                    tags = ", ".join(dataset['Tags'])
                    print(f"   - Tags: {tags}")
                
                # Source Information
                if dataset.get('Source'):
                    print(f"   - Source: {dataset['Source']}")
                if dataset.get('SourceType'):
                    print(f"   - Source Type: {dataset['SourceType']}")
                
                # Schema Information
                if dataset.get('Schema'):
                    schema = dataset['Schema']
                    if isinstance(schema, dict):
                        print("   - Schema:")
                        for field, field_type in schema.items():
                            print(f"     • {field}: {field_type}")
                
                # Permissions
                if dataset.get('Permissions'):
                    perms = dataset['Permissions']
                    print(f"   - Permissions: Read={perms.get('Read', False)}, "
                          f"Write={perms.get('Write', False)}, "
                          f"Delete={perms.get('Delete', False)}")
        
        # Summary statistics
        if total_count > 1:
            print(f"\n" + "="*50)
            print("Summary Statistics:")
            
            # Calculate totals
            total_size = sum(d.get('SizeMB', 0) for d in datasets)
            total_rows = sum(d.get('RowCount', 0) for d in datasets)
            
            print(f"- Total Datasets: {total_count}")
            if total_size > 0:
                print(f"- Total Size: {format_size_mb(total_size)}")
            if total_rows > 0:
                print(f"- Total Rows: {total_rows:,}")
            
            # Group by type
            types = {}
            for dataset in datasets:
                dtype = dataset.get('DatasetType', 'Unknown')
                types[dtype] = types.get(dtype, 0) + 1
            
            if types:
                print("- By Type:")
                for dtype, count in sorted(types.items()):
                    print(f"  • {dtype}: {count}")
        
        return response
        
    except MindzieAPIException as e:
        print_error(f"API error: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return None


def main():
    """Main function to demonstrate dataset listing."""
    print_header("List Datasets Example")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='List datasets for a project')
    parser.add_argument('--project-id', help='Project ID (optional, will auto-discover if not provided)')
    parser.add_argument('--brief', action='store_true', help='Show brief output only')
    args = parser.parse_args()
    
    # Initialize client
    client = MindzieAPIClient(
        base_url=config['base_url'],
        tenant_id=config['tenant_id'],
        api_key=config['api_key']
    )
    
    try:
        # Test connectivity
        print_info("Testing connectivity...")
        client.ping.ping()
        print_success("Connected to mindzie API")
        
        # Get or discover project ID
        if args.project_id:
            project_id = args.project_id
            print_info(f"Using provided project ID: {project_id}")
        else:
            project_id = discover_project(client)
            if not project_id:
                print_error("No projects available")
                return
        
        # List datasets
        result = list_datasets(
            client,
            project_id,
            show_details=not args.brief
        )
        
        if result:
            print_success("\nDataset listing completed successfully!")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to list datasets: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()