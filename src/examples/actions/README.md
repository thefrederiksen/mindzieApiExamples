# mindzie-api Actions Examples

This directory contains examples demonstrating how to use the Actions and Action Execution controllers in the mindzie-api Python package.

## Overview

The Actions system in mindzieStudio allows you to execute automated processes and workflows. These examples show you how to:

- Execute actions and monitor their progress
- Retrieve action execution history and details
- Download execution packages and results
- Monitor action execution status in real-time

## Controllers Covered

### ActionController (`client.actions`)
- Execute actions within projects
- Test connectivity to action endpoints

### ActionExecutionController (`client.action_executions`)  
- Retrieve action execution history
- Get detailed execution information
- Download execution packages
- Monitor execution status

## Setup

1. **Install the package**:
   ```bash
   pip install mindzie-api
   ```

2. **Set up credentials**:
   Copy the `.env.template` file from the parent examples directory to `.env` and fill in your credentials:
   ```
   MINDZIE_TENANT_ID=your-tenant-id-here
   MINDZIE_API_KEY=your-api-key-here
   ```

3. **Install optional dependencies** (for .env file support):
   ```bash
   pip install python-dotenv
   ```

## Basic Examples

### Connectivity Testing
- `test_action_connectivity.py` - Test connectivity to action endpoints

### Action Management
- `execute_action.py` - Execute an action and get results
- `list_actions.py` - List available actions in a project

### Execution History
- `get_action_executions.py` - Get execution history for actions
- `get_last_execution.py` - Get the most recent execution
- `get_execution_details.py` - Get detailed execution information

### Package Management
- `download_execution_package.py` - Download execution result packages
- `monitor_action_execution.py` - Monitor execution progress

## Advanced Examples

### Workflow Examples
- `action_execution_workflow.py` - Complete execute → monitor → results workflow
- `compare_executions.py` - Compare multiple action executions
- `action_statistics.py` - Generate execution statistics and analytics

## Common Patterns

### Error Handling
All examples include comprehensive error handling for common scenarios:
- Authentication failures
- Network timeouts
- Action not found errors
- Execution failures

### Authentication
Examples support multiple authentication methods:
- Environment variables (MINDZIE_TENANT_ID, MINDZIE_API_KEY)
- .env file support (recommended for development)
- Direct credential passing

### Project Context
Most action operations require a project context. Examples show how to:
- List available projects to find project IDs
- Handle project-specific operations
- Validate project access

## Prerequisites

- Valid mindzie Studio account with API access
- At least one project with actions configured
- Appropriate permissions to execute actions and view execution history

## Getting Help

- Check the main mindzie-api documentation
- Review the API Swagger documentation at: https://dev.mindziestudio.com/swagger/index.html
- Examine the basic examples in the parent directory for authentication patterns

## Note on Security

- Never commit .env files or hardcode credentials
- Use environment variables in production
- Regularly rotate API keys
- Follow principle of least privilege for API access