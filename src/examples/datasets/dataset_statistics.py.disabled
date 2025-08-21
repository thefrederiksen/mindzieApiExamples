"""
Analyze and display comprehensive dataset statistics.

This example demonstrates how to:
- Calculate aggregate statistics across all datasets
- Analyze dataset growth and trends
- Identify data quality issues
- Generate usage reports
- Compare dataset characteristics
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mindzie_api import MindzieAPIClient
from mindzie_api.exceptions import MindzieAPIException
from common_utils import (
    get_client_config,
    discover_project,
    format_timestamp,
    format_size_mb,
    print_header,
    print_error,
    print_success,
    print_info
)


def calculate_statistics(datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics for a collection of datasets.
    
    Args:
        datasets: List of dataset dictionaries
        
    Returns:
        Dictionary containing calculated statistics
    """
    stats = {
        'total_count': len(datasets),
        'total_size_mb': 0,
        'total_rows': 0,
        'total_columns': 0,
        'avg_size_mb': 0,
        'avg_rows': 0,
        'avg_columns': 0,
        'max_size_mb': 0,
        'min_size_mb': float('inf'),
        'largest_dataset': None,
        'smallest_dataset': None,
        'types': defaultdict(int),
        'statuses': defaultdict(int),
        'sources': defaultdict(int),
        'quality_metrics': {
            'avg_completeness': 0,
            'avg_accuracy': 0,
            'datasets_with_quality': 0
        },
        'time_analysis': {
            'newest_dataset': None,
            'oldest_dataset': None,
            'recently_modified': 0,
            'recently_accessed': 0,
            'stale_datasets': 0
        },
        'usage_stats': {
            'total_access_count': 0,
            'avg_access_count': 0,
            'most_accessed': None,
            'least_accessed': None
        }
    }
    
    if not datasets:
        return stats
    
    # Initialize tracking variables
    sizes = []
    row_counts = []
    column_counts = []
    access_counts = []
    completeness_scores = []
    accuracy_scores = []
    
    newest_date = None
    oldest_date = None
    newest_dataset = None
    oldest_dataset = None
    
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Process each dataset
    for dataset in datasets:
        name = dataset.get('DatasetName', 'Unnamed')
        
        # Size statistics
        if dataset.get('SizeMB') is not None:
            size = dataset['SizeMB']
            sizes.append(size)
            stats['total_size_mb'] += size
            
            if size > stats['max_size_mb']:
                stats['max_size_mb'] = size
                stats['largest_dataset'] = name
            
            if size < stats['min_size_mb']:
                stats['min_size_mb'] = size
                stats['smallest_dataset'] = name
        
        # Row and column statistics
        if dataset.get('RowCount') is not None:
            rows = dataset['RowCount']
            row_counts.append(rows)
            stats['total_rows'] += rows
        
        if dataset.get('ColumnCount') is not None:
            cols = dataset['ColumnCount']
            column_counts.append(cols)
            stats['total_columns'] += cols
        
        # Type and status distribution
        if dataset.get('DatasetType'):
            stats['types'][dataset['DatasetType']] += 1
        
        if dataset.get('Status'):
            stats['statuses'][dataset['Status']] += 1
        
        if dataset.get('SourceType'):
            stats['sources'][dataset['SourceType']] += 1
        
        # Quality metrics
        if dataset.get('DataQuality'):
            quality = dataset['DataQuality']
            if quality.get('Completeness') is not None:
                completeness_scores.append(quality['Completeness'])
            if quality.get('Accuracy') is not None:
                accuracy_scores.append(quality['Accuracy'])
            stats['quality_metrics']['datasets_with_quality'] += 1
        
        # Time analysis
        if dataset.get('CreatedAt'):
            try:
                created = datetime.fromisoformat(dataset['CreatedAt'].replace('Z', '+00:00'))
                if newest_date is None or created > newest_date:
                    newest_date = created
                    newest_dataset = name
                if oldest_date is None or created < oldest_date:
                    oldest_date = created
                    oldest_dataset = name
            except:
                pass
        
        if dataset.get('ModifiedAt'):
            try:
                modified = datetime.fromisoformat(dataset['ModifiedAt'].replace('Z', '+00:00'))
                if modified > week_ago:
                    stats['time_analysis']['recently_modified'] += 1
                elif modified < month_ago:
                    stats['time_analysis']['stale_datasets'] += 1
            except:
                pass
        
        if dataset.get('LastAccessedAt'):
            try:
                accessed = datetime.fromisoformat(dataset['LastAccessedAt'].replace('Z', '+00:00'))
                if accessed > week_ago:
                    stats['time_analysis']['recently_accessed'] += 1
            except:
                pass
        
        # Usage statistics
        if dataset.get('UsageStats'):
            usage = dataset['UsageStats']
            if usage.get('AccessCount') is not None:
                access_count = usage['AccessCount']
                access_counts.append(access_count)
                stats['usage_stats']['total_access_count'] += access_count
                
                if (stats['usage_stats']['most_accessed'] is None or 
                    access_count > stats['usage_stats'].get('max_access_count', 0)):
                    stats['usage_stats']['most_accessed'] = name
                    stats['usage_stats']['max_access_count'] = access_count
                
                if (stats['usage_stats']['least_accessed'] is None or 
                    access_count < stats['usage_stats'].get('min_access_count', float('inf'))):
                    stats['usage_stats']['least_accessed'] = name
                    stats['usage_stats']['min_access_count'] = access_count
    
    # Calculate averages
    if sizes:
        stats['avg_size_mb'] = sum(sizes) / len(sizes)
    if row_counts:
        stats['avg_rows'] = sum(row_counts) / len(row_counts)
    if column_counts:
        stats['avg_columns'] = sum(column_counts) / len(column_counts)
    if completeness_scores:
        stats['quality_metrics']['avg_completeness'] = sum(completeness_scores) / len(completeness_scores)
    if accuracy_scores:
        stats['quality_metrics']['avg_accuracy'] = sum(accuracy_scores) / len(accuracy_scores)
    if access_counts:
        stats['usage_stats']['avg_access_count'] = sum(access_counts) / len(access_counts)
    
    # Set time analysis results
    stats['time_analysis']['newest_dataset'] = newest_dataset
    stats['time_analysis']['oldest_dataset'] = oldest_dataset
    
    # Clean up infinity values
    if stats['min_size_mb'] == float('inf'):
        stats['min_size_mb'] = 0
    
    return stats


def display_statistics(stats: Dict[str, Any]):
    """
    Display statistics in a formatted manner.
    
    Args:
        stats: Dictionary containing calculated statistics
    """
    print("\n" + "="*70)
    print("DATASET STATISTICS REPORT")
    print("="*70)
    
    # Overall Summary
    print("\n📊 OVERALL SUMMARY")
    print("-" * 40)
    print(f"Total Datasets: {stats['total_count']}")
    
    if stats['total_count'] > 0:
        # Size Statistics
        print(f"\n💾 SIZE STATISTICS")
        print("-" * 40)
        print(f"Total Size: {format_size_mb(stats['total_size_mb'])}")
        print(f"Average Size: {format_size_mb(stats['avg_size_mb'])}")
        print(f"Largest: {stats['largest_dataset']} ({format_size_mb(stats['max_size_mb'])})")
        if stats['smallest_dataset']:
            print(f"Smallest: {stats['smallest_dataset']} ({format_size_mb(stats['min_size_mb'])})")
        
        # Data Volume
        print(f"\n📈 DATA VOLUME")
        print("-" * 40)
        if stats['total_rows'] > 0:
            print(f"Total Rows: {stats['total_rows']:,}")
            print(f"Average Rows: {stats['avg_rows']:,.0f}")
        if stats['total_columns'] > 0:
            print(f"Total Columns: {stats['total_columns']:,}")
            print(f"Average Columns: {stats['avg_columns']:.1f}")
        
        # Type Distribution
        if stats['types']:
            print(f"\n📁 DATASET TYPES")
            print("-" * 40)
            for dtype, count in sorted(stats['types'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats['total_count']) * 100
                print(f"{dtype}: {count} ({percentage:.1f}%)")
        
        # Status Distribution
        if stats['statuses']:
            print(f"\n🚦 STATUS DISTRIBUTION")
            print("-" * 40)
            for status, count in sorted(stats['statuses'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats['total_count']) * 100
                bar = '█' * int(percentage / 5)
                print(f"{status}: {count} ({percentage:.1f}%) {bar}")
        
        # Source Types
        if stats['sources']:
            print(f"\n🔗 DATA SOURCES")
            print("-" * 40)
            for source, count in sorted(stats['sources'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats['total_count']) * 100
                print(f"{source}: {count} ({percentage:.1f}%)")
        
        # Data Quality
        quality = stats['quality_metrics']
        if quality['datasets_with_quality'] > 0:
            print(f"\n✅ DATA QUALITY METRICS")
            print("-" * 40)
            print(f"Datasets with Quality Info: {quality['datasets_with_quality']}")
            if quality['avg_completeness'] > 0:
                print(f"Average Completeness: {quality['avg_completeness']:.1f}%")
            if quality['avg_accuracy'] > 0:
                print(f"Average Accuracy: {quality['avg_accuracy']:.1f}%")
        
        # Time Analysis
        time_stats = stats['time_analysis']
        print(f"\n🕐 TIME ANALYSIS")
        print("-" * 40)
        if time_stats['newest_dataset']:
            print(f"Newest Dataset: {time_stats['newest_dataset']}")
        if time_stats['oldest_dataset']:
            print(f"Oldest Dataset: {time_stats['oldest_dataset']}")
        print(f"Recently Modified (7 days): {time_stats['recently_modified']}")
        print(f"Recently Accessed (7 days): {time_stats['recently_accessed']}")
        if time_stats['stale_datasets'] > 0:
            print(f"⚠️  Stale Datasets (>30 days): {time_stats['stale_datasets']}")
        
        # Usage Statistics
        usage = stats['usage_stats']
        if usage['total_access_count'] > 0:
            print(f"\n📊 USAGE STATISTICS")
            print("-" * 40)
            print(f"Total Accesses: {usage['total_access_count']:,}")
            print(f"Average Access Count: {usage['avg_access_count']:.0f}")
            if usage['most_accessed']:
                print(f"Most Accessed: {usage['most_accessed']} ({usage.get('max_access_count', 0):,} times)")
            if usage['least_accessed']:
                print(f"Least Accessed: {usage['least_accessed']} ({usage.get('min_access_count', 0):,} times)")
        
        # Insights and Recommendations
        print(f"\n💡 INSIGHTS & RECOMMENDATIONS")
        print("-" * 40)
        
        # Size insights
        if stats['max_size_mb'] > 1000:  # > 1GB
            print("⚠️  Large datasets detected (>1GB) - Consider optimization")
        
        # Stale data warning
        if time_stats['stale_datasets'] > stats['total_count'] * 0.3:
            print("⚠️  Many datasets haven't been updated recently")
        
        # Low access warning
        if usage['total_access_count'] > 0 and time_stats['recently_accessed'] < stats['total_count'] * 0.2:
            print("⚠️  Low dataset utilization - Review unused datasets")
        
        # Quality issues
        if quality['datasets_with_quality'] > 0:
            if quality['avg_completeness'] < 80:
                print("⚠️  Data completeness below 80% - Review data quality")
            if quality['avg_accuracy'] < 90:
                print("⚠️  Data accuracy concerns - Validation recommended")
        
        # Success indicators
        if time_stats['recently_modified'] > stats['total_count'] * 0.5:
            print("✅ Good data freshness - Majority recently updated")
        
        if usage['total_access_count'] > stats['total_count'] * 100:
            print("✅ High dataset utilization")
    
    print("\n" + "="*70)


def analyze_datasets(
    client: MindzieAPIClient,
    project_id: str
) -> Optional[Dict[str, Any]]:
    """
    Analyze datasets and generate statistics.
    
    Args:
        client: The mindzie API client
        project_id: The project ID
        
    Returns:
        Statistics dictionary or None if error
    """
    try:
        print_info(f"Fetching datasets for project {project_id}...")
        
        # Get all datasets
        response = client.datasets.get_all(project_id)
        
        if not response or not response.get("Items"):
            print_info("No datasets found for analysis")
            return None
        
        datasets = response["Items"]
        print_success(f"Found {len(datasets)} dataset(s) to analyze")
        
        # Calculate statistics
        print_info("Calculating statistics...")
        stats = calculate_statistics(datasets)
        
        # Display statistics
        display_statistics(stats)
        
        return stats
        
    except MindzieAPIException as e:
        print_error(f"API error: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return None


def main():
    """Main function to demonstrate dataset statistics."""
    print_header("Dataset Statistics Analysis")
    
    # Get configuration
    config = get_client_config()
    if not config:
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Analyze dataset statistics')
    parser.add_argument('--project-id', help='Project ID (optional, will auto-discover if not provided)')
    parser.add_argument('--export', help='Export statistics to JSON file')
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
        
        # Analyze datasets
        stats = analyze_datasets(client, project_id)
        
        if stats:
            print_success("\nDataset analysis completed successfully!")
            
            # Export if requested
            if args.export:
                import json
                with open(args.export, 'w') as f:
                    json.dump(stats, f, indent=2, default=str)
                print_success(f"Statistics exported to {args.export}")
        
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
    except Exception as e:
        print_error(f"Failed to analyze datasets: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()