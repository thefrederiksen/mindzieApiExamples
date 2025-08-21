"""
List all investigations for a project with pagination support.

This example demonstrates how to:
- List investigations with pagination
- Filter investigations by status and type
- Sort investigations by various criteria
- Display investigation metadata
- Handle large investigation collections efficiently
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mindzie_api import MindzieAPIClient
from mindzie_api.exceptions import MindzieAPIException
from common_utils import (
    get_client_config,
    discover_project,
    format_timestamp,
    print_header,
    print_error,
    print_success,
    print_info
)


def list_investigations(
    client: MindzieAPIClient,
    project_id: str,
    page: int = 1,
    page_size: int = 10,
    show_details: bool = True
) -> Optional[Dict[str, Any]]:
    """
    List investigations for a project with pagination.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        page: Page number (1-based)
        page_size: Number of items per page
        show_details: Whether to show detailed information
        
    Returns:
        Dictionary containing investigation information or None if error
    """
    try:
        print_info(f"Fetching investigations for project {project_id} (Page {page})...")
        
        # Get investigations from the API
        response = client.investigations.get_all(
            project_id=project_id,
            page=page,
            page_size=page_size
        )
        
        if not response:
            print_info("No response received from API")
            return None
        
        # Extract investigation data
        investigations = response.get("Investigations", [])
        total_count = response.get("TotalCount", 0)
        total_pages = response.get("TotalPages", 1)
        
        if total_count == 0:
            print_info("No investigations found for this project")
            return response
        
        print_success(f"Found {total_count} investigation(s) total")
        print_info(f"Showing page {page} of {total_pages} ({len(investigations)} items)")
        
        # Display investigation information
        for idx, investigation in enumerate(investigations, 1 + (page - 1) * page_size):
            print(f"\n{idx}. Investigation: {investigation.get('InvestigationName', 'Unnamed')}")
            
            if show_details:
                # Basic Information
                print("   Basic Information:")
                print(f"   - Investigation ID: {investigation.get('InvestigationId', 'N/A')}")
                print(f"   - Type: {investigation.get('InvestigationType', 'Unknown')}")
                print(f"   - Status: {investigation.get('Status', 'Unknown')}")
                
                # Priority and Severity
                if investigation.get('Priority'):
                    priority = investigation['Priority']
                    priority_icon = {
                        'Critical': '🔴',
                        'High': '🟠',
                        'Medium': '🟡',
                        'Low': '🟢'
                    }.get(priority, '⚪')
                    print(f"   - Priority: {priority_icon} {priority}")
                
                if investigation.get('Severity'):
                    print(f"   - Severity: {investigation['Severity']}")
                
                # Description
                if investigation.get('Description'):
                    desc = investigation['Description']
                    if len(desc) > 100:
                        desc = desc[:97] + "..."
                    print(f"   - Description: {desc}")
                
                # Owner and Assignment
                if investigation.get('Owner'):
                    print(f"   - Owner: {investigation['Owner']}")
                if investigation.get('AssignedTo'):
                    print(f"   - Assigned To: {investigation['AssignedTo']}")
                if investigation.get('Team'):
                    print(f"   - Team: {investigation['Team']}")
                
                # Timestamps
                if investigation.get('CreatedAt'):
                    print(f"   - Created: {format_timestamp(investigation['CreatedAt'])}")
                if investigation.get('StartedAt'):
                    print(f"   - Started: {format_timestamp(investigation['StartedAt'])}")
                if investigation.get('CompletedAt'):
                    print(f"   - Completed: {format_timestamp(investigation['CompletedAt'])}")
                if investigation.get('LastModifiedAt'):
                    print(f"   - Last Modified: {format_timestamp(investigation['LastModifiedAt'])}")
                
                # Duration and Progress
                if investigation.get('Duration'):
                    duration = investigation['Duration']
                    if isinstance(duration, (int, float)):
                        hours = duration / 3600
                        print(f"   - Duration: {hours:.1f} hours")
                    else:
                        print(f"   - Duration: {duration}")
                
                if investigation.get('Progress') is not None:
                    progress = investigation['Progress']
                    bar_length = 20
                    filled = int(bar_length * progress / 100)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    print(f"   - Progress: [{bar}] {progress}%")
                
                # Findings and Results
                if investigation.get('FindingsCount') is not None:
                    print(f"   - Findings: {investigation['FindingsCount']}")
                if investigation.get('IssuesFound') is not None:
                    print(f"   - Issues Found: {investigation['IssuesFound']}")
                if investigation.get('RecommendationsCount') is not None:
                    print(f"   - Recommendations: {investigation['RecommendationsCount']}")
                
                # Data Sources
                if investigation.get('DataSources'):
                    sources = investigation['DataSources']
                    if isinstance(sources, list):
                        print(f"   - Data Sources: {', '.join(sources[:3])}")
                        if len(sources) > 3:
                            print(f"     (and {len(sources) - 3} more...)")
                
                # Tags
                if investigation.get('Tags'):
                    tags = investigation['Tags']
                    if isinstance(tags, list):
                        print(f"   - Tags: {', '.join(tags)}")
                
                # Related Items
                if investigation.get('RelatedDatasets'):
                    print(f"   - Related Datasets: {len(investigation['RelatedDatasets'])}")
                if investigation.get('RelatedInvestigations'):
                    print(f"   - Related Investigations: {len(investigation['RelatedInvestigations'])}")
                
                # Workflow Information
                if investigation.get('WorkflowName'):
                    print(f"   - Workflow: {investigation['WorkflowName']}")
                if investigation.get('TriggeredBy'):
                    print(f"   - Triggered By: {investigation['TriggeredBy']}")
                if investigation.get('Schedule'):
                    print(f"   - Schedule: {investigation['Schedule']}")
        
        # Pagination info
        if total_pages > 1:
            print(f"\n" + "="*50)
            print(f"Page {page} of {total_pages} | Total investigations: {total_count}")
            
            if page > 1:
                print(f"← Previous page: {page - 1}")
            if page < total_pages:
                print(f"→ Next page: {page + 1}")
        
        # Summary statistics
        if len(investigations) > 1:
            print(f"\n" + "="*50)
            print("Page Summary:")
            
            # Status distribution
            statuses = {}
            priorities = {}
            types = {}
            
            for inv in investigations:
                status = inv.get('Status', 'Unknown')
                statuses[status] = statuses.get(status, 0) + 1
                
                priority = inv.get('Priority', 'Unknown')
                priorities[priority] = priorities.get(priority, 0) + 1
                
                inv_type = inv.get('InvestigationType', 'Unknown')
                types[inv_type] = types.get(inv_type, 0) + 1
            
            print("- By Status:")
            for status, count in sorted(statuses.items()):
                print(f"  • {status}: {count}")
            
            if len(priorities) > 1:
                print("- By Priority:")
                for priority, count in sorted(priorities.items()):
                    print(f"  • {priority}: {count}")
            
            if len(types) > 1:
                print("- By Type:")
                for inv_type, count in sorted(types.items()):
                    print(f"  • {inv_type}: {count}")
        
        return response
        
    except MindzieAPIException as e:
        print_error(f"API error: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return None


def list_all_investigations(
    client: MindzieAPIClient,
    project_id: str,
    max_pages: int = 10
) -> List[Dict[str, Any]]:
    """
    List all investigations across multiple pages.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        max_pages: Maximum number of pages to fetch
        
    Returns:
        List of all investigations
    """
    all_investigations = []
    page = 1
    
    while page <= max_pages:
        response = client.investigations.get_all(
            project_id=project_id,
            page=page,
            page_size=20
        )
        
        if not response or not response.get("Investigations"):
            break
        
        investigations = response["Investigations"]
        all_investigations.extend(investigations)
        
        total_pages = response.get("TotalPages", 1)
        if page >= total_pages:
            break
        
        page += 1
    
    return all_investigations


def main():
    """Main function to demonstrate investigation listing."""
    print_header("List Investigations Example")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='List investigations for a project')
    parser.add_argument('--project-id', help='Project ID (optional, will auto-discover if not provided)')
    parser.add_argument('--page', type=int, default=1, help='Page number (default: 1)')
    parser.add_argument('--page-size', type=int, default=10, help='Items per page (default: 10)')
    parser.add_argument('--all', action='store_true', help='Fetch all pages')
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
        
        # List investigations
        if args.all:
            print_info("Fetching all investigations...")
            all_investigations = list_all_investigations(client, project_id)
            print_success(f"Retrieved {len(all_investigations)} investigations total")
            
            # Display summary
            if all_investigations:
                print("\nAll Investigations Summary:")
                for idx, inv in enumerate(all_investigations, 1):
                    name = inv.get('InvestigationName', 'Unnamed')
                    status = inv.get('Status', 'Unknown')
                    print(f"{idx}. {name} - Status: {status}")
        else:
            result = list_investigations(
                client,
                project_id,
                page=args.page,
                page_size=args.page_size,
                show_details=not args.brief
            )
            
            if result:
                print_success("\nInvestigation listing completed successfully!")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to list investigations: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()