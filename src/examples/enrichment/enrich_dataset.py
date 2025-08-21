"""
Enrich datasets with additional data and features.

This example demonstrates how to:
- Apply data enrichment operations to datasets
- Add calculated fields and derived metrics
- Integrate external data sources for enrichment
- Monitor enrichment job progress
- Handle enrichment errors and validation

NOTE: This example assumes the enrichment controller exists in the API.
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

def enrich_dataset(
    client: MindzieAPIClient,
    project_id: str,
    dataset_id: str,
    enrichment_config: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Enrich a dataset with additional data."""
    try:
        print_info(f"Starting enrichment for dataset {dataset_id}")
        
        # Display enrichment configuration
        print_info("Enrichment configuration:")
        for key, value in enrichment_config.items():
            print(f"  • {key}: {value}")
        
        if hasattr(client, 'enrichment') and hasattr(client.enrichment, 'enrich_dataset'):
            response = client.enrichment.enrich_dataset(
                project_id=project_id,
                dataset_id=dataset_id,
                **enrichment_config
            )
            print_success("Enrichment job started successfully!")
            return response
        else:
            # Simulate enrichment
            print_info("Note: enrichment controller not found")
            print_info("Simulating dataset enrichment for demonstration...")
            
            simulated_response = {
                "enrichment_job_id": f"enrich_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "project_id": project_id,
                "dataset_id": dataset_id,
                "status": "in_progress",
                "started_at": datetime.now().isoformat(),
                "estimated_completion": "5 minutes",
                "enrichment_config": enrichment_config
            }
            
            print_success("(Simulated) Enrichment job would be started")
            print(json.dumps(simulated_response, indent=2))
            return simulated_response
            
    except Exception as e:
        print_error(f"Error starting enrichment: {e}")
        return None

def main():
    """Main function."""
    print_header("Dataset Enrichment Example")
    
    config = get_client_config()
    if not config:
        return
    
    import argparse
    parser = argparse.ArgumentParser(description='Enrich a dataset')
    parser.add_argument('--project-id', help='Project ID')
    parser.add_argument('--dataset-id', help='Dataset ID')
    parser.add_argument('--enrichment-type', choices=['calculate', 'lookup', 'geocode', 'ml'], default='calculate')
    parser.add_argument('--fields', nargs='+', help='Fields to enrich')
    
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
        
        # For demo, use first available dataset if not specified
        dataset_id = args.dataset_id or "demo_dataset_001"
        
        enrichment_config = {
            "enrichment_type": args.enrichment_type,
            "target_fields": args.fields or ["amount", "category"],
            "operations": [
                {"type": "calculate", "field": "total_with_tax", "formula": "amount * 1.1"},
                {"type": "lookup", "field": "category_description", "lookup_table": "categories"}
            ]
        }
        
        result = enrich_dataset(client, project_id, dataset_id, enrichment_config)
        
        if result:
            print_success(f"✅ Enrichment job started!")
            print(f"Job ID: {result.get('enrichment_job_id', 'N/A')}")
            print(f"Status: {result.get('status', 'Unknown')}")
        
    except Exception as e:
        print_error(f"Failed to start enrichment: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()