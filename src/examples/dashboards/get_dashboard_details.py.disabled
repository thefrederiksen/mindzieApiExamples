"""
Get detailed configuration and metadata for a specific dashboard.

This example demonstrates how to:
- Retrieve comprehensive dashboard configuration
- Display widget details and layout
- Show data source connections
- Access dashboard filters and parameters
- Auto-discover dashboards when no ID is provided
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
    print_header,
    print_error,
    print_success,
    print_info
)


def discover_dashboard(client: MindzieAPIClient, project_id: str) -> Optional[str]:
    """
    Auto-discover a dashboard from the project.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        
    Returns:
        Dashboard ID or None if no dashboards found
    """
    try:
        print_info("Discovering available dashboards...")
        response = client.dashboards.get_all(
            project_id=project_id,
            page=1,
            page_size=10
        )
        
        if not response or not response.get("Dashboards"):
            print_info("No dashboards found in this project")
            return None
        
        dashboards = response["Dashboards"]
        
        if len(dashboards) == 1:
            dashboard = dashboards[0]
            print_success(f"Found dashboard: {dashboard.get('Name', 'Unnamed')}")
            return dashboard.get('DashboardId')
        
        # Multiple dashboards - let user choose
        print_info(f"Found {len(dashboards)} dashboards:")
        for idx, dashboard in enumerate(dashboards[:10], 1):  # Show max 10
            status = dashboard.get('Status', 'Unknown')
            access = "Public" if dashboard.get('IsPublic') else "Private"
            print(f"  {idx}. {dashboard.get('Name', 'Unnamed')} "
                  f"(Status: {status}, Access: {access}, ID: {dashboard.get('DashboardId', 'N/A')})")
        
        # Use the first one for demonstration
        selected = dashboards[0]
        print_info(f"Using first dashboard: {selected.get('Name', 'Unnamed')}")
        return selected.get('DashboardId')
        
    except Exception as e:
        print_error(f"Failed to discover dashboards: {e}")
        return None


def get_dashboard_details(
    client: MindzieAPIClient,
    project_id: str,
    dashboard_id: str,
    show_widgets: bool = True,
    show_config: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a dashboard.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        dashboard_id: The dashboard ID
        show_widgets: Whether to display widget details
        show_config: Whether to show configuration
        
    Returns:
        Dictionary containing dashboard details or None if error
    """
    try:
        print_info(f"Fetching details for dashboard {dashboard_id}...")
        
        # Note: Since there's no specific get_by_id method for dashboards,
        # we'll get all dashboards and filter
        response = client.dashboards.get_all(
            project_id=project_id,
            page=1,
            page_size=100  # Get more to find our dashboard
        )
        
        if not response or not response.get("Dashboards"):
            print_error("No dashboards found")
            return None
        
        # Find the specific dashboard
        dashboard = None
        for item in response["Dashboards"]:
            if item.get("DashboardId") == dashboard_id:
                dashboard = item
                break
        
        if not dashboard:
            print_error(f"Dashboard {dashboard_id} not found")
            return None
        
        print_success(f"Retrieved dashboard: {dashboard.get('Name', 'Unnamed')}")
        
        # Display comprehensive dashboard information
        print("\n" + "="*70)
        print("DASHBOARD DETAILS")
        print("="*70)
        
        # Basic Information
        print("\n📊 Basic Information:")
        print(f"   Name: {dashboard.get('Name', 'N/A')}")
        print(f"   ID: {dashboard.get('DashboardId', 'N/A')}")
        print(f"   Type: {dashboard.get('Type', 'Unknown')}")
        
        # Status and State
        status = dashboard.get('Status', 'Unknown')
        status_icon = {
            'Active': '✅',
            'Draft': '📝',
            'Published': '🚀',
            'Archived': '📦',
            'Deprecated': '⚠️'
        }.get(status, '❓')
        print(f"   Status: {status_icon} {status}")
        
        if dashboard.get('Version'):
            print(f"   Version: {dashboard['Version']}")
        
        # Description and Purpose
        if dashboard.get('Description'):
            print(f"\n📝 Description:")
            print(f"   {dashboard['Description']}")
        
        if dashboard.get('Purpose'):
            print(f"\n🎯 Purpose:")
            print(f"   {dashboard['Purpose']}")
        
        # URLs and Access
        print(f"\n🔗 Access Information:")
        if dashboard.get('Url'):
            print(f"   Dashboard URL: {dashboard['Url']}")
        if dashboard.get('EmbedUrl'):
            print(f"   Embed URL: {dashboard['EmbedUrl']}")
        if dashboard.get('PublicUrl'):
            print(f"   Public URL: {dashboard['PublicUrl']}")
        if dashboard.get('ApiEndpoint'):
            print(f"   API Endpoint: {dashboard['ApiEndpoint']}")
        
        # Access Control
        access_icon = "🌐" if dashboard.get('IsPublic') else "🔒"
        access_type = "Public" if dashboard.get('IsPublic') else "Private"
        print(f"   Access Type: {access_icon} {access_type}")
        
        if dashboard.get('RequiresAuthentication') is not None:
            auth = "Required" if dashboard['RequiresAuthentication'] else "Not Required"
            print(f"   Authentication: {auth}")
        
        # Ownership
        print(f"\n👥 Ownership:")
        if dashboard.get('Owner'):
            print(f"   Owner: {dashboard['Owner']}")
        if dashboard.get('CreatedBy'):
            print(f"   Created By: {dashboard['CreatedBy']}")
        if dashboard.get('ModifiedBy'):
            print(f"   Modified By: {dashboard['ModifiedBy']}")
        if dashboard.get('Department'):
            print(f"   Department: {dashboard['Department']}")
        if dashboard.get('Team'):
            print(f"   Team: {dashboard['Team']}")
        
        # Timestamps
        print(f"\n🕐 Timeline:")
        if dashboard.get('CreatedAt'):
            print(f"   Created: {format_timestamp(dashboard['CreatedAt'])}")
        if dashboard.get('ModifiedAt'):
            print(f"   Modified: {format_timestamp(dashboard['ModifiedAt'])}")
        if dashboard.get('PublishedAt'):
            print(f"   Published: {format_timestamp(dashboard['PublishedAt'])}")
        if dashboard.get('LastViewedAt'):
            print(f"   Last Viewed: {format_timestamp(dashboard['LastViewedAt'])}")
        if dashboard.get('LastRefreshedAt'):
            print(f"   Last Refreshed: {format_timestamp(dashboard['LastRefreshedAt'])}")
        
        # Widgets and Components
        if show_widgets:
            print(f"\n🧩 Widgets & Components:")
            
            if dashboard.get('WidgetCount') is not None:
                print(f"   Total Widgets: {dashboard['WidgetCount']}")
            
            if dashboard.get('Widgets'):
                widgets = dashboard['Widgets']
                if isinstance(widgets, list):
                    print(f"   Widget Details ({len(widgets)} widgets):")
                    
                    for idx, widget in enumerate(widgets, 1):
                        if isinstance(widget, dict):
                            print(f"\n   Widget {idx}: {widget.get('Name', 'Unnamed')}")
                            print(f"     - Type: {widget.get('Type', 'Unknown')}")
                            print(f"     - ID: {widget.get('WidgetId', 'N/A')}")
                            
                            if widget.get('Position'):
                                pos = widget['Position']
                                if isinstance(pos, dict):
                                    print(f"     - Position: Row {pos.get('Row', 0)}, Col {pos.get('Col', 0)}")
                            
                            if widget.get('Size'):
                                size = widget['Size']
                                if isinstance(size, dict):
                                    print(f"     - Size: {size.get('Width', 0)}x{size.get('Height', 0)}")
                            
                            if widget.get('DataSource'):
                                print(f"     - Data Source: {widget['DataSource']}")
                            
                            if widget.get('Query'):
                                query = widget['Query']
                                if len(query) > 50:
                                    query = query[:47] + "..."
                                print(f"     - Query: {query}")
                            
                            if widget.get('RefreshInterval'):
                                print(f"     - Refresh: {widget['RefreshInterval']}s")
                            
                            if widget.get('ChartType'):
                                print(f"     - Chart Type: {widget['ChartType']}")
                            
                            if widget.get('Metrics'):
                                metrics = widget['Metrics']
                                if isinstance(metrics, list):
                                    print(f"     - Metrics: {', '.join(metrics[:3])}")
                            
                            if widget.get('Filters'):
                                filters = widget['Filters']
                                if isinstance(filters, list):
                                    print(f"     - Filters: {len(filters)} applied")
                        else:
                            print(f"   Widget {idx}: {widget}")
            
            # Layout Information
            if dashboard.get('Layout'):
                layout = dashboard['Layout']
                if isinstance(layout, dict):
                    print(f"\n   Layout Configuration:")
                    print(f"     - Type: {layout.get('Type', 'Grid')}")
                    print(f"     - Columns: {layout.get('Columns', 12)}")
                    print(f"     - Rows: {layout.get('Rows', 'Auto')}")
                    if layout.get('Responsive'):
                        print(f"     - Responsive: Yes")
                    if layout.get('Breakpoints'):
                        print(f"     - Breakpoints: {layout['Breakpoints']}")
        
        # Data Sources
        print(f"\n📁 Data Sources:")
        if dashboard.get('DataSources'):
            sources = dashboard['DataSources']
            if isinstance(sources, list):
                for idx, source in enumerate(sources, 1):
                    if isinstance(source, dict):
                        print(f"   {idx}. {source.get('Name', 'Unnamed')}")
                        print(f"      - Type: {source.get('Type', 'Unknown')}")
                        print(f"      - Connection: {source.get('Connection', 'N/A')}")
                        if source.get('LastSync'):
                            print(f"      - Last Sync: {format_timestamp(source['LastSync'])}")
                    else:
                        print(f"   {idx}. {source}")
        
        # Filters and Parameters
        if dashboard.get('GlobalFilters') or dashboard.get('Parameters'):
            print(f"\n🔧 Filters & Parameters:")
            
            if dashboard.get('GlobalFilters'):
                filters = dashboard['GlobalFilters']
                if isinstance(filters, list):
                    print(f"   Global Filters ({len(filters)}):")
                    for filter_item in filters[:5]:
                        if isinstance(filter_item, dict):
                            print(f"     • {filter_item.get('Name', 'N/A')}: "
                                  f"{filter_item.get('Field', 'N/A')} "
                                  f"{filter_item.get('Operator', '=')} "
                                  f"{filter_item.get('Value', 'N/A')}")
                        else:
                            print(f"     • {filter_item}")
            
            if dashboard.get('Parameters'):
                params = dashboard['Parameters']
                if isinstance(params, dict):
                    print(f"   Parameters ({len(params)}):")
                    for key, value in list(params.items())[:5]:
                        print(f"     • {key}: {value}")
        
        # Refresh and Caching
        print(f"\n🔄 Refresh & Caching:")
        if dashboard.get('RefreshInterval'):
            interval = dashboard['RefreshInterval']
            if isinstance(interval, (int, float)):
                if interval >= 3600:
                    print(f"   Refresh Interval: {interval/3600:.1f} hours")
                elif interval >= 60:
                    print(f"   Refresh Interval: {interval/60:.0f} minutes")
                else:
                    print(f"   Refresh Interval: {interval} seconds")
        
        if dashboard.get('AutoRefresh') is not None:
            auto = "Enabled" if dashboard['AutoRefresh'] else "Disabled"
            print(f"   Auto-Refresh: {auto}")
        
        if dashboard.get('CacheEnabled') is not None:
            cache = "Enabled" if dashboard['CacheEnabled'] else "Disabled"
            print(f"   Caching: {cache}")
            
            if dashboard.get('CacheDuration'):
                print(f"   Cache Duration: {dashboard['CacheDuration']} seconds")
        
        # Theme and Appearance
        print(f"\n🎨 Theme & Appearance:")
        if dashboard.get('Theme'):
            print(f"   Theme: {dashboard['Theme']}")
        if dashboard.get('ColorScheme'):
            print(f"   Color Scheme: {dashboard['ColorScheme']}")
        if dashboard.get('FontFamily'):
            print(f"   Font: {dashboard['FontFamily']}")
        if dashboard.get('LogoUrl'):
            print(f"   Logo: {dashboard['LogoUrl']}")
        if dashboard.get('BackgroundColor'):
            print(f"   Background: {dashboard['BackgroundColor']}")
        
        # Configuration
        if show_config and dashboard.get('Configuration'):
            config = dashboard['Configuration']
            if isinstance(config, dict):
                print(f"\n⚙️ Configuration:")
                for key, value in list(config.items())[:10]:
                    if isinstance(value, (dict, list)):
                        print(f"   {key}: {type(value).__name__} with {len(value)} items")
                    else:
                        print(f"   {key}: {value}")
        
        # Sharing and Permissions
        if dashboard.get('SharedWith') or dashboard.get('Permissions'):
            print(f"\n🔐 Sharing & Permissions:")
            
            if dashboard.get('SharedWith'):
                shared = dashboard['SharedWith']
                if isinstance(shared, list):
                    print(f"   Shared With ({len(shared)} users/groups):")
                    for user in shared[:5]:
                        if isinstance(user, dict):
                            print(f"     • {user.get('Name', 'N/A')} ({user.get('Role', 'Viewer')})")
                        else:
                            print(f"     • {user}")
                    if len(shared) > 5:
                        print(f"     ... and {len(shared) - 5} more")
            
            if dashboard.get('Permissions'):
                perms = dashboard['Permissions']
                if isinstance(perms, dict):
                    print("   Permissions:")
                    print(f"     • View: {perms.get('View', False)}")
                    print(f"     • Edit: {perms.get('Edit', False)}")
                    print(f"     • Delete: {perms.get('Delete', False)}")
                    print(f"     • Share: {perms.get('Share', False)}")
                    print(f"     • Export: {perms.get('Export', False)}")
        
        # Usage Statistics
        print(f"\n📊 Usage Statistics:")
        if dashboard.get('ViewCount') is not None:
            print(f"   Total Views: {dashboard['ViewCount']:,}")
        if dashboard.get('UniqueViewers') is not None:
            print(f"   Unique Viewers: {dashboard['UniqueViewers']:,}")
        if dashboard.get('AverageViewTime') is not None:
            avg_time = dashboard['AverageViewTime']
            if isinstance(avg_time, (int, float)):
                if avg_time >= 60:
                    print(f"   Avg View Time: {avg_time/60:.1f} minutes")
                else:
                    print(f"   Avg View Time: {avg_time:.0f} seconds")
        if dashboard.get('LastViewedBy'):
            print(f"   Last Viewed By: {dashboard['LastViewedBy']}")
        if dashboard.get('MostActiveUsers'):
            users = dashboard['MostActiveUsers']
            if isinstance(users, list) and users:
                print(f"   Most Active Users: {', '.join(users[:3])}")
        
        # Export Options
        if dashboard.get('ExportFormats'):
            formats = dashboard['ExportFormats']
            if isinstance(formats, list) and formats:
                print(f"\n📤 Export Options:")
                print(f"   Available Formats: {', '.join(formats)}")
                if dashboard.get('ScheduledExports'):
                    print(f"   Scheduled Exports: {dashboard['ScheduledExports']}")
        
        # Tags and Metadata
        if dashboard.get('Tags'):
            tags = dashboard['Tags']
            if isinstance(tags, list) and tags:
                print(f"\n🏷️  Tags: {', '.join(tags)}")
        
        if dashboard.get('Category'):
            print(f"📂 Category: {dashboard['Category']}")
        
        if dashboard.get('Keywords'):
            keywords = dashboard['Keywords']
            if isinstance(keywords, list) and keywords:
                print(f"🔑 Keywords: {', '.join(keywords)}")
        
        # Related Items
        if dashboard.get('RelatedDashboards') or dashboard.get('Dependencies'):
            print(f"\n🔗 Related Items:")
            
            if dashboard.get('RelatedDashboards'):
                related = dashboard['RelatedDashboards']
                if isinstance(related, list) and related:
                    print(f"   Related Dashboards: {', '.join(related[:3])}")
            
            if dashboard.get('Dependencies'):
                deps = dashboard['Dependencies']
                if isinstance(deps, list) and deps:
                    print(f"   Dependencies: {', '.join(deps[:3])}")
        
        # Notes
        if dashboard.get('Notes'):
            print(f"\n📝 Notes:")
            print(f"   {dashboard['Notes']}")
        
        print("\n" + "="*70)
        
        return dashboard
        
    except MindzieAPIException as e:
        print_error(f"API error: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return None


def main():
    """Main function to demonstrate getting dashboard details."""
    print_header("Get Dashboard Details Example")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Get detailed dashboard information')
    parser.add_argument('--project-id', help='Project ID (optional, will auto-discover if not provided)')
    parser.add_argument('--dashboard-id', help='Dashboard ID (optional, will auto-discover if not provided)')
    parser.add_argument('--no-widgets', action='store_true', help='Skip widget details')
    parser.add_argument('--no-config', action='store_true', help='Skip configuration details')
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
        
        # Get or discover dashboard ID
        if args.dashboard_id:
            dashboard_id = args.dashboard_id
            print_info(f"Using provided dashboard ID: {dashboard_id}")
        else:
            dashboard_id = discover_dashboard(client, project_id)
            if not dashboard_id:
                print_error("No dashboards available")
                return
        
        # Get dashboard details
        result = get_dashboard_details(
            client,
            project_id,
            dashboard_id,
            show_widgets=not args.no_widgets,
            show_config=not args.no_config
        )
        
        if result:
            print_success("\nDashboard details retrieved successfully!")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to get dashboard details: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()