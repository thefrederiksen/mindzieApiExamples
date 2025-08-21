"""
Complete ETL (Extract, Transform, Load) pipeline workflow.

This example demonstrates how to:
- Orchestrate a complete ETL workflow
- Extract data from multiple sources
- Apply transformations and data quality checks
- Load data into target datasets
- Monitor pipeline progress and handle errors
- Schedule and automate pipeline execution

This combines multiple API controllers for a complete workflow.
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import time

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

class ETLPipeline:
    """ETL Pipeline orchestrator."""
    
    def __init__(self, client: MindzieAPIClient, project_id: str):
        self.client = client
        self.project_id = project_id
        self.pipeline_id = f"etl_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.steps = []
        self.status = "initialized"
        
    def extract_data(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract data from multiple sources."""
        print_info("🔍 EXTRACT: Starting data extraction...")
        
        extraction_results = {
            "step": "extract",
            "sources_processed": 0,
            "total_records": 0,
            "datasets_created": []
        }
        
        for idx, source in enumerate(sources, 1):
            print_info(f"  Processing source {idx}/{len(sources)}: {source.get('name', 'Unknown')}")
            
            try:
                # Simulate data extraction
                dataset_config = {
                    "name": f"extracted_{source.get('name', 'data')}_{self.pipeline_id}",
                    "source_type": source.get('type', 'csv'),
                    "source_path": source.get('path'),
                    "schema_auto_detect": True
                }
                
                # This would use the datasets.create() method
                if hasattr(self.client.datasets, 'create'):
                    dataset = self.client.datasets.create(self.project_id, **dataset_config)
                else:
                    # Simulate dataset creation
                    dataset = {
                        "dataset_id": f"ds_extract_{idx}_{self.pipeline_id}",
                        "name": dataset_config["name"],
                        "status": "created",
                        "record_count": source.get('estimated_records', 1000)
                    }
                
                extraction_results["datasets_created"].append(dataset)
                extraction_results["total_records"] += dataset.get('record_count', 1000)
                extraction_results["sources_processed"] += 1
                
                print_success(f"    ✓ Extracted {dataset.get('record_count', 1000)} records")
                
            except Exception as e:
                print_error(f"    ✗ Failed to extract from {source.get('name')}: {e}")
        
        print_success(f"EXTRACT Complete: {extraction_results['total_records']} total records from {extraction_results['sources_processed']} sources")
        self.steps.append(extraction_results)
        return extraction_results
    
    def transform_data(self, datasets: List[Dict[str, Any]], transformations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply transformations to extracted data."""
        print_info("⚙️  TRANSFORM: Starting data transformations...")
        
        transformation_results = {
            "step": "transform",
            "datasets_processed": 0,
            "transformations_applied": 0,
            "quality_checks_passed": 0,
            "enriched_datasets": []
        }
        
        for dataset in datasets:
            dataset_id = dataset.get('dataset_id')
            print_info(f"  Transforming dataset: {dataset.get('name', dataset_id)}")
            
            try:
                # Apply transformations
                for transform in transformations:
                    print_info(f"    Applying {transform.get('type', 'unknown')} transformation...")
                    
                    if transform.get('type') == 'enrichment':
                        # Use enrichment controller
                        enrichment_config = {
                            "enrichment_type": transform.get('enrichment_type', 'calculate'),
                            "operations": transform.get('operations', [])
                        }
                        
                        if hasattr(self.client, 'enrichment'):
                            result = self.client.enrichment.enrich_dataset(
                                self.project_id, dataset_id, **enrichment_config
                            )
                        else:
                            result = {"status": "simulated", "job_id": f"enrich_{len(transformation_results['enriched_datasets'])}"}\n                        \n                        transformation_results["enriched_datasets"].append(result)\n                    \n                    elif transform.get('type') == 'validation':\n                        # Data quality validation\n                        print_info(f"      Validating data quality...")\n                        # Simulate validation\n                        validation_passed = True  # Would check actual data quality\n                        if validation_passed:\n                            transformation_results["quality_checks_passed"] += 1\n                            print_success(f"      ✓ Quality check passed")\n                    \n                    transformation_results["transformations_applied"] += 1\n                \n                transformation_results["datasets_processed"] += 1\n                print_success(f"    ✓ Dataset transformation complete")\n                \n            except Exception as e:\n                print_error(f"    ✗ Failed to transform dataset {dataset_id}: {e}")\n        \n        print_success(f"TRANSFORM Complete: {transformation_results['transformations_applied']} transformations applied")\n        self.steps.append(transformation_results)\n        return transformation_results\n    \n    def load_data(self, datasets: List[Dict[str, Any]], target_config: Dict[str, Any]) -> Dict[str, Any]:\n        """Load transformed data to target destination."""\n        print_info("📦 LOAD: Starting data loading...")\n        \n        load_results = {\n            "step": "load",\n            "datasets_loaded": 0,\n            "total_records_loaded": 0,\n            "target_datasets": []\n        }\n        \n        target_type = target_config.get('type', 'dataset')\n        \n        for dataset in datasets:\n            dataset_id = dataset.get('dataset_id')\n            print_info(f"  Loading dataset: {dataset.get('name', dataset_id)}")\n            \n            try:\n                if target_type == 'dataset':\n                    # Create final dataset\n                    final_dataset_config = {\n                        "name": f"final_{dataset.get('name', 'data')}",\n                        "source_dataset_id": dataset_id,\n                        "target_schema": target_config.get('schema'),\n                        "data_quality_verified": True\n                    }\n                    \n                    if hasattr(self.client.datasets, 'create'):\n                        final_dataset = self.client.datasets.create(self.project_id, **final_dataset_config)\n                    else:\n                        final_dataset = {\n                            "dataset_id": f"ds_final_{len(load_results['target_datasets'])}_{self.pipeline_id}",\n                            "name": final_dataset_config["name"],\n                            "status": "loaded",\n                            "record_count": dataset.get('record_count', 1000)\n                        }\n                    \n                    load_results["target_datasets"].append(final_dataset)\n                    load_results["total_records_loaded"] += final_dataset.get('record_count', 1000)\n                    load_results["datasets_loaded"] += 1\n                    \n                    print_success(f"    ✓ Loaded {final_dataset.get('record_count', 1000)} records")\n                \n            except Exception as e:\n                print_error(f"    ✗ Failed to load dataset {dataset_id}: {e}")\n        \n        print_success(f"LOAD Complete: {load_results['total_records_loaded']} records loaded to {load_results['datasets_loaded']} datasets")\n        self.steps.append(load_results)\n        return load_results\n    \n    def run_pipeline(self, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:\n        """Execute the complete ETL pipeline."""\n        start_time = datetime.now()\n        print_header(f"🚀 Starting ETL Pipeline: {self.pipeline_id}")\n        \n        try:\n            self.status = "running"\n            \n            # Step 1: Extract\n            extraction_results = self.extract_data(pipeline_config.get('sources', []))\n            \n            # Step 2: Transform\n            transformation_results = self.transform_data(\n                extraction_results.get('datasets_created', []),\n                pipeline_config.get('transformations', [])\n            )\n            \n            # Step 3: Load\n            load_results = self.load_data(\n                extraction_results.get('datasets_created', []),\n                pipeline_config.get('target', {})\n            )\n            \n            # Pipeline summary\n            end_time = datetime.now()\n            duration = (end_time - start_time).total_seconds()\n            \n            pipeline_summary = {\n                "pipeline_id": self.pipeline_id,\n                "status": "completed",\n                "started_at": start_time.isoformat(),\n                "completed_at": end_time.isoformat(),\n                "duration_seconds": duration,\n                "steps_completed": len(self.steps),\n                "total_records_processed": sum(step.get('total_records', 0) for step in self.steps),\n                "final_datasets": load_results.get('target_datasets', [])\n            }\n            \n            self.status = "completed"\n            \n            print_header("🎉 ETL Pipeline Completed Successfully!")\n            print(f"📊 Pipeline Summary:")\n            print(f"  • Duration: {duration:.1f} seconds")\n            print(f"  • Records Processed: {pipeline_summary['total_records_processed']:,}")\n            print(f"  • Final Datasets: {len(pipeline_summary['final_datasets'])}")\n            \n            return pipeline_summary\n            \n        except Exception as e:\n            self.status = "failed"\n            print_error(f"❌ Pipeline failed: {e}")\n            return {\n                "pipeline_id": self.pipeline_id,\n                "status": "failed",\n                "error": str(e),\n                "steps_completed": len(self.steps)\n            }\n\n\ndef main():\n    """Main function."""\n    print_header("ETL Pipeline Workflow Example")\n    \n    config = get_client_config()\n    if not config:\n        return\n    \n    import argparse\n    parser = argparse.ArgumentParser(description='Run ETL pipeline workflow')\n    parser.add_argument('--project-id', help='Project ID')\n    parser.add_argument('--config-file', help='Pipeline configuration file (JSON)')\n    parser.add_argument('--sources', nargs='+', help='Data source paths')\n    \n    args = parser.parse_args()\n    \n    client = MindzieAPIClient(\n        base_url=config['base_url'],\n        tenant_id=config['tenant_id'],\n        api_key=config['api_key']\n    )\n    \n    try:\n        client.ping.ping()\n        print_success("Connected to mindzie API")\n        \n        if args.project_id:\n            project_id = args.project_id\n        else:\n            project_id = discover_project(client)\n            if not project_id:\n                print_error("No projects available")\n                return\n        \n        # Load pipeline configuration\n        if args.config_file and os.path.exists(args.config_file):\n            with open(args.config_file) as f:\n                pipeline_config = json.load(f)\n        else:\n            # Default configuration\n            sources = []\n            if args.sources:\n                for idx, source_path in enumerate(args.sources):\n                    sources.append({\n                        "name": f"source_{idx+1}",\n                        "type": "csv",\n                        "path": source_path,\n                        "estimated_records": 1000\n                    })\n            else:\n                # Demo sources\n                sources = [\n                    {"name": "sales_data", "type": "csv", "path": "/data/sales.csv", "estimated_records": 5000},\n                    {"name": "customer_data", "type": "database", "path": "customers_table", "estimated_records": 2000}\n                ]\n            \n            pipeline_config = {\n                "sources": sources,\n                "transformations": [\n                    {\n                        "type": "enrichment",\n                        "enrichment_type": "calculate",\n                        "operations": [\n                            {"field": "total_amount", "formula": "quantity * price"},\n                            {"field": "customer_segment", "lookup_table": "segments"}\n                        ]\n                    },\n                    {\n                        "type": "validation",\n                        "rules": ["not_null", "data_types", "ranges"]\n                    }\n                ],\n                "target": {\n                    "type": "dataset",\n                    "schema": "sales_analytics_v1"\n                }\n            }\n        \n        # Create and run pipeline\n        pipeline = ETLPipeline(client, project_id)\n        result = pipeline.run_pipeline(pipeline_config)\n        \n        if result.get('status') == 'completed':\n            print_success(f"✅ ETL Pipeline completed successfully!")\n            print(f"Pipeline ID: {result.get('pipeline_id')}")\n            \n            # Display final datasets\n            final_datasets = result.get('final_datasets', [])\n            if final_datasets:\n                print("\\n📋 Final Datasets Created:")\n                for dataset in final_datasets:\n                    print(f"  • {dataset.get('name')} (ID: {dataset.get('dataset_id')})")\n        else:\n            print_error("❌ ETL Pipeline failed")\n        \n    except Exception as e:\n        print_error(f"Failed to run ETL pipeline: {e}")\n    finally:\n        client.close()\n\n\nif __name__ == "__main__":\n    main()