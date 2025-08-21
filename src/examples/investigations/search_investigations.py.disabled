"""
Search and filter investigations with various criteria.

This example demonstrates how to:
- Search investigations by name and description
- Filter by status, priority, and type
- Filter by date ranges
- Search by tags and categories
- Combine multiple search criteria
- Sort results by different fields
"""

import os
import sys
from datetime import datetime, timedelta
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


def filter_investigations(
    investigations: List[Dict[str, Any]],
    search_term: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    investigation_type: Optional[str] = None,
    owner: Optional[str] = None,
    tags: Optional[List[str]] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    min_findings: Optional[int] = None,
    max_findings: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Filter investigations based on various criteria.
    
    Args:
        investigations: List of investigation dictionaries
        search_term: Search in name and description
        status: Filter by status
        priority: Filter by priority
        investigation_type: Filter by type
        owner: Filter by owner
        tags: Filter by tags (any match)
        date_from: Filter by creation date (from)
        date_to: Filter by creation date (to)
        min_findings: Minimum number of findings
        max_findings: Maximum number of findings
        
    Returns:
        Filtered list of investigations
    """
    filtered = investigations.copy()
    
    # Search term filter (name and description)
    if search_term:
        search_lower = search_term.lower()
        filtered = [
            inv for inv in filtered
            if (search_lower in inv.get('InvestigationName', '').lower() or
                search_lower in inv.get('Description', '').lower())
        ]
    
    # Status filter
    if status:
        filtered = [
            inv for inv in filtered
            if inv.get('Status', '').lower() == status.lower()
        ]
    
    # Priority filter
    if priority:
        filtered = [
            inv for inv in filtered
            if inv.get('Priority', '').lower() == priority.lower()
        ]
    
    # Type filter
    if investigation_type:
        filtered = [
            inv for inv in filtered
            if inv.get('InvestigationType', '').lower() == investigation_type.lower()
        ]
    
    # Owner filter
    if owner:
        owner_lower = owner.lower()
        filtered = [
            inv for inv in filtered
            if owner_lower in inv.get('Owner', '').lower()
        ]
    
    # Tags filter (any match)
    if tags:
        tags_lower = [tag.lower() for tag in tags]
        filtered = [
            inv for inv in filtered
            if inv.get('Tags') and any(
                tag.lower() in tags_lower
                for tag in inv['Tags']
            )
        ]
    
    # Date range filter
    if date_from or date_to:
        date_filtered = []
        for inv in filtered:
            if inv.get('CreatedAt'):
                try:
                    created = datetime.fromisoformat(inv['CreatedAt'].replace('Z', '+00:00'))
                    
                    if date_from and created < date_from:
                        continue
                    if date_to and created > date_to:
                        continue
                    
                    date_filtered.append(inv)
                except:
                    # If date parsing fails, include the investigation
                    date_filtered.append(inv)
            else:
                # No creation date, include by default
                date_filtered.append(inv)
        
        filtered = date_filtered
    
    # Findings count filter
    if min_findings is not None or max_findings is not None:
        findings_filtered = []
        for inv in filtered:
            findings_count = inv.get('FindingsCount', 0)
            
            if min_findings is not None and findings_count < min_findings:
                continue
            if max_findings is not None and findings_count > max_findings:
                continue
            
            findings_filtered.append(inv)
        
        filtered = findings_filtered
    
    return filtered


def sort_investigations(
    investigations: List[Dict[str, Any]],
    sort_by: str = 'created',
    descending: bool = True
) -> List[Dict[str, Any]]:
    """
    Sort investigations by specified field.
    
    Args:
        investigations: List of investigation dictionaries
        sort_by: Field to sort by (created, modified, name, priority, findings)
        descending: Sort in descending order
        
    Returns:
        Sorted list of investigations
    """
    # Define sort key functions
    sort_keys = {
        'created': lambda x: x.get('CreatedAt', ''),
        'modified': lambda x: x.get('LastModifiedAt', ''),
        'name': lambda x: x.get('InvestigationName', '').lower(),
        'priority': lambda x: {
            'critical': 0,
            'high': 1,
            'medium': 2,
            'low': 3
        }.get(x.get('Priority', '').lower(), 4),
        'findings': lambda x: x.get('FindingsCount', 0),
        'progress': lambda x: x.get('Progress', 0),
        'status': lambda x: x.get('Status', '').lower()
    }
    
    # Get sort key function
    key_func = sort_keys.get(sort_by.lower(), sort_keys['created'])
    
    # Sort investigations
    try:
        sorted_invs = sorted(investigations, key=key_func, reverse=descending)
    except:
        # If sorting fails, return original list
        sorted_invs = investigations
    
    return sorted_invs


def search_investigations(
    client: MindzieAPIClient,
    project_id: str,
    search_criteria: Dict[str, Any],
    max_results: int = 50
) -> List[Dict[str, Any]]:
    """
    Search investigations with specified criteria.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        search_criteria: Dictionary with search parameters
        max_results: Maximum number of results to return
        
    Returns:
        List of matching investigations
    """
    try:
        print_info(f"Searching investigations in project {project_id}...")
        
        # Fetch all investigations (paginated)
        all_investigations = []
        page = 1
        max_pages = 10  # Limit pages to avoid excessive API calls
        
        while page <= max_pages:
            response = client.investigations.get_all(
                project_id=project_id,
                page=page,
                page_size=50
            )
            
            if not response or not response.get("Investigations"):
                break
            
            investigations = response["Investigations"]
            all_investigations.extend(investigations)
            
            # Check if we have enough or reached the last page
            total_pages = response.get("TotalPages", 1)
            if page >= total_pages or len(all_investigations) >= max_results * 2:
                break
            
            page += 1
        
        if not all_investigations:
            print_info("No investigations found to search")
            return []
        
        print_info(f"Searching through {len(all_investigations)} investigations...")
        
        # Apply filters
        filtered = filter_investigations(
            all_investigations,
            search_term=search_criteria.get('search_term'),
            status=search_criteria.get('status'),
            priority=search_criteria.get('priority'),
            investigation_type=search_criteria.get('type'),
            owner=search_criteria.get('owner'),
            tags=search_criteria.get('tags'),
            date_from=search_criteria.get('date_from'),
            date_to=search_criteria.get('date_to'),
            min_findings=search_criteria.get('min_findings'),
            max_findings=search_criteria.get('max_findings')
        )
        
        # Sort results
        sort_by = search_criteria.get('sort_by', 'created')
        descending = search_criteria.get('descending', True)
        sorted_results = sort_investigations(filtered, sort_by, descending)
        
        # Limit results
        final_results = sorted_results[:max_results]
        
        print_success(f"Found {len(filtered)} matching investigation(s)")
        
        return final_results
        
    except MindzieAPIException as e:
        print_error(f"API error: {e}")
        return []
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return []


def display_search_results(results: List[Dict[str, Any]], verbose: bool = True):
    """
    Display search results in a formatted manner.
    
    Args:
        results: List of investigation dictionaries
        verbose: Whether to show detailed information
    """
    if not results:
        print_info("No investigations match the search criteria")
        return
    
    print(f"\n" + "="*70)
    print(f"SEARCH RESULTS ({len(results)} investigation(s))")
    print("="*70)
    
    for idx, inv in enumerate(results, 1):
        name = inv.get('InvestigationName', 'Unnamed')
        status = inv.get('Status', 'Unknown')
        priority = inv.get('Priority', 'N/A')
        
        # Status icon
        status_icon = {
            'Completed': '✅',
            'InProgress': '🔄',
            'Pending': '⏳',
            'Failed': '❌',
            'Cancelled': '⚠️'
        }.get(status, '❓')
        
        # Priority icon
        priority_icon = {
            'Critical': '🔴',
            'High': '🟠',
            'Medium': '🟡',
            'Low': '🟢'
        }.get(priority, '⚪')
        
        print(f"\n{idx}. {name}")
        print(f"   Status: {status_icon} {status} | Priority: {priority_icon} {priority}")
        
        if verbose:
            if inv.get('InvestigationType'):
                print(f"   Type: {inv['InvestigationType']}")
            if inv.get('Owner'):
                print(f"   Owner: {inv['Owner']}")
            if inv.get('CreatedAt'):
                print(f"   Created: {format_timestamp(inv['CreatedAt'])}")
            if inv.get('FindingsCount') is not None:
                print(f"   Findings: {inv['FindingsCount']}")
            if inv.get('Progress') is not None:
                progress = inv['Progress']
                bar_length = 15
                filled = int(bar_length * progress / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"   Progress: [{bar}] {progress}%")
            if inv.get('Description'):
                desc = inv['Description']
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                print(f"   Description: {desc}")
            if inv.get('Tags'):
                tags = inv['Tags']
                if isinstance(tags, list) and tags:
                    print(f"   Tags: {', '.join(tags[:5])}")
    
    # Summary statistics
    if len(results) > 1:
        print(f"\n" + "-"*70)
        print("SUMMARY")
        print("-"*70)
        
        # Status distribution
        statuses = {}
        priorities = {}
        total_findings = 0
        completed_count = 0
        
        for inv in results:
            status = inv.get('Status', 'Unknown')
            statuses[status] = statuses.get(status, 0) + 1
            
            if status == 'Completed':
                completed_count += 1
            
            priority = inv.get('Priority', 'Unknown')
            priorities[priority] = priorities.get(priority, 0) + 1
            
            total_findings += inv.get('FindingsCount', 0)
        
        print("Status Distribution:")
        for status, count in sorted(statuses.items()):
            percentage = (count / len(results)) * 100
            print(f"  • {status}: {count} ({percentage:.1f}%)")
        
        if len(priorities) > 1:
            print("\nPriority Distribution:")
            for priority, count in sorted(priorities.items()):
                percentage = (count / len(results)) * 100
                print(f"  • {priority}: {count} ({percentage:.1f}%)")
        
        if total_findings > 0:
            avg_findings = total_findings / len(results)
            print(f"\nTotal Findings: {total_findings} (avg: {avg_findings:.1f} per investigation)")
        
        if completed_count > 0:
            completion_rate = (completed_count / len(results)) * 100
            print(f"Completion Rate: {completion_rate:.1f}%")
    
    print("\n" + "="*70)


def main():
    """Main function to demonstrate investigation searching."""
    print_header("Search Investigations Example")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Search and filter investigations')
    parser.add_argument('--project-id', help='Project ID (optional, will auto-discover if not provided)')
    parser.add_argument('--search', help='Search term (name/description)')
    parser.add_argument('--status', help='Filter by status (Completed, InProgress, Pending, Failed)')
    parser.add_argument('--priority', help='Filter by priority (Critical, High, Medium, Low)')
    parser.add_argument('--type', help='Filter by investigation type')
    parser.add_argument('--owner', help='Filter by owner')
    parser.add_argument('--tags', nargs='+', help='Filter by tags (space-separated)')
    parser.add_argument('--days-ago', type=int, help='Filter investigations created in last N days')
    parser.add_argument('--min-findings', type=int, help='Minimum number of findings')
    parser.add_argument('--max-findings', type=int, help='Maximum number of findings')
    parser.add_argument('--sort-by', default='created', 
                       choices=['created', 'modified', 'name', 'priority', 'findings', 'progress', 'status'],
                       help='Sort results by field')
    parser.add_argument('--ascending', action='store_true', help='Sort in ascending order')
    parser.add_argument('--max-results', type=int, default=20, help='Maximum results to show')
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
        
        # Build search criteria
        search_criteria = {}
        
        if args.search:
            search_criteria['search_term'] = args.search
            print_info(f"Searching for: '{args.search}'")
        
        if args.status:
            search_criteria['status'] = args.status
            print_info(f"Filtering by status: {args.status}")
        
        if args.priority:
            search_criteria['priority'] = args.priority
            print_info(f"Filtering by priority: {args.priority}")
        
        if args.type:
            search_criteria['type'] = args.type
            print_info(f"Filtering by type: {args.type}")
        
        if args.owner:
            search_criteria['owner'] = args.owner
            print_info(f"Filtering by owner: {args.owner}")
        
        if args.tags:
            search_criteria['tags'] = args.tags
            print_info(f"Filtering by tags: {', '.join(args.tags)}")
        
        if args.days_ago:
            date_from = datetime.now() - timedelta(days=args.days_ago)
            search_criteria['date_from'] = date_from
            print_info(f"Filtering by last {args.days_ago} days")
        
        if args.min_findings is not None:
            search_criteria['min_findings'] = args.min_findings
            print_info(f"Minimum findings: {args.min_findings}")
        
        if args.max_findings is not None:
            search_criteria['max_findings'] = args.max_findings
            print_info(f"Maximum findings: {args.max_findings}")
        
        search_criteria['sort_by'] = args.sort_by
        search_criteria['descending'] = not args.ascending
        
        # Search investigations
        results = search_investigations(
            client,
            project_id,
            search_criteria,
            max_results=args.max_results
        )
        
        # Display results
        display_search_results(results, verbose=not args.brief)
        
        if results:
            print_success("\nSearch completed successfully!")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to search investigations: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()