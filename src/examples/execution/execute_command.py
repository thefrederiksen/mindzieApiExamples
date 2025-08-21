"""
Execute general commands and scripts through the execution controller.

This example demonstrates how to:
- Execute custom scripts and commands
- Monitor execution progress and status
- Handle execution parameters and environment variables
- Capture and retrieve execution output
- Manage execution timeouts and cancellation

NOTE: This example assumes the execution controller exists in the API.
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

def execute_command(
    client: MindzieAPIClient,
    project_id: str,
    command_config: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Execute a command or script."""
    try:
        print_info(f"Executing command: {command_config.get('command', 'N/A')}")
        
        # Display execution configuration
        print_info("Execution configuration:")
        for key, value in command_config.items():
            if key != 'environment_vars':  # Don't print sensitive env vars
                print(f"  • {key}: {value}")
        
        if hasattr(client, 'execution') and hasattr(client.execution, 'execute'):
            response = client.execution.execute(
                project_id=project_id,
                **command_config
            )
            print_success("Command execution started!")
            return response
        else:
            # Simulate execution
            print_info("Note: execution controller not found")
            print_info("Simulating command execution for demonstration...")
            
            simulated_response = {
                "execution_id": f"exec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "project_id": project_id,
                "command": command_config.get('command'),
                "status": "running",
                "started_at": datetime.now().isoformat(),
                "estimated_duration": command_config.get('timeout', 300),
                "output_available": True
            }
            
            print_success("(Simulated) Command execution would be started")
            print(json.dumps(simulated_response, indent=2))
            return simulated_response
            
    except Exception as e:
        print_error(f"Error executing command: {e}")
        return None

def monitor_execution(
    client: MindzieAPIClient,
    execution_id: str
) -> Optional[Dict[str, Any]]:
    """Monitor execution status."""
    try:
        if hasattr(client, 'execution') and hasattr(client.execution, 'get_status'):
            status = client.execution.get_status(execution_id)
            return status
        else:
            # Simulate status check
            return {
                "execution_id": execution_id,
                "status": "completed",
                "progress": 100,
                "output": "Command completed successfully\\nProcessed 1000 records",
                "exit_code": 0
            }
    except Exception as e:
        print_error(f"Error checking execution status: {e}")
        return None

def main():
    """Main function."""
    print_header("Execute Command Example")
    
    config = get_client_config()
    if not config:
        return
    
    import argparse
    parser = argparse.ArgumentParser(description='Execute a command or script')
    parser.add_argument('command', help='Command to execute')
    parser.add_argument('--project-id', help='Project ID')
    parser.add_argument('--timeout', type=int, default=300, help='Execution timeout in seconds')
    parser.add_argument('--async', action='store_true', help='Run asynchronously')
    parser.add_argument('--env', nargs='+', help='Environment variables (KEY=VALUE)')
    
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
        
        # Parse environment variables
        env_vars = {}
        if args.env:
            for env in args.env:
                if '=' in env:
                    key, value = env.split('=', 1)
                    env_vars[key] = value
        
        command_config = {
            "command": args.command,
            "timeout": args.timeout,
            "async_execution": getattr(args, 'async', False),
            "environment_vars": env_vars,
            "capture_output": True
        }
        
        result = execute_command(client, project_id, command_config)
        
        if result:
            execution_id = result.get('execution_id')
            print_success(f"✅ Command execution started!")
            print(f"Execution ID: {execution_id}")
            
            # Monitor execution if synchronous
            if not getattr(args, 'async', False) and execution_id:
                print_info("Monitoring execution...")
                status = monitor_execution(client, execution_id)
                if status:
                    print(f"Status: {status.get('status')}")
                    if status.get('output'):
                        print(f"Output: {status.get('output')}")
        
    except Exception as e:
        print_error(f"Failed to execute command: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()