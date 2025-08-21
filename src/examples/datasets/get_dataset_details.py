"""
Get detailed information about a specific dataset.

This example demonstrates how to:
- Retrieve comprehensive dataset metadata
- Display schema and structure information
- Show data lineage and relationships
- Handle dataset permissions and access control
- Auto-discover datasets when no ID is provided
"""

import os
import sys
import json
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


def discover_dataset(client: MindzieAPIClient, project_id: str) -> Optional[str]:
    """
    Auto-discover a dataset from the project.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        
    Returns:
        Dataset ID or None if no datasets found
    """
    try:
        print_info("Discovering available datasets...")
        response = client.datasets.get_all(project_id)
        
        if not response or not response.get("Items"):
            print_info("No datasets found in this project")
            return None
        
        datasets = response["Items"]
        
        if len(datasets) == 1:
            dataset = datasets[0]
            print_success(f"Found dataset: {dataset.get('DatasetName', 'Unnamed')}")
            return dataset.get('DatasetId')
        
        # Multiple datasets - let user choose
        print_info(f"Found {len(datasets)} datasets:")
        for idx, dataset in enumerate(datasets[:10], 1):  # Show max 10
            print(f"  {idx}. {dataset.get('DatasetName', 'Unnamed')} "
                  f"(ID: {dataset.get('DatasetId', 'N/A')})")
        
        # Use the first one for demonstration
        selected = datasets[0]
        print_info(f"Using first dataset: {selected.get('DatasetName', 'Unnamed')}")
        return selected.get('DatasetId')
        
    except Exception as e:
        print_error(f"Failed to discover datasets: {e}")
        return None


def get_dataset_details(
    client: MindzieAPIClient,
    project_id: str,
    dataset_id: str,
    show_schema: bool = True,
    show_preview: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a dataset.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        dataset_id: The dataset ID
        show_schema: Whether to display schema information
        show_preview: Whether to show data preview
        
    Returns:
        Dictionary containing dataset details or None if error
    """
    try:
        print_info(f"Fetching details for dataset {dataset_id}...")
        
        # Note: Since there's no specific get_by_id method for datasets,
        # we'll get all datasets and filter
        response = client.datasets.get_all(project_id)
        
        if not response or not response.get("Items"):
            print_error("No datasets found")
            return None
        
        # Find the specific dataset
        dataset = None
        for item in response["Items"]:
            if item.get("DatasetId") == dataset_id:
                dataset = item
                break
        
        if not dataset:
            print_error(f"Dataset {dataset_id} not found")
            return None
        
        print_success(f"Retrieved dataset: {dataset.get('DatasetName', 'Unnamed')}")
        
        # Display comprehensive dataset information
        print("\n" + "="*60)
        print("DATASET DETAILS")
        print("="*60)
        
        # Basic Information
        print("\n📊 Basic Information:")
        print(f"   Name: {dataset.get('DatasetName', 'N/A')}")
        print(f"   ID: {dataset.get('DatasetId', 'N/A')}")
        print(f"   Type: {dataset.get('DatasetType', 'Unknown')}")
        print(f"   Status: {dataset.get('Status', 'Unknown')}")
        print(f"   Version: {dataset.get('Version', 'N/A')}")
        
        # Description and Documentation
        if dataset.get('Description'):
            print(f"\n📝 Description:")
            print(f"   {dataset['Description']}")
        
        # Size and Statistics
        print(f"\n📈 Statistics:")
        if dataset.get('SizeMB') is not None:
            print(f"   Size: {format_size_mb(dataset['SizeMB'])}")
        if dataset.get('CompressedSizeMB') is not None:
            print(f"   Compressed Size: {format_size_mb(dataset['CompressedSizeMB'])}")
            if dataset.get('SizeMB'):
                ratio = (1 - dataset['CompressedSizeMB'] / dataset['SizeMB']) * 100
                print(f"   Compression Ratio: {ratio:.1f}%")
        if dataset.get('RowCount') is not None:
            print(f"   Rows: {dataset['RowCount']:,}")
        if dataset.get('ColumnCount') is not None:
            print(f"   Columns: {dataset['ColumnCount']}")
        
        # Data Quality Metrics
        if dataset.get('DataQuality'):
            quality = dataset['DataQuality']
            print(f"\n✅ Data Quality:")
            if quality.get('Completeness') is not None:
                print(f"   Completeness: {quality['Completeness']:.1f}%")
            if quality.get('Accuracy') is not None:
                print(f"   Accuracy: {quality['Accuracy']:.1f}%")
            if quality.get('Consistency') is not None:
                print(f"   Consistency: {quality['Consistency']:.1f}%")
            if quality.get('NullPercentage') is not None:
                print(f"   Null Values: {quality['NullPercentage']:.1f}%")
        
        # Timestamps
        print(f"\n🕐 Timeline:")
        if dataset.get('CreatedAt'):
            print(f"   Created: {format_timestamp(dataset['CreatedAt'])}")
        if dataset.get('ModifiedAt'):
            print(f"   Last Modified: {format_timestamp(dataset['ModifiedAt'])}")
        if dataset.get('LastAccessedAt'):
            print(f"   Last Accessed: {format_timestamp(dataset['LastAccessedAt'])}")
        if dataset.get('LastRefreshedAt'):
            print(f"   Last Refreshed: {format_timestamp(dataset['LastRefreshedAt'])}")
        if dataset.get('ExpiresAt'):
            print(f"   Expires: {format_timestamp(dataset['ExpiresAt'])}")
        
        # Source Information
        if dataset.get('Source') or dataset.get('SourceType'):
            print(f"\n🔗 Source Information:")
            if dataset.get('Source'):
                print(f"   Source: {dataset['Source']}")
            if dataset.get('SourceType'):
                print(f"   Source Type: {dataset['SourceType']}")
            if dataset.get('SourceConnection'):
                print(f"   Connection: {dataset['SourceConnection']}")
            if dataset.get('RefreshSchedule'):
                print(f"   Refresh Schedule: {dataset['RefreshSchedule']}")
        
        # Schema Information
        if show_schema and dataset.get('Schema'):
            print(f"\n📋 Schema:")
            schema = dataset['Schema']
            
            if isinstance(schema, dict):
                for field_name, field_info in schema.items():
                    if isinstance(field_info, dict):
                        print(f"   • {field_name}:")
                        print(f"     - Type: {field_info.get('Type', 'Unknown')}")
                        if field_info.get('Nullable') is not None:
                            print(f"     - Nullable: {field_info['Nullable']}")
                        if field_info.get('DefaultValue') is not None:
                            print(f"     - Default: {field_info['DefaultValue']}")
                        if field_info.get('Description'):
                            print(f"     - Description: {field_info['Description']}")
                    else:
                        print(f"   • {field_name}: {field_info}")
            elif isinstance(schema, list):
                for field in schema:
                    if isinstance(field, dict):
                        name = field.get('Name', 'Unknown')
                        dtype = field.get('Type', 'Unknown')
                        print(f"   • {name}: {dtype}")
                    else:
                        print(f"   • {field}")
        
        # Tags and Categories
        if dataset.get('Tags'):
            print(f"\n🏷️  Tags:")
            for tag in dataset['Tags']:
                print(f"   • {tag}")
        
        if dataset.get('Categories'):
            print(f"\n📁 Categories:")
            for category in dataset['Categories']:
                print(f"   • {category}")
        
        # Relationships
        if dataset.get('RelatedDatasets'):
            print(f"\n🔄 Related Datasets:")
            for related in dataset['RelatedDatasets']:
                print(f"   • {related}")
        
        if dataset.get('DependentDatasets'):
            print(f"\n⬇️  Dependent Datasets:")
            for dependent in dataset['DependentDatasets']:
                print(f"   • {dependent}")
        
        # Permissions and Access
        if dataset.get('Permissions'):
            perms = dataset['Permissions']
            print(f"\n🔐 Permissions:")
            print(f"   Read: {perms.get('Read', False)}")
            print(f"   Write: {perms.get('Write', False)}")
            print(f"   Delete: {perms.get('Delete', False)}")
            print(f"   Share: {perms.get('Share', False)}")
            
            if perms.get('SharedWith'):
                print(f"   Shared With:")
                for user in perms['SharedWith']:
                    print(f"     • {user}")
        
        if dataset.get('Owner'):
            print(f"   Owner: {dataset['Owner']}")
        
        # Usage Statistics
        if dataset.get('UsageStats'):
            stats = dataset['UsageStats']
            print(f"\n📊 Usage Statistics:")
            if stats.get('AccessCount') is not None:
                print(f"   Access Count: {stats['AccessCount']:,}")
            if stats.get('QueryCount') is not None:
                print(f"   Query Count: {stats['QueryCount']:,}")
            if stats.get('AverageQueryTime') is not None:
                print(f"   Avg Query Time: {stats['AverageQueryTime']:.2f}ms")
            if stats.get('TopUsers'):
                print(f"   Top Users:")
                for user in stats['TopUsers'][:5]:
                    print(f"     • {user}")
        
        # Data Preview (if requested and available)
        if show_preview and dataset.get('Preview'):
            print(f"\n👁️  Data Preview:")
            preview = dataset['Preview']
            
            if isinstance(preview, list) and preview:
                # Show first few rows
                print("   First 5 rows:")
                for idx, row in enumerate(preview[:5], 1):
                    print(f"   Row {idx}: {json.dumps(row, indent=6)}")
        
        # Metadata
        if dataset.get('Metadata'):
            print(f"\n📎 Additional Metadata:")
            metadata = dataset['Metadata']
            for key, value in metadata.items():
                print(f"   {key}: {value}")
        
        print("\n" + "="*60)
        
        return dataset
        
    except MindzieAPIException as e:
        print_error(f"API error: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return None


def main():
    """Main function to demonstrate getting dataset details."""
    print_header("Get Dataset Details Example")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Get detailed dataset information')
    parser.add_argument('--project-id', help='Project ID (optional, will auto-discover if not provided)')
    parser.add_argument('--dataset-id', help='Dataset ID (optional, will auto-discover if not provided)')
    parser.add_argument('--no-schema', action='store_true', help='Skip schema information')
    parser.add_argument('--preview', action='store_true', help='Show data preview if available')
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
        
        # Get or discover dataset ID
        if args.dataset_id:
            dataset_id = args.dataset_id
            print_info(f"Using provided dataset ID: {dataset_id}")
        else:
            dataset_id = discover_dataset(client, project_id)
            if not dataset_id:
                print_error("No datasets available")
                return
        
        # Get dataset details
        result = get_dataset_details(
            client,
            project_id,
            dataset_id,
            show_schema=not args.no_schema,
            show_preview=args.preview
        )
        
        if result:
            print_success("\nDataset details retrieved successfully!")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to get dataset details: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()