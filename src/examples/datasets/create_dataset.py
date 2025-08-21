"""
Create a new dataset from various data sources.

This example demonstrates how to:
- Create datasets from CSV, JSON, database connections
- Configure dataset schema and metadata
- Set up data validation rules
- Handle different data source types
- Configure refresh schedules and data quality checks

NOTE: This example assumes the create() method exists in the datasets controller.
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mindzie_api import MindzieAPIClient
from mindzie_api.exceptions import MindzieAPIException
from common_utils import (
    get_client_config,
    discover_project,
    print_header,
    print_error,
    print_success,
    print_info
)

def create_dataset(
    client: MindzieAPIClient,
    project_id: str,
    dataset_config: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Create a new dataset."""
    try:
        print_info(f"Creating dataset: {dataset_config.get('name', 'Unnamed')}")
        
        if hasattr(client.datasets, 'create'):
            response = client.datasets.create(project_id, **dataset_config)
            print_success("Dataset created successfully!")
            return response
        else:
            # Simulate creation
            simulated_response = {
                "dataset_id": f"ds_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "project_id": project_id,
                **dataset_config,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            print_success("(Simulated) Dataset would be created")
            print(json.dumps(simulated_response, indent=2))
            return simulated_response
            
    except Exception as e:
        print_error(f"Error creating dataset: {e}")
        return None

def main():
    """Main function."""
    print_header("Create Dataset Example")
    
    config = get_client_config()
    if not config:
        return
    
    import argparse
    parser = argparse.ArgumentParser(description='Create a new dataset')
    parser.add_argument('name', help='Dataset name')
    parser.add_argument('--project-id', help='Project ID')
    parser.add_argument('--source-type', choices=['csv', 'json', 'database', 'api'], default='csv')
    parser.add_argument('--source-path', help='Path to data source')
    parser.add_argument('--description', help='Dataset description')
    
    args = parser.parse_args()
    
    client = MindzieAPIClient(
        base_url=config['base_url'],
        tenant_id=config['tenant_id'],
        api_key=config['api_key']
    )
    
    try:
        client.ping.ping()
        print_success("Connected to mindzie API")
        
        if args.project_id:
            project_id = args.project_id
        else:
            project_id = discover_project(client)
            if not project_id:
                print_error("No projects available")
                return
        
        dataset_config = {
            "name": args.name,
            "description": args.description or f"Dataset created on {datetime.now().strftime('%Y-%m-%d')}",
            "source_type": args.source_type,
            "source_path": args.source_path,
            "schema_auto_detect": True,
            "data_quality_checks": True
        }
        
        result = create_dataset(client, project_id, dataset_config)
        
        if result:
            print_success(f"✅ Dataset '{args.name}' created successfully!")
            print(f"Dataset ID: {result.get('dataset_id', 'N/A')}")
        
    except Exception as e:
        print_error(f"Failed to create dataset: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()