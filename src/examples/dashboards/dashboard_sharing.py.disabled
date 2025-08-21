"""
Manage dashboard sharing and access settings.

This example demonstrates how to:
- View current sharing settings
- Manage user and group access
- Set public/private access
- Configure permissions and roles
- Track sharing history and audit logs
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


def get_dashboard_sharing_info(
    client: MindzieAPIClient,
    project_id: str,
    dashboard_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get sharing information for a dashboard or all dashboards.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        dashboard_id: Specific dashboard ID (optional)
        
    Returns:
        Dictionary containing sharing information or None if error
    """
    try:
        print_info(f"Fetching dashboard sharing information for project {project_id}...")
        
        # Get dashboards from the API
        response = client.dashboards.get_all(
            project_id=project_id,
            page=1,
            page_size=100
        )
        
        if not response or not response.get("Dashboards"):
            print_info("No dashboards found")
            return None
        
        dashboards = response["Dashboards"]
        
        # Filter for specific dashboard if ID provided
        if dashboard_id:
            dashboards = [d for d in dashboards if d.get("DashboardId") == dashboard_id]
            if not dashboards:
                print_error(f"Dashboard {dashboard_id} not found")
                return None
        
        sharing_info = {
            'total_dashboards': len(dashboards),
            'public_dashboards': 0,
            'private_dashboards': 0,
            'shared_dashboards': 0,
            'dashboards': []
        }
        
        for dashboard in dashboards:
            dash_info = {
                'id': dashboard.get('DashboardId'),
                'name': dashboard.get('Name', 'Unnamed'),
                'is_public': dashboard.get('IsPublic', False),
                'shared_with': dashboard.get('SharedWith', []),
                'permissions': dashboard.get('Permissions', {}),
                'owner': dashboard.get('Owner'),
                'created_by': dashboard.get('CreatedBy'),
                'modified_by': dashboard.get('ModifiedBy')
            }
            
            # Count dashboard types
            if dash_info['is_public']:
                sharing_info['public_dashboards'] += 1
            else:
                sharing_info['private_dashboards'] += 1
            
            if dash_info['shared_with']:
                sharing_info['shared_dashboards'] += 1
            
            sharing_info['dashboards'].append(dash_info)
        
        return sharing_info
        
    except MindzieAPIException as e:
        print_error(f"API error: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return None


def display_sharing_info(sharing_info: Dict[str, Any], detailed: bool = True):
    """
    Display dashboard sharing information in a formatted manner.
    
    Args:
        sharing_info: Dictionary containing sharing information
        detailed: Whether to show detailed information
    """
    print("\n" + "="*70)
    print("DASHBOARD SHARING & ACCESS REPORT")
    print("="*70)
    
    # Summary Statistics
    print("\n📊 SUMMARY")
    print("-" * 40)
    print(f"Total Dashboards: {sharing_info['total_dashboards']}")
    print(f"Public Dashboards: {sharing_info['public_dashboards']}")
    print(f"Private Dashboards: {sharing_info['private_dashboards']}")
    print(f"Shared Dashboards: {sharing_info['shared_dashboards']}")
    
    if sharing_info['total_dashboards'] > 0:
        public_percent = (sharing_info['public_dashboards'] / sharing_info['total_dashboards']) * 100
        shared_percent = (sharing_info['shared_dashboards'] / sharing_info['total_dashboards']) * 100
        print(f"\nAccess Distribution:")
        print(f"  • Public: {public_percent:.1f}%")
        print(f"  • Private: {100 - public_percent:.1f}%")
        print(f"  • Shared (with specific users): {shared_percent:.1f}%")
    
    if not detailed:
        return
    
    # Detailed Dashboard Information
    for idx, dashboard in enumerate(sharing_info['dashboards'], 1):
        print(f"\n" + "-"*70)
        print(f"{idx}. Dashboard: {dashboard['name']}")
        print(f"   ID: {dashboard['id']}")
        
        # Access Type
        access_icon = "🌐" if dashboard['is_public'] else "🔒"
        access_type = "Public" if dashboard['is_public'] else "Private"
        print(f"\n   Access Type: {access_icon} {access_type}")
        
        # Ownership
        print(f"\n   Ownership:")
        if dashboard['owner']:
            print(f"     Owner: {dashboard['owner']}")
        if dashboard['created_by']:
            print(f"     Created By: {dashboard['created_by']}")
        if dashboard['modified_by']:
            print(f"     Last Modified By: {dashboard['modified_by']}")
        
        # Sharing Details
        if dashboard['shared_with']:
            shared_list = dashboard['shared_with']
            print(f"\n   Shared With ({len(shared_list)} users/groups):")
            
            # Analyze sharing patterns
            users = []
            groups = []
            departments = []
            
            for entity in shared_list:
                if isinstance(entity, dict):
                    entity_type = entity.get('Type', 'User')
                    entity_name = entity.get('Name', 'Unknown')
                    entity_role = entity.get('Role', 'Viewer')
                    
                    if entity_type == 'Group':
                        groups.append(entity_name)
                        print(f"     👥 Group: {entity_name} ({entity_role})")
                    elif entity_type == 'Department':
                        departments.append(entity_name)
                        print(f"     🏢 Department: {entity_name} ({entity_role})")
                    else:
                        users.append(entity_name)
                        print(f"     👤 User: {entity_name} ({entity_role})")
                    
                    # Show additional permissions if available
                    if entity.get('Permissions'):
                        perms = entity['Permissions']
                        perm_list = []
                        if perms.get('View'): perm_list.append('View')
                        if perms.get('Edit'): perm_list.append('Edit')
                        if perms.get('Delete'): perm_list.append('Delete')
                        if perms.get('Share'): perm_list.append('Share')
                        if perms.get('Export'): perm_list.append('Export')
                        if perm_list:
                            print(f"        Permissions: {', '.join(perm_list)}")
                    
                    # Show access expiry if available
                    if entity.get('ExpiresAt'):
                        print(f"        Expires: {format_timestamp(entity['ExpiresAt'])}")
                    
                    # Show last access if available
                    if entity.get('LastAccessedAt'):
                        print(f"        Last Accessed: {format_timestamp(entity['LastAccessedAt'])}")
                else:
                    # Simple string format
                    users.append(entity)
                    print(f"     👤 {entity}")
            
            # Sharing summary
            if len(shared_list) > 5:
                print(f"\n     Summary:")
                if users:
                    print(f"       • {len(users)} individual users")
                if groups:
                    print(f"       • {len(groups)} groups")
                if departments:
                    print(f"       • {len(departments)} departments")
        
        # Permissions
        if dashboard['permissions']:
            perms = dashboard['permissions']
            print(f"\n   Default Permissions:")
            
            # Display permissions with icons
            perm_icons = {
                'View': '👁️',
                'Edit': '✏️',
                'Delete': '🗑️',
                'Share': '🔗',
                'Export': '📤',
                'Print': '🖨️',
                'Download': '⬇️',
                'Comment': '💬',
                'Annotate': '📝'
            }
            
            for perm, enabled in perms.items():
                if isinstance(enabled, bool):
                    status = "✅" if enabled else "❌"
                    icon = perm_icons.get(perm, '•')
                    print(f"     {icon} {perm}: {status}")
                elif isinstance(enabled, dict):
                    # Complex permission with conditions
                    print(f"     • {perm}:")
                    for key, value in enabled.items():
                        print(f"       - {key}: {value}")
    
    # Access Control Matrix (if multiple dashboards)
    if len(sharing_info['dashboards']) > 1:
        print(f"\n" + "="*70)
        print("ACCESS CONTROL MATRIX")
        print("-" * 70)
        
        # Collect all unique users/groups
        all_entities = set()
        for dashboard in sharing_info['dashboards']:
            for entity in dashboard['shared_with']:
                if isinstance(entity, dict):
                    all_entities.add(entity.get('Name', 'Unknown'))
                else:
                    all_entities.add(entity)
        
        if all_entities:
            print(f"\nUsers/Groups with Access ({len(all_entities)} total):")
            for entity in sorted(all_entities)[:10]:  # Show first 10
                # Count how many dashboards this entity has access to
                access_count = 0
                for dashboard in sharing_info['dashboards']:
                    for shared_entity in dashboard['shared_with']:
                        if isinstance(shared_entity, dict):
                            if shared_entity.get('Name') == entity:
                                access_count += 1
                                break
                        elif shared_entity == entity:
                            access_count += 1
                            break
                
                if access_count > 0:
                    percent = (access_count / len(sharing_info['dashboards'])) * 100
                    bar = '█' * int(percent / 10)
                    print(f"  {entity}: {access_count}/{len(sharing_info['dashboards'])} dashboards [{bar}]")
            
            if len(all_entities) > 10:
                print(f"  ... and {len(all_entities) - 10} more")
    
    # Security Recommendations
    print(f"\n" + "="*70)
    print("🔒 SECURITY RECOMMENDATIONS")
    print("-" * 70)
    
    recommendations = []
    
    # Check for overly public dashboards
    if sharing_info['public_dashboards'] > sharing_info['total_dashboards'] * 0.5:
        recommendations.append("⚠️  High percentage of public dashboards - Review if all need public access")
    
    # Check for dashboards without owners
    orphaned = [d for d in sharing_info['dashboards'] if not d['owner']]
    if orphaned:
        recommendations.append(f"⚠️  {len(orphaned)} dashboard(s) without defined owners")
    
    # Check for overly shared dashboards
    overshared = [d for d in sharing_info['dashboards'] if len(d['shared_with']) > 20]
    if overshared:
        recommendations.append(f"⚠️  {len(overshared)} dashboard(s) shared with >20 entities - Consider using groups")
    
    # Check for good practices
    if sharing_info['shared_dashboards'] > 0 and sharing_info['public_dashboards'] < sharing_info['total_dashboards'] * 0.3:
        recommendations.append("✅ Good balance of public vs. private dashboards")
    
    groups_used = any(
        any(isinstance(e, dict) and e.get('Type') == 'Group' for e in d['shared_with'])
        for d in sharing_info['dashboards']
    )
    if groups_used:
        recommendations.append("✅ Using groups for access management (best practice)")
    
    if recommendations:
        for rec in recommendations:
            print(f"  {rec}")
    else:
        print("  ✅ No security concerns detected")
    
    print("\n" + "="*70)


def analyze_sharing_patterns(sharing_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze sharing patterns across dashboards.
    
    Args:
        sharing_info: Dictionary containing sharing information
        
    Returns:
        Dictionary with analysis results
    """
    analysis = {
        'most_shared': None,
        'least_shared': None,
        'avg_shares': 0,
        'common_users': {},
        'access_distribution': {},
        'permission_patterns': {}
    }
    
    if not sharing_info['dashboards']:
        return analysis
    
    # Find most and least shared dashboards
    dashboards_by_shares = sorted(
        sharing_info['dashboards'],
        key=lambda x: len(x['shared_with']),
        reverse=True
    )
    
    if dashboards_by_shares:
        analysis['most_shared'] = {
            'name': dashboards_by_shares[0]['name'],
            'share_count': len(dashboards_by_shares[0]['shared_with'])
        }
        analysis['least_shared'] = {
            'name': dashboards_by_shares[-1]['name'],
            'share_count': len(dashboards_by_shares[-1]['shared_with'])
        }
    
    # Calculate average shares
    total_shares = sum(len(d['shared_with']) for d in sharing_info['dashboards'])
    if sharing_info['dashboards']:
        analysis['avg_shares'] = total_shares / len(sharing_info['dashboards'])
    
    # Find common users across dashboards
    user_access_count = {}
    for dashboard in sharing_info['dashboards']:
        for entity in dashboard['shared_with']:
            if isinstance(entity, dict):
                name = entity.get('Name', 'Unknown')
            else:
                name = entity
            
            user_access_count[name] = user_access_count.get(name, 0) + 1
    
    # Get top users with most access
    analysis['common_users'] = dict(
        sorted(user_access_count.items(), key=lambda x: x[1], reverse=True)[:5]
    )
    
    # Analyze permission patterns
    for dashboard in sharing_info['dashboards']:
        if dashboard['permissions']:
            for perm, enabled in dashboard['permissions'].items():
                if isinstance(enabled, bool) and enabled:
                    analysis['permission_patterns'][perm] = \
                        analysis['permission_patterns'].get(perm, 0) + 1
    
    return analysis


def main():
    """Main function to demonstrate dashboard sharing management."""
    print_header("Dashboard Sharing & Access Management")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Manage dashboard sharing and access')
    parser.add_argument('--project-id', help='Project ID (optional, will auto-discover if not provided)')
    parser.add_argument('--dashboard-id', help='Specific dashboard ID (optional)')
    parser.add_argument('--analyze', action='store_true', help='Show sharing pattern analysis')
    parser.add_argument('--brief', action='store_true', help='Show summary only')
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
        
        # Get sharing information
        sharing_info = get_dashboard_sharing_info(
            client,
            project_id,
            dashboard_id=args.dashboard_id
        )
        
        if not sharing_info:
            print_error("Failed to retrieve sharing information")
            return
        
        # Display sharing information
        display_sharing_info(sharing_info, detailed=not args.brief)
        
        # Analyze patterns if requested
        if args.analyze and sharing_info['dashboards']:
            analysis = analyze_sharing_patterns(sharing_info)
            
            print(f"\n" + "="*70)
            print("SHARING PATTERN ANALYSIS")
            print("-" * 70)
            
            if analysis['most_shared']:
                print(f"\nMost Shared Dashboard:")
                print(f"  {analysis['most_shared']['name']} "
                      f"({analysis['most_shared']['share_count']} shares)")
            
            if analysis['least_shared']:
                print(f"\nLeast Shared Dashboard:")
                print(f"  {analysis['least_shared']['name']} "
                      f"({analysis['least_shared']['share_count']} shares)")
            
            print(f"\nAverage Shares per Dashboard: {analysis['avg_shares']:.1f}")
            
            if analysis['common_users']:
                print(f"\nUsers with Most Dashboard Access:")
                for user, count in analysis['common_users'].items():
                    percent = (count / len(sharing_info['dashboards'])) * 100
                    print(f"  • {user}: {count} dashboards ({percent:.0f}%)")
            
            if analysis['permission_patterns']:
                print(f"\nCommon Permissions Enabled:")
                for perm, count in sorted(analysis['permission_patterns'].items(), 
                                         key=lambda x: x[1], reverse=True):
                    percent = (count / len(sharing_info['dashboards'])) * 100
                    print(f"  • {perm}: {count} dashboards ({percent:.0f}%)")
            
            print("\n" + "="*70)
        
        print_success("\nSharing information retrieved successfully!")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to get sharing information: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()