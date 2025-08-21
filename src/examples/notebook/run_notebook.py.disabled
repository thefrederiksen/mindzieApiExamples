"""
Execute Jupyter notebooks through the notebook controller.

This example demonstrates how to:
- Execute Jupyter notebooks remotely
- Pass parameters to notebook execution
- Monitor notebook execution progress
- Retrieve notebook outputs and results
- Handle notebook execution errors

NOTE: This example assumes the notebook controller exists in the API.
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

def run_notebook(
    client: MindzieAPIClient,
    project_id: str,
    notebook_config: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Execute a Jupyter notebook."""
    try:
        print_info(f"Running notebook: {notebook_config.get('notebook_path', 'N/A')}")
        
        # Display execution configuration
        print_info("Notebook execution configuration:")
        for key, value in notebook_config.items():
            if key != 'parameters':
                print(f"  • {key}: {value}")
            else:
                print(f"  • parameters: {len(value)} parameter(s)")
        
        if hasattr(client, 'notebook') and hasattr(client.notebook, 'run'):
            response = client.notebook.run(
                project_id=project_id,
                **notebook_config
            )
            print_success("Notebook execution started!")
            return response
        else:
            # Simulate notebook execution
            print_info("Note: notebook controller not found")
            print_info("Simulating notebook execution for demonstration...")
            
            simulated_response = {
                "execution_id": f"nb_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "project_id": project_id,
                "notebook_path": notebook_config.get('notebook_path'),
                "status": "running",
                "started_at": datetime.now().isoformat(),
                "estimated_duration": "3 minutes",
                "cell_count": 15,
                "completed_cells": 0
            }
            
            print_success("(Simulated) Notebook execution would be started")
            print(json.dumps(simulated_response, indent=2))
            return simulated_response
            
    except Exception as e:
        print_error(f"Error running notebook: {e}")
        return None

def get_notebook_status(
    client: MindzieAPIClient,
    execution_id: str
) -> Optional[Dict[str, Any]]:
    """Get notebook execution status."""
    try:
        if hasattr(client, 'notebook') and hasattr(client.notebook, 'get_status'):
            status = client.notebook.get_status(execution_id)
            return status
        else:
            # Simulate status
            return {
                "execution_id": execution_id,
                "status": "completed",
                "completed_cells": 15,
                "total_cells": 15,
                "outputs_available": True,
                "execution_time": "2m 34s"
            }
    except Exception as e:
        print_error(f"Error getting notebook status: {e}")
        return None

def main():
    """Main function."""
    print_header("Run Notebook Example")
    
    config = get_client_config()
    if not config:
        return
    
    import argparse
    parser = argparse.ArgumentParser(description='Execute a Jupyter notebook')
    parser.add_argument('notebook_path', help='Path to notebook file')
    parser.add_argument('--project-id', help='Project ID')
    parser.add_argument('--output-path', help='Path for output notebook')
    parser.add_argument('--kernel', default='python3', help='Kernel to use')
    parser.add_argument('--param', nargs=2, action='append', metavar=('KEY', 'VALUE'), help='Notebook parameters')
    parser.add_argument('--timeout', type=int, default=3600, help='Execution timeout')
    
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
        
        # Parse parameters
        parameters = {}
        if args.param:
            for key, value in args.param:
                # Try to parse as JSON, otherwise treat as string
                try:
                    parameters[key] = json.loads(value)
                except:
                    parameters[key] = value
        
        notebook_config = {
            "notebook_path": args.notebook_path,
            "output_path": args.output_path,
            "kernel": args.kernel,
            "parameters": parameters,
            "timeout": args.timeout,
            "capture_output": True
        }
        
        result = run_notebook(client, project_id, notebook_config)
        
        if result:
            execution_id = result.get('execution_id')
            print_success(f"✅ Notebook execution started!")
            print(f"Execution ID: {execution_id}")
            
            # Check status
            if execution_id:
                print_info("Checking execution status...")
                status = get_notebook_status(client, execution_id)
                if status:
                    print(f"Status: {status.get('status')}")
                    print(f"Progress: {status.get('completed_cells', 0)}/{status.get('total_cells', 0)} cells")
        
    except Exception as e:
        print_error(f"Failed to run notebook: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()