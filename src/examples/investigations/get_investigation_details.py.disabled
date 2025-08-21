"""
Get detailed information about a specific investigation.

This example demonstrates how to:
- Retrieve comprehensive investigation metadata
- Display findings and recommendations
- Show investigation workflow and timeline
- Access investigation results and artifacts
- Auto-discover investigations when no ID is provided
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


def discover_investigation(client: MindzieAPIClient, project_id: str) -> Optional[str]:
    """
    Auto-discover an investigation from the project.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        
    Returns:
        Investigation ID or None if no investigations found
    """
    try:
        print_info("Discovering available investigations...")
        response = client.investigations.get_all(
            project_id=project_id,
            page=1,
            page_size=10
        )
        
        if not response or not response.get("Investigations"):
            print_info("No investigations found in this project")
            return None
        
        investigations = response["Investigations"]
        
        if len(investigations) == 1:
            investigation = investigations[0]
            print_success(f"Found investigation: {investigation.get('InvestigationName', 'Unnamed')}")
            return investigation.get('InvestigationId')
        
        # Multiple investigations - let user choose
        print_info(f"Found {len(investigations)} investigations:")
        for idx, investigation in enumerate(investigations[:10], 1):  # Show max 10
            status = investigation.get('Status', 'Unknown')
            print(f"  {idx}. {investigation.get('InvestigationName', 'Unnamed')} "
                  f"(Status: {status}, ID: {investigation.get('InvestigationId', 'N/A')})")
        
        # Use the first one for demonstration
        selected = investigations[0]
        print_info(f"Using first investigation: {selected.get('InvestigationName', 'Unnamed')}")
        return selected.get('InvestigationId')
        
    except Exception as e:
        print_error(f"Failed to discover investigations: {e}")
        return None


def get_investigation_details(
    client: MindzieAPIClient,
    project_id: str,
    investigation_id: str,
    show_findings: bool = True,
    show_timeline: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about an investigation.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        investigation_id: The investigation ID
        show_findings: Whether to display findings
        show_timeline: Whether to show timeline
        
    Returns:
        Dictionary containing investigation details or None if error
    """
    try:
        print_info(f"Fetching details for investigation {investigation_id}...")
        
        # Note: Since there's no specific get_by_id method for investigations,
        # we'll get all investigations and filter
        response = client.investigations.get_all(
            project_id=project_id,
            page=1,
            page_size=100  # Get more to find our investigation
        )
        
        if not response or not response.get("Investigations"):
            print_error("No investigations found")
            return None
        
        # Find the specific investigation
        investigation = None
        for item in response["Investigations"]:
            if item.get("InvestigationId") == investigation_id:
                investigation = item
                break
        
        if not investigation:
            print_error(f"Investigation {investigation_id} not found")
            return None
        
        print_success(f"Retrieved investigation: {investigation.get('InvestigationName', 'Unnamed')}")
        
        # Display comprehensive investigation information
        print("\n" + "="*70)
        print("INVESTIGATION DETAILS")
        print("="*70)
        
        # Basic Information
        print("\n🔍 Basic Information:")
        print(f"   Name: {investigation.get('InvestigationName', 'N/A')}")
        print(f"   ID: {investigation.get('InvestigationId', 'N/A')}")
        print(f"   Type: {investigation.get('InvestigationType', 'Unknown')}")
        
        # Status and Priority
        status = investigation.get('Status', 'Unknown')
        status_icon = {
            'Completed': '✅',
            'InProgress': '🔄',
            'Pending': '⏳',
            'Failed': '❌',
            'Cancelled': '⚠️'
        }.get(status, '❓')
        print(f"   Status: {status_icon} {status}")
        
        if investigation.get('Priority'):
            priority = investigation['Priority']
            priority_icon = {
                'Critical': '🔴',
                'High': '🟠',
                'Medium': '🟡',
                'Low': '🟢'
            }.get(priority, '⚪')
            print(f"   Priority: {priority_icon} {priority}")
        
        if investigation.get('Severity'):
            print(f"   Severity: {investigation['Severity']}")
        
        # Description and Purpose
        if investigation.get('Description'):
            print(f"\n📝 Description:")
            print(f"   {investigation['Description']}")
        
        if investigation.get('Purpose'):
            print(f"\n🎯 Purpose:")
            print(f"   {investigation['Purpose']}")
        
        # Ownership and Assignment
        print(f"\n👥 Assignment:")
        if investigation.get('Owner'):
            print(f"   Owner: {investigation['Owner']}")
        if investigation.get('AssignedTo'):
            print(f"   Assigned To: {investigation['AssignedTo']}")
        if investigation.get('Team'):
            print(f"   Team: {investigation['Team']}")
        if investigation.get('Department'):
            print(f"   Department: {investigation['Department']}")
        
        # Timeline
        if show_timeline:
            print(f"\n🕐 Timeline:")
            if investigation.get('CreatedAt'):
                print(f"   Created: {format_timestamp(investigation['CreatedAt'])}")
            if investigation.get('StartedAt'):
                print(f"   Started: {format_timestamp(investigation['StartedAt'])}")
            if investigation.get('CompletedAt'):
                print(f"   Completed: {format_timestamp(investigation['CompletedAt'])}")
            if investigation.get('LastModifiedAt'):
                print(f"   Last Modified: {format_timestamp(investigation['LastModifiedAt'])}")
            if investigation.get('DueDate'):
                print(f"   Due Date: {format_timestamp(investigation['DueDate'])}")
            
            # Duration calculation
            if investigation.get('Duration'):
                duration = investigation['Duration']
                if isinstance(duration, (int, float)):
                    hours = duration / 3600
                    days = hours / 24
                    if days >= 1:
                        print(f"   Duration: {days:.1f} days ({hours:.1f} hours)")
                    else:
                        print(f"   Duration: {hours:.1f} hours")
                else:
                    print(f"   Duration: {duration}")
        
        # Progress and Metrics
        if investigation.get('Progress') is not None:
            progress = investigation['Progress']
            bar_length = 30
            filled = int(bar_length * progress / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\n📊 Progress: [{bar}] {progress}%")
        
        if investigation.get('Metrics'):
            metrics = investigation['Metrics']
            print(f"\n📈 Metrics:")
            for key, value in metrics.items():
                print(f"   {key}: {value}")
        
        # Findings and Results
        if show_findings:
            print(f"\n🔎 Findings & Results:")
            
            if investigation.get('FindingsCount') is not None:
                print(f"   Total Findings: {investigation['FindingsCount']}")
            
            if investigation.get('Findings'):
                findings = investigation['Findings']
                if isinstance(findings, list):
                    for idx, finding in enumerate(findings[:5], 1):  # Show first 5
                        if isinstance(finding, dict):
                            print(f"\n   Finding {idx}:")
                            print(f"     Title: {finding.get('Title', 'N/A')}")
                            print(f"     Severity: {finding.get('Severity', 'N/A')}")
                            print(f"     Category: {finding.get('Category', 'N/A')}")
                            if finding.get('Description'):
                                desc = finding['Description']
                                if len(desc) > 100:
                                    desc = desc[:97] + "..."
                                print(f"     Description: {desc}")
                        else:
                            print(f"   • {finding}")
                    
                    if len(findings) > 5:
                        print(f"   ... and {len(findings) - 5} more findings")
            
            if investigation.get('IssuesFound') is not None:
                print(f"   Issues Found: {investigation['IssuesFound']}")
            
            if investigation.get('AnomaliesDetected') is not None:
                print(f"   Anomalies Detected: {investigation['AnomaliesDetected']}")
        
        # Recommendations
        if investigation.get('RecommendationsCount') is not None or investigation.get('Recommendations'):
            print(f"\n💡 Recommendations:")
            
            if investigation.get('RecommendationsCount') is not None:
                print(f"   Total Recommendations: {investigation['RecommendationsCount']}")
            
            if investigation.get('Recommendations'):
                recommendations = investigation['Recommendations']
                if isinstance(recommendations, list):
                    for idx, rec in enumerate(recommendations[:3], 1):  # Show first 3
                        if isinstance(rec, dict):
                            print(f"   {idx}. {rec.get('Title', 'N/A')}")
                            if rec.get('Priority'):
                                print(f"      Priority: {rec['Priority']}")
                            if rec.get('Description'):
                                print(f"      {rec['Description']}")
                        else:
                            print(f"   • {rec}")
                    
                    if len(recommendations) > 3:
                        print(f"   ... and {len(recommendations) - 3} more recommendations")
        
        # Data Sources and Scope
        print(f"\n📁 Data Scope:")
        
        if investigation.get('DataSources'):
            sources = investigation['DataSources']
            if isinstance(sources, list):
                print(f"   Data Sources ({len(sources)}):")
                for source in sources[:5]:
                    print(f"     • {source}")
                if len(sources) > 5:
                    print(f"     ... and {len(sources) - 5} more")
        
        if investigation.get('DatasetsAnalyzed'):
            datasets = investigation['DatasetsAnalyzed']
            if isinstance(datasets, list):
                print(f"   Datasets Analyzed ({len(datasets)}):")
                for dataset in datasets[:3]:
                    print(f"     • {dataset}")
        
        if investigation.get('DataVolume'):
            print(f"   Data Volume: {investigation['DataVolume']}")
        
        if investigation.get('RecordsProcessed') is not None:
            print(f"   Records Processed: {investigation['RecordsProcessed']:,}")
        
        # Workflow Information
        if investigation.get('WorkflowName') or investigation.get('WorkflowId'):
            print(f"\n⚙️ Workflow:")
            if investigation.get('WorkflowName'):
                print(f"   Name: {investigation['WorkflowName']}")
            if investigation.get('WorkflowId'):
                print(f"   ID: {investigation['WorkflowId']}")
            if investigation.get('WorkflowVersion'):
                print(f"   Version: {investigation['WorkflowVersion']}")
            if investigation.get('TriggeredBy'):
                print(f"   Triggered By: {investigation['TriggeredBy']}")
            if investigation.get('TriggerType'):
                print(f"   Trigger Type: {investigation['TriggerType']}")
            if investigation.get('Schedule'):
                print(f"   Schedule: {investigation['Schedule']}")
        
        # Related Items
        if (investigation.get('RelatedInvestigations') or 
            investigation.get('RelatedDatasets') or 
            investigation.get('RelatedIncidents')):
            print(f"\n🔗 Related Items:")
            
            if investigation.get('RelatedInvestigations'):
                related = investigation['RelatedInvestigations']
                if isinstance(related, list) and related:
                    print(f"   Related Investigations ({len(related)}):")
                    for item in related[:3]:
                        print(f"     • {item}")
            
            if investigation.get('RelatedDatasets'):
                datasets = investigation['RelatedDatasets']
                if isinstance(datasets, list) and datasets:
                    print(f"   Related Datasets ({len(datasets)}):")
                    for dataset in datasets[:3]:
                        print(f"     • {dataset}")
            
            if investigation.get('RelatedIncidents'):
                incidents = investigation['RelatedIncidents']
                if isinstance(incidents, list) and incidents:
                    print(f"   Related Incidents ({len(incidents)}):")
                    for incident in incidents[:3]:
                        print(f"     • {incident}")
        
        # Tags and Categories
        if investigation.get('Tags'):
            tags = investigation['Tags']
            if isinstance(tags, list) and tags:
                print(f"\n🏷️  Tags: {', '.join(tags)}")
        
        if investigation.get('Categories'):
            categories = investigation['Categories']
            if isinstance(categories, list) and categories:
                print(f"📂 Categories: {', '.join(categories)}")
        
        # Artifacts and Outputs
        if investigation.get('Artifacts') or investigation.get('OutputFiles'):
            print(f"\n📦 Artifacts & Outputs:")
            
            if investigation.get('Artifacts'):
                artifacts = investigation['Artifacts']
                if isinstance(artifacts, list):
                    print(f"   Artifacts ({len(artifacts)}):")
                    for artifact in artifacts[:3]:
                        if isinstance(artifact, dict):
                            print(f"     • {artifact.get('Name', 'N/A')} "
                                  f"({artifact.get('Type', 'Unknown')} - "
                                  f"{artifact.get('Size', 'N/A')})")
                        else:
                            print(f"     • {artifact}")
            
            if investigation.get('OutputFiles'):
                files = investigation['OutputFiles']
                if isinstance(files, list):
                    print(f"   Output Files ({len(files)}):")
                    for file in files[:3]:
                        print(f"     • {file}")
        
        # Configuration and Parameters
        if investigation.get('Configuration') or investigation.get('Parameters'):
            print(f"\n⚙️ Configuration:")
            
            if investigation.get('Configuration'):
                config = investigation['Configuration']
                if isinstance(config, dict):
                    for key, value in list(config.items())[:5]:
                        print(f"   {key}: {value}")
            
            if investigation.get('Parameters'):
                params = investigation['Parameters']
                if isinstance(params, dict):
                    print("   Parameters:")
                    for key, value in params.items():
                        print(f"     {key}: {value}")
        
        # Notes and Comments
        if investigation.get('Notes') or investigation.get('Comments'):
            print(f"\n📝 Notes & Comments:")
            
            if investigation.get('Notes'):
                print(f"   Notes: {investigation['Notes']}")
            
            if investigation.get('Comments'):
                comments = investigation['Comments']
                if isinstance(comments, list):
                    for comment in comments[:2]:
                        if isinstance(comment, dict):
                            print(f"   • {comment.get('Author', 'Unknown')}: {comment.get('Text', '')}")
                        else:
                            print(f"   • {comment}")
        
        # Audit Trail
        if investigation.get('AuditTrail'):
            trail = investigation['AuditTrail']
            if isinstance(trail, list) and trail:
                print(f"\n📋 Audit Trail (last 3 events):")
                for event in trail[:3]:
                    if isinstance(event, dict):
                        print(f"   • {event.get('Timestamp', 'N/A')}: "
                              f"{event.get('Action', 'N/A')} by {event.get('User', 'N/A')}")
                    else:
                        print(f"   • {event}")
        
        print("\n" + "="*70)
        
        return investigation
        
    except MindzieAPIException as e:
        print_error(f"API error: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return None


def main():
    """Main function to demonstrate getting investigation details."""
    print_header("Get Investigation Details Example")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Get detailed investigation information')
    parser.add_argument('--project-id', help='Project ID (optional, will auto-discover if not provided)')
    parser.add_argument('--investigation-id', help='Investigation ID (optional, will auto-discover if not provided)')
    parser.add_argument('--no-findings', action='store_true', help='Skip findings information')
    parser.add_argument('--no-timeline', action='store_true', help='Skip timeline information')
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
        
        # Get or discover investigation ID
        if args.investigation_id:
            investigation_id = args.investigation_id
            print_info(f"Using provided investigation ID: {investigation_id}")
        else:
            investigation_id = discover_investigation(client, project_id)
            if not investigation_id:
                print_error("No investigations available")
                return
        
        # Get investigation details
        result = get_investigation_details(
            client,
            project_id,
            investigation_id,
            show_findings=not args.no_findings,
            show_timeline=not args.no_timeline
        )
        
        if result:
            print_success("\nInvestigation details retrieved successfully!")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to get investigation details: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()