#!/usr/bin/env python
"""
Download execution packages from mindzie Studio action executions.

This example demonstrates how to download result packages from completed
action executions, including handling different download formats and
saving files locally.
"""

import os
import sys
from pathlib import Path
import mimetypes
from urllib.parse import urlparse

# Add parent directory to path for shared utilities
sys.path.append(str(Path(__file__).parent.parent))

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

# Import from parent directory utilities
from common_utils import create_client, handle_api_error, print_section, print_success, print_error, print_info

def download_execution_package(client, project_id: str, execution_id: str, download_dir: str = None):
    """Download the execution package for a specific execution."""
    print_section(f"Downloading Package for Execution: {execution_id}")
    
    try:
        # First, get execution details to check if it's completed
        execution = client.action_executions.get_by_id(project_id, execution_id)
        
        if not execution:
            print_error("Execution not found")
            return None
        
        status = execution.get('status', 'Unknown')
        if status.lower() not in ['completed', 'finished', 'success']:
            print_error(f"Execution is not completed (status: {status})")
            print_info("Only completed executions have downloadable packages")
            return None
        
        print_success(f"✓ Execution is completed (status: {status})")
        
        # Try to download the package
        package_response = client.action_executions.download_package(project_id, execution_id)
        
        if package_response:
            print_success("✓ Package download request successful")
            return save_package(package_response, execution_id, download_dir)
        else:
            print_error("No package data received")
            return None
            
    except Exception as e:
        print_error(f"Failed to download package: {e}")
        return None

def save_package(package_data, execution_id: str, download_dir: str = None):
    """Save the package data to a local file."""
    print_section("Saving Package")
    
    # Determine download directory
    if download_dir is None:
        download_dir = Path.cwd() / "downloads"
    else:
        download_dir = Path(download_dir)
    
    # Create download directory if it doesn't exist
    download_dir.mkdir(parents=True, exist_ok=True)
    print_info(f"Download directory: {download_dir}")
    
    # Handle different response formats
    if isinstance(package_data, dict):
        # API might return metadata with download URL
        if 'downloadUrl' in package_data:
            print_info("Received download URL - would need to implement URL download")
            return package_data['downloadUrl']
        elif 'packageData' in package_data:
            package_content = package_data['packageData']
        elif 'data' in package_data:
            package_content = package_data['data']
        else:
            # Try to save the entire response as JSON
            package_content = package_data
    else:
        # Direct content
        package_content = package_data
    
    # Determine file extension based on content
    file_extension = determine_file_extension(package_content)
    filename = f"execution_{execution_id}_package{file_extension}"
    file_path = download_dir / filename
    
    try:
        # Save based on content type
        if isinstance(package_content, (bytes, bytearray)):
            # Binary data
            with open(file_path, 'wb') as f:
                f.write(package_content)
        elif isinstance(package_content, str):
            # Text data
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(package_content)
        else:
            # JSON or other structured data
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(package_content, f, indent=2)
        
        file_size = file_path.stat().st_size
        print_success(f"✓ Package saved: {file_path}")
        print_info(f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        return str(file_path)
        
    except Exception as e:
        print_error(f"Failed to save package: {e}")
        return None

def determine_file_extension(content):
    """Determine appropriate file extension based on content."""
    if isinstance(content, (bytes, bytearray)):
        # Check for common binary formats
        if content.startswith(b'PK'):  # ZIP file
            return '.zip'
        elif content.startswith(b'%PDF'):  # PDF file
            return '.pdf'
        elif content.startswith(b'\x89PNG'):  # PNG image
            return '.png'
        elif content.startswith(b'\xff\xd8\xff'):  # JPEG image
            return '.jpg'
        else:
            return '.bin'
    
    elif isinstance(content, str):
        # Check for common text formats
        content_lower = content.lower().strip()
        if content_lower.startswith('<?xml') or '<' in content and '>' in content:
            return '.xml'
        elif content_lower.startswith('{') or content_lower.startswith('['):
            return '.json'
        elif 'csv' in content_lower or ',' in content:
            return '.csv'
        else:
            return '.txt'
    
    else:
        # Structured data - save as JSON
        return '.json'

def analyze_package_content(file_path: str):
    """Analyze the downloaded package content."""
    print_section("Package Analysis")
    
    if not file_path or not Path(file_path).exists():
        print_error("Package file not found")
        return
    
    file_path = Path(file_path)
    file_size = file_path.stat().st_size
    
    print(f"File: {file_path.name}")
    print(f"Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"Extension: {file_path.suffix}")
    
    # Try to analyze content based on extension
    try:
        if file_path.suffix.lower() == '.json':
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print_info("JSON content structure:")
            if isinstance(data, dict):
                print(f"  Object with {len(data)} keys: {list(data.keys())[:5]}")
            elif isinstance(data, list):
                print(f"  Array with {len(data)} items")
            else:
                print(f"  {type(data).__name__}: {str(data)[:100]}")
        
        elif file_path.suffix.lower() in ['.txt', '.csv', '.xml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(500)  # Read first 500 chars
            print_info("Text content preview:")
            print(content[:200] + ("..." if len(content) > 200 else ""))
        
        elif file_path.suffix.lower() == '.zip':
            print_info("ZIP archive - use your preferred ZIP tool to extract")
        
        else:
            print_info("Binary content - use appropriate tools to view")
    
    except Exception as e:
        print_info(f"Could not analyze content: {e}")

def main():
    """Main function to download execution packages."""
    print("mindzie-api Download Execution Package Example")
    print("=" * 50)
    
    # Create client
    client = create_client()
    if not client:
        return 1
    
    try:
        # Get available projects
        print_section("Getting Available Projects")
        projects_response = client.projects.get_projects()
        projects = projects_response.get('projects', [])
        
        if not projects:
            print_error("No projects found. Please create a project first.")
            return 1
        
        # Show available projects
        print("Available projects:")
        for i, project in enumerate(projects):
            print(f"  {i+1}. {project.get('name', 'Unknown')} (ID: {project['id']})")
        
        # Get user's project choice
        if len(projects) == 1:
            selected_project = projects[0]
            print_info(f"Using only available project: {selected_project.get('name', 'Unknown')}")
        else:
            try:
                choice = input(f"\nSelect a project (1-{len(projects)}): ").strip()
                project_index = int(choice) - 1
                if 0 <= project_index < len(projects):
                    selected_project = projects[project_index]
                else:
                    print_error("Invalid project selection.")
                    return 1
            except (ValueError, KeyboardInterrupt):
                print_error("Invalid input or cancelled.")
                return 1
        
        project_id = selected_project['id']
        project_name = selected_project.get('name', 'Unknown')
        
        print_success(f"Selected project: {project_name} (ID: {project_id})")
        
        # Get execution ID from user
        print_section("Execution Selection")
        print_info("You need to provide an execution ID to download its package.")
        print_info("Execution IDs are GUIDs from completed action executions.")
        print_info("Use get_action_executions.py or get_last_execution.py to find execution IDs.")
        
        try:
            execution_id = input("\nEnter the Execution ID: ").strip()
            if not execution_id:
                print_error("Execution ID is required.")
                return 1
        except KeyboardInterrupt:
            print_error("Cancelled.")
            return 1
        
        # Optional: Get download directory
        print_section("Download Location")
        print_info("Packages will be saved to a 'downloads' directory by default.")
        try:
            custom_dir = input("Enter custom download directory (or press Enter for default): ").strip()
            download_dir = custom_dir if custom_dir else None
        except KeyboardInterrupt:
            download_dir = None
        
        # Download the package
        saved_file = download_execution_package(client, project_id, execution_id, download_dir)
        
        if saved_file:
            # Analyze the downloaded package
            analyze_package_content(saved_file)
            
            print_section("Summary")
            print_success("✓ Successfully downloaded execution package")
            print_info(f"Package saved to: {saved_file}")
            print_info("You can now examine the package contents using appropriate tools.")
        else:
            print_section("Summary")
            print_error("Failed to download execution package")
            print_info("Please verify the execution ID and ensure the execution is completed.")
    
    except Exception as e:
        handle_api_error(e, "downloading execution package")
        return 1
    
    finally:
        client.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())