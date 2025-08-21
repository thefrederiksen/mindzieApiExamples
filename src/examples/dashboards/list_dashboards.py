"""
List all dashboards for a project with pagination support.

This example demonstrates how to:
- List dashboards with pagination
- Display dashboard metadata and properties
- Show dashboard URLs and access information
- Filter dashboards by type and status
- Auto-discover projects when no ID is provided
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


def list_dashboards(
    client: MindzieAPIClient,
    project_id: str,
    page: int = 1,
    page_size: int = 10,
    show_details: bool = True
) -> Optional[Dict[str, Any]]:
    """
    List dashboards for a project with pagination.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        page: Page number (1-based)
        page_size: Number of items per page
        show_details: Whether to show detailed information
        
    Returns:
        Dictionary containing dashboard information or None if error
    """
    try:
        print_info(f"Fetching dashboards for project {project_id} (Page {page})...")
        
        # Get dashboards from the API
        response = client.dashboards.get_all(
            project_id=project_id,
            page=page,
            page_size=page_size
        )
        
        if not response:
            print_info("No response received from API")
            return None
        
        # Extract dashboard data
        dashboards = response.get("Dashboards", [])
        total_count = response.get("TotalCount", 0)
        total_pages = response.get("TotalPages", 1)
        
        if total_count == 0:
            print_info("No dashboards found for this project")
            return response
        
        print_success(f"Found {total_count} dashboard(s) total")
        print_info(f"Showing page {page} of {total_pages} ({len(dashboards)} items)")
        
        # Display dashboard information
        for idx, dashboard in enumerate(dashboards, 1 + (page - 1) * page_size):
            print(f"\n{idx}. Dashboard: {dashboard.get('Name', 'Unnamed')}")
            
            if show_details:
                # Basic Information
                print("   Basic Information:")
                print(f"   - Dashboard ID: {dashboard.get('DashboardId', 'N/A')}")
                print(f"   - Type: {dashboard.get('Type', 'Unknown')}")
                print(f"   - Status: {dashboard.get('Status', 'Unknown')}")
                
                # URL and Access
                if dashboard.get('Url'):
                    print(f"   - URL: {dashboard['Url']}")
                if dashboard.get('EmbedUrl'):
                    print(f"   - Embed URL: {dashboard['EmbedUrl']}")
                if dashboard.get('PublicUrl'):
                    print(f"   - Public URL: {dashboard['PublicUrl']}")
                
                # Description
                if dashboard.get('Description'):
                    desc = dashboard['Description']
                    if len(desc) > 100:
                        desc = desc[:97] + "..."
                    print(f"   - Description: {desc}")
                
                # Owner and Permissions
                if dashboard.get('Owner'):
                    print(f"   - Owner: {dashboard['Owner']}")
                if dashboard.get('CreatedBy'):
                    print(f"   - Created By: {dashboard['CreatedBy']}")
                if dashboard.get('ModifiedBy'):
                    print(f"   - Modified By: {dashboard['ModifiedBy']}")
                
                # Access Control
                if dashboard.get('IsPublic') is not None:
                    access = "Public" if dashboard['IsPublic'] else "Private"
                    icon = "🌐" if dashboard['IsPublic'] else "🔒"
                    print(f"   - Access: {icon} {access}")
                
                if dashboard.get('SharedWith'):
                    shared = dashboard['SharedWith']
                    if isinstance(shared, list) and shared:
                        print(f"   - Shared With: {', '.join(shared[:3])}")
                        if len(shared) > 3:
                            print(f"     (and {len(shared) - 3} more...)")
                
                # Timestamps
                if dashboard.get('CreatedAt'):
                    print(f"   - Created: {format_timestamp(dashboard['CreatedAt'])}")
                if dashboard.get('ModifiedAt'):
                    print(f"   - Modified: {format_timestamp(dashboard['ModifiedAt'])}")
                if dashboard.get('LastViewedAt'):
                    print(f"   - Last Viewed: {format_timestamp(dashboard['LastViewedAt'])}")
                if dashboard.get('LastRefreshedAt'):
                    print(f"   - Last Refreshed: {format_timestamp(dashboard['LastRefreshedAt'])}")
                
                # Dashboard Components
                if dashboard.get('WidgetCount') is not None:
                    print(f"   - Widgets: {dashboard['WidgetCount']}")
                if dashboard.get('Widgets'):
                    widgets = dashboard['Widgets']
                    if isinstance(widgets, list):
                        widget_types = {}
                        for widget in widgets:
                            widget_type = widget.get('Type', 'Unknown') if isinstance(widget, dict) else 'Unknown'
                            widget_types[widget_type] = widget_types.get(widget_type, 0) + 1
                        
                        if widget_types:
                            print("   - Widget Types:")
                            for wtype, count in sorted(widget_types.items()):
                                print(f"     • {wtype}: {count}")
                
                # Data Sources
                if dashboard.get('DataSources'):
                    sources = dashboard['DataSources']
                    if isinstance(sources, list):
                        print(f"   - Data Sources ({len(sources)}):")
                        for source in sources[:3]:
                            print(f"     • {source}")
                        if len(sources) > 3:
                            print(f"     (and {len(sources) - 3} more...)")
                
                # Filters and Parameters
                if dashboard.get('Filters'):
                    filters = dashboard['Filters']
                    if isinstance(filters, list):
                        print(f"   - Filters: {', '.join(filters)}")
                
                if dashboard.get('Parameters'):
                    params = dashboard['Parameters']
                    if isinstance(params, dict):
                        print(f"   - Parameters: {len(params)} defined")
                
                # Refresh Settings
                if dashboard.get('RefreshInterval'):
                    interval = dashboard['RefreshInterval']
                    if isinstance(interval, (int, float)):
                        if interval >= 3600:
                            print(f"   - Refresh Interval: {interval/3600:.1f} hours")
                        elif interval >= 60:
                            print(f"   - Refresh Interval: {interval/60:.0f} minutes")
                        else:
                            print(f"   - Refresh Interval: {interval} seconds")
                    else:
                        print(f"   - Refresh Interval: {interval}")
                
                if dashboard.get('AutoRefresh') is not None:
                    auto = "Enabled" if dashboard['AutoRefresh'] else "Disabled"
                    print(f"   - Auto-Refresh: {auto}")
                
                # Tags and Categories
                if dashboard.get('Tags'):
                    tags = dashboard['Tags']
                    if isinstance(tags, list) and tags:
                        print(f"   - Tags: {', '.join(tags)}")
                
                if dashboard.get('Category'):
                    print(f"   - Category: {dashboard['Category']}")
                
                # Theme and Layout
                if dashboard.get('Theme'):
                    print(f"   - Theme: {dashboard['Theme']}")
                if dashboard.get('Layout'):
                    print(f"   - Layout: {dashboard['Layout']}")
                
                # Usage Statistics
                if dashboard.get('ViewCount') is not None:
                    print(f"   - View Count: {dashboard['ViewCount']:,}")
                if dashboard.get('UniqueViewers') is not None:
                    print(f"   - Unique Viewers: {dashboard['UniqueViewers']:,}")
                if dashboard.get('AverageViewTime') is not None:
                    avg_time = dashboard['AverageViewTime']
                    if isinstance(avg_time, (int, float)):
                        print(f"   - Avg View Time: {avg_time:.1f} seconds")
                
                # Export Options
                if dashboard.get('ExportFormats'):
                    formats = dashboard['ExportFormats']
                    if isinstance(formats, list) and formats:
                        print(f"   - Export Formats: {', '.join(formats)}")
        
        # Pagination info
        if total_pages > 1:
            print(f"\n" + "="*50)
            print(f"Page {page} of {total_pages} | Total dashboards: {total_count}")
            
            if page > 1:
                print(f"← Previous page: {page - 1}")
            if page < total_pages:
                print(f"→ Next page: {page + 1}")
        
        # Summary statistics
        if len(dashboards) > 1:
            print(f"\n" + "="*50)
            print("Page Summary:")
            
            # Status distribution
            statuses = {}
            types = {}
            public_count = 0
            shared_count = 0
            total_widgets = 0
            total_views = 0
            
            for dash in dashboards:
                status = dash.get('Status', 'Unknown')
                statuses[status] = statuses.get(status, 0) + 1
                
                dash_type = dash.get('Type', 'Unknown')
                types[dash_type] = types.get(dash_type, 0) + 1
                
                if dash.get('IsPublic'):
                    public_count += 1
                
                if dash.get('SharedWith'):
                    shared_count += 1
                
                total_widgets += dash.get('WidgetCount', 0)
                total_views += dash.get('ViewCount', 0)
            
            print("- By Status:")
            for status, count in sorted(statuses.items()):
                print(f"  • {status}: {count}")
            
            if len(types) > 1:
                print("- By Type:")
                for dtype, count in sorted(types.items()):
                    print(f"  • {dtype}: {count}")
            
            if public_count > 0:
                print(f"- Public Dashboards: {public_count}")
            if shared_count > 0:
                print(f"- Shared Dashboards: {shared_count}")
            
            if total_widgets > 0:
                avg_widgets = total_widgets / len(dashboards)
                print(f"- Total Widgets: {total_widgets} (avg: {avg_widgets:.1f} per dashboard)")
            
            if total_views > 0:
                avg_views = total_views / len(dashboards)
                print(f"- Total Views: {total_views:,} (avg: {avg_views:.0f} per dashboard)")
        
        return response
        
    except MindzieAPIException as e:
        print_error(f"API error: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return None


def list_all_dashboards(
    client: MindzieAPIClient,
    project_id: str,
    max_pages: int = 10
) -> List[Dict[str, Any]]:
    """
    List all dashboards across multiple pages.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        max_pages: Maximum number of pages to fetch
        
    Returns:
        List of all dashboards
    """
    all_dashboards = []
    page = 1
    
    while page <= max_pages:
        response = client.dashboards.get_all(
            project_id=project_id,
            page=page,
            page_size=20
        )
        
        if not response or not response.get("Dashboards"):
            break
        
        dashboards = response["Dashboards"]
        all_dashboards.extend(dashboards)
        
        total_pages = response.get("TotalPages", 1)
        if page >= total_pages:
            break
        
        page += 1
    
    return all_dashboards


def main():
    """Main function to demonstrate dashboard listing."""
    print_header("List Dashboards Example")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='List dashboards for a project')
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
        
        # List dashboards
        if args.all:
            print_info("Fetching all dashboards...")
            all_dashboards = list_all_dashboards(client, project_id)
            print_success(f"Retrieved {len(all_dashboards)} dashboards total")
            
            # Display summary
            if all_dashboards:
                print("\nAll Dashboards Summary:")
                for idx, dash in enumerate(all_dashboards, 1):
                    name = dash.get('Name', 'Unnamed')
                    status = dash.get('Status', 'Unknown')
                    access = "Public" if dash.get('IsPublic') else "Private"
                    print(f"{idx}. {name} - Status: {status}, Access: {access}")
                    if dash.get('Url'):
                        print(f"   URL: {dash['Url']}")
        else:
            result = list_dashboards(
                client,
                project_id,
                page=args.page,
                page_size=args.page_size,
                show_details=not args.brief
            )
            
            if result:
                print_success("\nDashboard listing completed successfully!")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to list dashboards: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()