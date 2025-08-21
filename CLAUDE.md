# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains Python examples demonstrating the mindzie-api package usage. The examples are organized into categories showing how to interact with the mindzie API for projects, actions, and action executions.

## Common Development Tasks

### Running Examples

All examples require mindzie API credentials set as environment variables:
```bash
set MINDZIE_TENANT_ID=your-tenant-id
set MINDZIE_API_KEY=your-api-key
```

To test basic connectivity:
```bash
python src/examples/hello_world.py  # No auth required
python src/examples/hello_world_authenticated.py  # Requires credentials
```

### Testing Authentication

Use the provided batch file for testing authentication:
```bash
src/examples/test_auth.bat
```

## Architecture and Structure

The codebase demonstrates client usage of the mindzie-api package with these key patterns:

1. **MindzieAPIClient** - Main client class instantiated with base_url, tenant_id, and api_key
2. **Controller Pattern** - Organized endpoints by functional area:
   - `client.ping` - Connectivity testing
   - `client.projects` - Project operations
   - `client.actions` - Action execution
   - `client.action_executions` - Execution history and monitoring

3. **Auto-Discovery Features** - Many examples include smart project discovery that automatically finds and uses available projects when no specific ID is provided

4. **Error Handling Pattern** - All examples include comprehensive error handling with user-friendly messages for:
   - Missing credentials
   - Network connectivity issues
   - Invalid project/action IDs
   - API errors

## API Endpoints

Base URL: `https://dev.mindziestudio.com`

Key endpoints demonstrated:
- `/api/test/test/ping/unauthorized-ping` - Unauthenticated connectivity test
- `/api/{tenantId}/project` - List projects
- `/api/{tenantId}/project/{projectId}` - Get project details
- `/api/{tenantId}/action/{projectId}/execute/{actionId}` - Execute action
- `/api/{tenantId}/actionexecution` - Get execution history

Authentication: Bearer token in Authorization header